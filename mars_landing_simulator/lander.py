"""
火星着陆器模型
基于NASA的真实火星探测器（好奇号、毅力号）
"""

from enum import Enum
from typing import Dict


class LandingStage(Enum):
    """着陆阶段枚举"""
    ENTRY = "Entry"  # 大气进入阶段
    PARACHUTE = "Parachute"  # 降落伞阶段
    POWERED_DESCENT = "Powered Descent"  # 动力下降
    LANDING = "Landing"  # 着陆
    CRASHED = "Crashed"  # 坠毁
    SUCCESS = "Success"  # 成功着陆


class MarsLander:
    """
    火星着陆器类
    模拟类似于NASA好奇号/毅力号的着陆器
    """

    def __init__(self):
        # 初始状态
        self.altitude = 125_000  # m - 初始高度（125km，大气进入高度）
        self.velocity = 5800  # m/s - 初始速度（向下，约5.8km/s）
        self.mass = 3_200  # kg - 总质量（类似毅力号）

        # 阶段状态
        self.stage = LandingStage.ENTRY
        self.time_elapsed = 0  # s

        # 燃料
        self.fuel = 400  # kg - 下降级燃料
        self.fuel_max = 400  # kg

        # 不同阶段的配置
        self.entry_shield_deployed = True
        self.parachute_deployed = False
        self.powered_descent_started = False

        # 物理参数
        self._update_physical_params()

    def _update_physical_params(self):
        """根据当前阶段更新物理参数"""

        if self.stage == LandingStage.ENTRY:
            # 进入阶段 - 热防护盾
            self.drag_coefficient = 1.5  # 高阻力系数
            self.cross_section = 4.5 * 4.5 * 3.14159  # m² - 热防护盾面积（直径4.5m）

        elif self.stage == LandingStage.PARACHUTE:
            # 降落伞阶段
            if self.parachute_deployed:
                self.drag_coefficient = 1.8
                self.cross_section = 21.5 * 21.5 * 3.14159 / 4  # 超音速降落伞（直径21.5m）
            else:
                # 降落伞展开前
                self.drag_coefficient = 0.8
                self.cross_section = 10  # m²

        elif self.stage == LandingStage.POWERED_DESCENT:
            # 动力下降阶段
            self.drag_coefficient = 0.5
            self.cross_section = 15  # m² - 较小截面
            # 推进器参数
            self.max_thrust = 15000  # N - 最大推力（增加以确保能够减速）
            self.fuel_consumption_rate = 2.0  # kg/s（全推力时）
            self.isp = 220  # s - 比冲（肼推进器）

        elif self.stage == LandingStage.LANDING or self.stage == LandingStage.SUCCESS:
            self.drag_coefficient = 0.5
            self.cross_section = 15

    def get_thrust(self, throttle: float = 0.0) -> float:
        """
        获取推力

        Args:
            throttle: 油门（0-1）

        Returns:
            推力 (N)
        """
        if self.stage != LandingStage.POWERED_DESCENT or self.fuel <= 0:
            return 0.0

        # 限制油门范围
        throttle = max(0.0, min(1.0, throttle))
        return self.max_thrust * throttle

    def consume_fuel(self, thrust: float, dt: float):
        """
        消耗燃料

        Args:
            thrust: 推力 (N)
            dt: 时间步长 (s)
        """
        if thrust > 0 and self.fuel > 0:
            # 燃料消耗 = 推力 / (Isp * g0)，其中g0是地球重力
            g0 = 9.81
            fuel_used = (thrust / (self.isp * g0)) * dt
            self.fuel = max(0, self.fuel - fuel_used)
            # 更新质量
            self.mass = max(self.mass - fuel_used, self.mass - self.fuel_max)

    def check_stage_transition(self) -> bool:
        """
        检查是否需要转换阶段

        Returns:
            是否发生了阶段转换
        """
        transition = False

        # 首先检查是否已经着陆或坠毁（所有阶段都要检查）
        if self.altitude <= 0 and self.stage not in [LandingStage.SUCCESS, LandingStage.CRASHED]:
            # 检查着陆速度（考虑着陆缓冲系统）
            if self.velocity < 12.0:  # 安全着陆速度阈值（约43 km/h，有缓冲系统可承受）
                self.stage = LandingStage.SUCCESS
            else:
                self.stage = LandingStage.CRASHED
            self.altitude = 0
            return True

        if self.stage == LandingStage.ENTRY:
            # 当速度降到超音速降落伞展开条件时
            # 马赫数 < 2.2，高度 7-11km
            from mars_physics import MarsPhysics
            mach = MarsPhysics.mach_number(self.velocity, self.altitude)

            if mach < 2.5 and self.altitude < 11_000 and self.altitude > 7_000:
                self.stage = LandingStage.PARACHUTE
                self.parachute_deployed = True
                self._update_physical_params()
                transition = True
            # 备用：如果高度太低还没展开降落伞，也要展开
            elif self.altitude < 7_000 and not self.parachute_deployed:
                self.stage = LandingStage.PARACHUTE
                self.parachute_deployed = True
                self._update_physical_params()
                transition = True

        elif self.stage == LandingStage.PARACHUTE:
            # 当高度降到约2km时，抛弃降落伞，开始动力下降
            if self.altitude < 2_100 and self.altitude > 100:
                self.stage = LandingStage.POWERED_DESCENT
                self.powered_descent_started = True
                self._update_physical_params()
                transition = True

        return transition

    def get_telemetry(self) -> Dict:
        """
        获取遥测数据

        Returns:
            包含所有状态信息的字典
        """
        from mars_physics import MarsPhysics

        mach = MarsPhysics.mach_number(self.velocity, self.altitude)
        dyn_pressure = MarsPhysics.dynamic_pressure(self.velocity, self.altitude)
        atm_density = MarsPhysics.atmospheric_density(self.altitude)

        return {
            'time': self.time_elapsed,
            'altitude': self.altitude,
            'velocity': self.velocity,
            'mass': self.mass,
            'fuel': self.fuel,
            'fuel_percent': (self.fuel / self.fuel_max) * 100,
            'stage': self.stage.value,
            'mach_number': mach,
            'dynamic_pressure': dyn_pressure,
            'atmospheric_density': atm_density,
            'g_force': 0.0,  # 将由模拟器计算
        }


class GuidanceController:
    """制导控制系统"""

    @staticmethod
    def calculate_throttle(lander: MarsLander, target_velocity: float = None) -> float:
        """
        计算油门设置（改进的PD控制器）

        Args:
            lander: 着陆器对象
            target_velocity: 目标速度 (m/s)

        Returns:
            油门设置 (0-1)
        """
        if lander.stage != LandingStage.POWERED_DESCENT:
            return 0.0

        if lander.fuel <= 0:
            return 0.0

        # 根据高度和速度计算目标速度曲线
        if target_velocity is None:
            # 自动制导：速度应该随高度线性减小
            if lander.altitude > 1000:
                # 高空：较快下降
                target_velocity = 30 + (lander.altitude / 2000) * 40
            elif lander.altitude > 300:
                # 中空：中等下降
                target_velocity = 15 + (lander.altitude / 1000) * 15
            elif lander.altitude > 50:
                # 低空：慢速下降
                target_velocity = 5 + (lander.altitude / 300) * 10
            else:
                # 超低空：非常慢
                target_velocity = max(1.5, lander.altitude / 50 * 5)

        # PD控制
        velocity_error = lander.velocity - target_velocity
        kp = 0.25  # 增加比例增益以提高响应速度

        # 基础推力（抵消重力）
        from mars_physics import MarsPhysics
        gravity = MarsPhysics.gravitational_acceleration(lander.altitude)
        base_throttle = (lander.mass * gravity) / lander.max_thrust

        # 修正推力
        correction = kp * velocity_error

        # 增加一个前馈项来预测需要的减速
        if velocity_error > 0 and lander.altitude > 0:
            # 计算需要的减速度
            time_to_target = lander.altitude / max(target_velocity, 1.0)
            needed_decel = velocity_error / time_to_target
            feedforward = (lander.mass * needed_decel) / lander.max_thrust
            correction += feedforward * 0.3  # 30%的前馈

        throttle = base_throttle + correction

        # 限制范围
        throttle = max(0.0, min(1.0, throttle))

        # 接近地面时的特殊处理
        if lander.altitude < 100:
            # 确保有足够的推力进行最后减速
            min_throttle = 0.6 + (100 - lander.altitude) / 100 * 0.3
            throttle = max(throttle, min_throttle)

        # 最后20米：全力减速到接近0
        if lander.altitude < 20 and lander.velocity > 2.0:
            throttle = 0.95  # 接近全推力

        # 紧急情况：速度过快且接近地面
        if lander.altitude < 200 and lander.velocity > target_velocity * 2:
            throttle = 1.0  # 全推力

        return throttle
