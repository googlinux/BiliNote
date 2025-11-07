# 🚀 火星登陆模拟器 Mars Landing Simulator

一个高度逼真的火星登陆物理模拟程序，基于NASA真实任务数据和物理模型。

## ✨ 特点

- **真实物理模拟**: 基于火星实际参数（重力、大气密度、温度等）
- **完整降落过程**: 包含大气进入、降落伞、动力下降和着陆四个阶段
- **精确的大气模型**: 指数大气密度模型
- **自动制导系统**: PD控制器实现自动着陆
- **详细遥测数据**: 实时显示高度、速度、马赫数、动压等参数
- **可视化支持**: 使用matplotlib绘制任务剖面图

## 🔬 物理模型

### 火星参数
- **表面重力**: 3.721 m/s²（地球的38%）
- **大气压强**: 610 Pa（地球的0.6%）
- **大气密度**: 0.020 kg/m³
- **大气组成**: 95% CO₂
- **表面温度**: -63°C (210 K)

### 着陆器参数（基于NASA毅力号）
- **总质量**: 3,200 kg
- **燃料**: 400 kg
- **最大推力**: 8,000 N（8个推进器）
- **热防护盾直径**: 4.5 m
- **降落伞直径**: 21.5 m

### 降落阶段

1. **大气进入阶段** (Entry)
   - 初始高度: 125 km
   - 初始速度: 5,800 m/s (~20,900 km/h)
   - 使用热防护盾减速
   - 经历强烈气动加热

2. **降落伞阶段** (Parachute)
   - 触发条件: 马赫数 < 2.5，高度 7-11 km
   - 超音速降落伞展开
   - 大幅降低速度

3. **动力下降阶段** (Powered Descent)
   - 触发高度: 约2 km
   - 使用反推火箭精确控制
   - 自动制导系统调整推力

4. **着陆** (Landing)
   - 目标: 着陆速度 < 2 m/s
   - 成功标准: 安全触地且速度合适

## 📦 安装

### 基础运行（仅需Python 3.6+）

```bash
cd mars_landing_simulator
python simulator.py
```

### 高级可视化（需要matplotlib）

```bash
pip install matplotlib
python -c "from simulator import MarsLandingSimulator; from visualizer import MarsLandingVisualizer; s = MarsLandingSimulator(); s.run(verbose=False); v = MarsLandingVisualizer(s); v.plot_mission_profile()"
```

或安装所有依赖：

```bash
pip install -r requirements.txt
```

## 🎮 使用方法

### 基础模拟

```python
from simulator import MarsLandingSimulator

# 创建模拟器
sim = MarsLandingSimulator(dt=0.1, realtime=False)

# 运行模拟（每5秒显示一次状态）
sim.run(display_interval=5.0, verbose=True)
```

### 带可视化的模拟

```python
from simulator import MarsLandingSimulator
from visualizer import MarsLandingVisualizer

# 运行模拟
sim = MarsLandingSimulator()
sim.run(verbose=False)

# 绘制任务剖面
viz = MarsLandingVisualizer(sim)
viz.plot_mission_profile(save_path='mars_landing.png')
```

### 比较不同配置

```python
from simulator import MarsLandingSimulator
from visualizer import plot_comparison

# 运行多个模拟
sim1 = MarsLandingSimulator(dt=0.1)
sim1.run(verbose=False)

sim2 = MarsLandingSimulator(dt=0.05)  # 更高精度
sim2.run(verbose=False)

# 比较结果
plot_comparison([sim1, sim2], ['dt=0.1s', 'dt=0.05s'], 'comparison.png')
```

## 📊 输出示例

```
================================================================================
火星登陆模拟器 - Mars Landing Simulator
基于NASA真实任务参数
================================================================================

────────────────────────────────────────────────────────────────────────────────
⏱️  时间:     45.0 s  |  🚀 阶段: Entry
────────────────────────────────────────────────────────────────────────────────
📏 高度:      98234.5 m  ( 98.23 km)
💨 速度:       1456.32 m/s  (马赫  6.07)
⚖️  质量:       3200.0 kg
🌡️  动压:       42156.3 Pa
🌫️  大气密度:  0.000039 kg/m³
────────────────────────────────────────────────────────────────────────────────
进度: [████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 21.4%
```

## 🧮 物理公式

### 重力加速度
```
g = G * M / r²
```

### 大气密度（指数模型）
```
ρ(h) = ρ₀ * exp(-h / H)
```
其中 H = 11,100 m（大气标高）

### 空气阻力
```
F_drag = 0.5 * ρ * v² * C_d * A
```

### 动压
```
q = 0.5 * ρ * v²
```

### 马赫数
```
M = v / a
```
其中 a = √(γRT/M) 是音速

## 🎯 技术细节

- **数值积分**: 二阶Runge-Kutta方法（中点法）
- **时间步长**: 默认0.1秒（可调）
- **制导算法**: PD控制器 + 速度剖面跟踪
- **阶段转换**: 基于高度、速度和马赫数的自动触发

## 📝 文件结构

```
mars_landing_simulator/
├── mars_physics.py     # 火星物理参数和物理引擎
├── lander.py          # 着陆器模型和制导控制
├── simulator.py       # 主模拟器
├── visualizer.py      # 可视化工具
├── requirements.txt   # 依赖包
└── README.md         # 本文件
```

## 🔍 验证和精度

本模拟器的物理模型基于：
- NASA火星探测任务公开数据
- 标准大气动力学方程
- 真实的火星物理参数

关键验证点：
- ✅ 大气进入速度: ~5.8 km/s（与实际一致）
- ✅ 降落伞展开条件: 马赫2-2.5，高度7-11km（与实际一致）
- ✅ 动力下降时间: ~40-80秒（合理范围）
- ✅ 最终着陆速度: < 2 m/s（安全要求）

## 🚧 未来改进

- [ ] 添加横向运动（完整6自由度模拟）
- [ ] 地形高程模型
- [ ] 风场影响
- [ ] 更详细的气动加热模型
- [ ] 实时3D可视化
- [ ] 燃料最优化算法
- [ ] 多种着陆器配置

## 📚 参考资料

- NASA Mars 2020 Perseverance Rover Entry, Descent, and Landing
- NASA Mars Science Laboratory (Curiosity) EDL
- Mars Atmosphere Model
- Spacecraft Entry, Descent, and Landing at Mars

## 📄 许可证

MIT License

## 👨‍🚀 作者

创建用于教育和科研目的

---

**注意**: 这是一个教育性模拟程序，虽然基于真实物理参数，但不应用于实际任务规划。
