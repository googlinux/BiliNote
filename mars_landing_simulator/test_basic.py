"""简单测试脚本"""

from mars_physics import MarsPhysics, PhysicsEngine
from lander import MarsLander, GuidanceController

# 创建着陆器
lander = MarsLander()

print("初始状态:")
print(f"  高度: {lander.altitude} m")
print(f"  速度: {lander.velocity} m/s")
print(f"  质量: {lander.mass} kg")
print()

# 模拟几个步骤
dt = 0.1
controller = GuidanceController()

for i in range(10):
    # 检查阶段转换
    lander.check_stage_transition()

    # 计算推力
    throttle = controller.calculate_throttle(lander)
    thrust = lander.get_thrust(throttle)

    # 计算加速度
    acceleration, forces = PhysicsEngine.calculate_net_force(
        mass=lander.mass,
        altitude=lander.altitude,
        velocity=lander.velocity,
        thrust=thrust,
        drag_coef=lander.drag_coefficient,
        cross_section=lander.cross_section
    )

    # 更新运动学
    new_altitude, new_velocity = PhysicsEngine.update_kinematics(
        altitude=lander.altitude,
        velocity=lander.velocity,
        acceleration=acceleration,
        dt=dt
    )

    # 更新状态
    lander.altitude = new_altitude
    lander.velocity = new_velocity
    lander.time_elapsed += dt

    print(f"步骤 {i+1}:")
    print(f"  时间: {lander.time_elapsed:.1f} s")
    print(f"  高度: {lander.altitude:.1f} m")
    print(f"  速度: {lander.velocity:.2f} m/s")
    print(f"  加速度: {acceleration:.2f} m/s²")
    print(f"  阶段: {lander.stage.value}")
    print()

    if lander.altitude <= 0:
        break

print("测试完成")
