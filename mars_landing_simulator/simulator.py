"""
火星登陆模拟器主程序
整合物理引擎、着陆器模型和可视化
"""

import time
import sys
from typing import Optional
from mars_physics import MarsPhysics, PhysicsEngine
from lander import MarsLander, LandingStage, GuidanceController


class MarsLandingSimulator:
    """火星登陆模拟器"""

    def __init__(self, dt: float = 0.1, realtime: bool = False):
        """
        初始化模拟器

        Args:
            dt: 时间步长 (s)
            realtime: 是否实时运行（否则尽快运行）
        """
        self.dt = dt
        self.realtime = realtime
        self.lander = MarsLander()
        self.controller = GuidanceController()

        # 统计信息
        self.max_g_force = 0.0
        self.max_heating = 0.0
        self.stage_transitions = []

        # 历史记录（用于绘图）
        self.history = {
            'time': [],
            'altitude': [],
            'velocity': [],
            'stage': [],
            'fuel': [],
            'thrust': [],
        }

    def step(self):
        """执行一个模拟步骤"""

        # 检查阶段转换
        if self.lander.check_stage_transition():
            self.stage_transitions.append({
                'time': self.lander.time_elapsed,
                'stage': self.lander.stage.value,
                'altitude': self.lander.altitude,
                'velocity': self.lander.velocity,
            })

        # 如果已经着陆或坠毁，不再更新
        if self.lander.stage in [LandingStage.SUCCESS, LandingStage.CRASHED]:
            return False

        # 计算推力（制导系统）
        throttle = self.controller.calculate_throttle(self.lander)
        thrust = self.lander.get_thrust(throttle)

        # 计算净加速度
        acceleration, forces = PhysicsEngine.calculate_net_force(
            mass=self.lander.mass,
            altitude=self.lander.altitude,
            velocity=self.lander.velocity,
            thrust=thrust,
            drag_coef=self.lander.drag_coefficient,
            cross_section=self.lander.cross_section
        )

        # 计算G力（相对于地球重力）
        g_force = abs(acceleration) / 9.81
        self.max_g_force = max(self.max_g_force, g_force)

        # 计算气动加热（简化模型）
        heating = MarsPhysics.dynamic_pressure(self.lander.velocity, self.lander.altitude) * \
                  (self.lander.velocity / 1000) ** 2
        self.max_heating = max(self.max_heating, heating)

        # 更新运动学
        new_altitude, new_velocity = PhysicsEngine.update_kinematics(
            altitude=self.lander.altitude,
            velocity=self.lander.velocity,
            acceleration=acceleration,
            dt=self.dt
        )

        # 更新着陆器状态
        self.lander.altitude = new_altitude
        self.lander.velocity = new_velocity
        self.lander.time_elapsed += self.dt

        # 消耗燃料
        self.lander.consume_fuel(thrust, self.dt)

        # 记录历史
        self.history['time'].append(self.lander.time_elapsed)
        self.history['altitude'].append(self.lander.altitude)
        self.history['velocity'].append(self.lander.velocity)
        self.history['stage'].append(self.lander.stage.value)
        self.history['fuel'].append(self.lander.fuel)
        self.history['thrust'].append(thrust)

        return True

    def run(self, display_interval: float = 1.0, verbose: bool = True, max_time: float = 600.0):
        """
        运行模拟

        Args:
            display_interval: 显示更新间隔 (s)
            verbose: 是否显示详细信息
            max_time: 最大模拟时间 (s)
        """
        print("=" * 80)
        print("火星登陆模拟器 - Mars Landing Simulator")
        print("基于NASA真实任务参数")
        print("=" * 80)
        print()

        last_display_time = 0
        simulation_running = True

        try:
            while simulation_running:
                # 执行模拟步骤
                simulation_running = self.step()

                # 实时模式延迟
                if self.realtime:
                    time.sleep(self.dt)

                # 显示更新
                if verbose and (self.lander.time_elapsed - last_display_time >= display_interval):
                    self.display_status()
                    last_display_time = self.lander.time_elapsed

                # 检查是否完成
                if self.lander.stage in [LandingStage.SUCCESS, LandingStage.CRASHED]:
                    break

                # 检查超时
                if self.lander.time_elapsed > max_time:
                    print(f"\n⚠️  模拟超时 ({max_time}秒)")
                    break

        except KeyboardInterrupt:
            print("\n\n模拟被用户中断")

        # 显示最终结果
        self.display_final_report()

    def display_status(self):
        """显示当前状态"""
        telemetry = self.lander.get_telemetry()

        print(f"\n{'─' * 80}")
        print(f"⏱️  时间: {telemetry['time']:8.1f} s  |  🚀 阶段: {telemetry['stage']}")
        print(f"{'─' * 80}")
        print(f"📏 高度:     {telemetry['altitude']:10.1f} m  ({telemetry['altitude']/1000:6.2f} km)")
        print(f"💨 速度:     {telemetry['velocity']:10.2f} m/s  (马赫 {telemetry['mach_number']:5.2f})")
        print(f"⚖️  质量:     {telemetry['mass']:10.1f} kg")

        if self.lander.stage == LandingStage.POWERED_DESCENT:
            print(f"⛽ 燃料:     {telemetry['fuel']:10.1f} kg  ({telemetry['fuel_percent']:5.1f}%)")

        print(f"🌡️  动压:     {telemetry['dynamic_pressure']:10.1f} Pa")
        print(f"🌫️  大气密度: {telemetry['atmospheric_density']:10.6f} kg/m³")
        print(f"{'─' * 80}")

        # 进度条
        if self.lander.altitude > 0:
            progress = max(0, min(100, 100 * (1 - self.lander.altitude / 125000)))
            bar_length = 50
            filled = int(bar_length * progress / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"进度: [{bar}] {progress:.1f}%")

    def display_final_report(self):
        """显示最终报告"""
        print("\n\n")
        print("=" * 80)
        print("最终报告 - Final Report")
        print("=" * 80)

        # 着陆结果
        if self.lander.stage == LandingStage.SUCCESS:
            print("✅ 着陆成功！ LANDING SUCCESSFUL!")
            print(f"   最终速度: {self.lander.velocity:.2f} m/s (安全范围)")
        else:
            print("❌ 着陆失败 - 坠毁")
            print(f"   撞击速度: {self.lander.velocity:.2f} m/s (过快)")

        print()
        print("任务统计:")
        print(f"  • 总时间:       {self.lander.time_elapsed:.1f} 秒")
        print(f"  • 最大G力:      {self.max_g_force:.2f} g")
        print(f"  • 剩余燃料:     {self.lander.fuel:.1f} kg ({self.lander.fuel/self.lander.fuel_max*100:.1f}%)")

        print()
        print("阶段转换:")
        for transition in self.stage_transitions:
            print(f"  • {transition['time']:6.1f}s - 进入 '{transition['stage']}' 阶段")
            print(f"    高度: {transition['altitude']/1000:.2f} km, 速度: {transition['velocity']:.1f} m/s")

        print()
        print("关键指标:")
        print(f"  • 进入速度:     5800 m/s (约 20,900 km/h)")
        print(f"  • 最大气动加热:  {self.max_heating:.0f} (相对单位)")
        print(f"  • 最终质量:     {self.lander.mass:.1f} kg")

        print("=" * 80)


def display_ascii_art():
    """显示ASCII艺术图"""
    art = """
    🚀 火星登陆模拟器 🔴

         .-.
        ( ( )~
         `-'
          |
         /|\\
        / | \\
       🛸~~~🛸

    真实物理模拟
    Real Physics Simulation
    """
    print(art)


def main():
    """主函数"""
    display_ascii_art()

    print("初始化模拟器...")
    print()

    # 创建模拟器（时间步长0.1秒）
    simulator = MarsLandingSimulator(dt=0.1, realtime=False)

    # 运行模拟（每1秒显示一次状态）
    simulator.run(display_interval=5.0, verbose=True)

    print("\n模拟完成！")


if __name__ == "__main__":
    main()
