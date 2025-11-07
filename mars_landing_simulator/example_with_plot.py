"""
示例：运行模拟并生成可视化图表
Example: Run simulation and generate visualization
"""

from simulator import MarsLandingSimulator
from visualizer import MarsLandingVisualizer, MATPLOTLIB_AVAILABLE


def main():
    """主函数"""

    print("=" * 80)
    print("火星登陆模拟器 - 完整示例")
    print("Mars Landing Simulator - Full Example")
    print("=" * 80)
    print()

    # 创建模拟器
    print("📝 创建模拟器...")
    simulator = MarsLandingSimulator(dt=0.1, realtime=False)

    # 运行模拟
    print("🚀 开始模拟...\n")
    simulator.run(display_interval=10.0, verbose=True)

    # 如果matplotlib可用，生成可视化
    if MATPLOTLIB_AVAILABLE:
        print("\n📊 生成可视化图表...")
        try:
            visualizer = MarsLandingVisualizer(simulator)
            visualizer.plot_mission_profile(save_path='mars_landing_profile.png')
            print("✅ 图表已保存: mars_landing_profile.png")
        except Exception as e:
            print(f"❌ 生成图表时出错: {e}")
    else:
        print("\n⚠️  matplotlib未安装，跳过可视化")
        print("   安装命令: pip install matplotlib")

    print("\n✨ 完成!")


if __name__ == "__main__":
    main()
