"""
火星物理环境模拟模块
包含火星的真实物理参数和大气模型
"""

import math
from typing import Tuple


class MarsPhysics:
    """火星物理参数类 - 基于真实数据"""

    # 火星基本参数
    GRAVITY = 3.721  # m/s² - 火星表面重力加速度
    RADIUS = 3_389_500  # m - 火星半径
    MASS = 6.4171e23  # kg - 火星质量

    # 大气参数
    SURFACE_PRESSURE = 610  # Pa - 火星表面平均气压
    SCALE_HEIGHT = 11_100  # m - 大气标高
    SURFACE_DENSITY = 0.020  # kg/m³ - 表面大气密度
    SURFACE_TEMP = 210  # K - 表面平均温度（-63°C）

    # 气体常数
    R = 8.314  # J/(mol·K) - 通用气体常数
    M = 0.04345  # kg/mol - 火星大气摩尔质量（95% CO2）

    # 音速（在表面温度下）
    SOUND_SPEED = math.sqrt(1.3 * R * SURFACE_TEMP / M)  # ~240 m/s

    @staticmethod
    def atmospheric_density(altitude: float) -> float:
        """
        计算给定高度的大气密度（指数大气模型）

        Args:
            altitude: 海拔高度 (m)

        Returns:
            大气密度 (kg/m³)
        """
        if altitude < 0:
            altitude = 0
        return MarsPhysics.SURFACE_DENSITY * math.exp(-altitude / MarsPhysics.SCALE_HEIGHT)

    @staticmethod
    def atmospheric_pressure(altitude: float) -> float:
        """
        计算给定高度的大气压强

        Args:
            altitude: 海拔高度 (m)

        Returns:
            大气压强 (Pa)
        """
        if altitude < 0:
            altitude = 0
        return MarsPhysics.SURFACE_PRESSURE * math.exp(-altitude / MarsPhysics.SCALE_HEIGHT)

    @staticmethod
    def drag_force(velocity: float, altitude: float, drag_coef: float,
                   cross_section: float) -> float:
        """
        计算空气阻力

        F_drag = 0.5 * ρ * v² * C_d * A

        Args:
            velocity: 速度 (m/s)
            altitude: 高度 (m)
            drag_coef: 阻力系数
            cross_section: 横截面积 (m²)

        Returns:
            阻力大小 (N)
        """
        density = MarsPhysics.atmospheric_density(altitude)
        return 0.5 * density * velocity**2 * drag_coef * cross_section

    @staticmethod
    def gravitational_acceleration(altitude: float) -> float:
        """
        计算给定高度的重力加速度

        g = G * M / r²

        Args:
            altitude: 海拔高度 (m)

        Returns:
            重力加速度 (m/s²)
        """
        r = MarsPhysics.RADIUS + altitude
        G = 6.67430e-11  # 引力常数
        return G * MarsPhysics.MASS / (r * r)

    @staticmethod
    def mach_number(velocity: float, altitude: float) -> float:
        """
        计算马赫数

        Args:
            velocity: 速度 (m/s)
            altitude: 高度 (m)

        Returns:
            马赫数
        """
        # 温度随高度变化（限制最小值避免溢出）
        exponent = -altitude / (2 * MarsPhysics.SCALE_HEIGHT)
        # 限制指数范围避免溢出（-100到10之间）
        exponent = max(-100, min(10, exponent))
        temp = MarsPhysics.SURFACE_TEMP * math.exp(exponent)
        # 确保温度至少为50K（避免除零和非物理值）
        temp = max(temp, 50)
        sound_speed = math.sqrt(1.3 * MarsPhysics.R * temp / MarsPhysics.M)
        return velocity / sound_speed

    @staticmethod
    def dynamic_pressure(velocity: float, altitude: float) -> float:
        """
        计算动压 q = 0.5 * ρ * v²

        Args:
            velocity: 速度 (m/s)
            altitude: 高度 (m)

        Returns:
            动压 (Pa)
        """
        density = MarsPhysics.atmospheric_density(altitude)
        return 0.5 * density * velocity**2


class PhysicsEngine:
    """物理引擎 - 处理力和运动"""

    @staticmethod
    def calculate_net_force(mass: float, altitude: float, velocity: float,
                          thrust: float, drag_coef: float,
                          cross_section: float) -> Tuple[float, dict]:
        """
        计算净加速度（向下为正，与速度坐标系一致）

        Args:
            mass: 质量 (kg)
            altitude: 高度 (m)
            velocity: 速度 (m/s，向下为正)
            thrust: 推力 (N，向上)
            drag_coef: 阻力系数
            cross_section: 横截面积 (m²)

        Returns:
            净加速度 (m/s²，向下为正) 和力的详细信息字典
        """
        # 重力加速度（向下，为正）
        gravity_accel = MarsPhysics.gravitational_acceleration(altitude)

        # 阻力加速度（与速度方向相反，向上）
        if velocity > 0:  # 向下运动
            drag_force = MarsPhysics.drag_force(abs(velocity), altitude, drag_coef, cross_section)
            drag_accel = -drag_force / mass  # 向上，为负
        else:  # 向上运动（不太可能发生）
            drag_force = MarsPhysics.drag_force(abs(velocity), altitude, drag_coef, cross_section)
            drag_accel = drag_force / mass  # 向下，为正

        # 推力加速度（向上，为负）
        thrust_accel = -thrust / mass

        # 总加速度（向下为正）
        net_accel = gravity_accel + drag_accel + thrust_accel

        forces = {
            'gravity': gravity_accel * mass,
            'drag': drag_accel * mass,
            'thrust': thrust_accel * mass,
            'net_accel': net_accel
        }

        return net_accel, forces

    @staticmethod
    def update_kinematics(altitude: float, velocity: float, acceleration: float,
                        dt: float) -> Tuple[float, float]:
        """
        更新运动学状态（向下为正）

        Args:
            altitude: 当前高度 (m)
            velocity: 当前速度 (m/s，向下为正)
            acceleration: 加速度 (m/s²，向下为正)
            dt: 时间步长 (s)

        Returns:
            新的高度和速度
        """
        # 速度更新：向下速度增加时，加速度为正
        new_velocity = velocity + acceleration * dt

        # 高度更新：向下运动时（velocity > 0），高度减小
        new_altitude = altitude - velocity * dt - 0.5 * acceleration * dt**2

        # 确保高度不为负
        if new_altitude < 0:
            new_altitude = 0

        return new_altitude, new_velocity
