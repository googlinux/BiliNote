"""
高级可视化模块 - 使用matplotlib绘制图表
需要安装: pip install matplotlib
"""

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from matplotlib.gridspec import GridSpec
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("警告: matplotlib未安装，无法使用高级可视化功能")


class MarsLandingVisualizer:
    """火星登陆可视化器"""

    def __init__(self, simulator):
        """
        初始化可视化器

        Args:
            simulator: MarsLandingSimulator实例
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("需要安装matplotlib: pip install matplotlib")

        self.simulator = simulator
        self.fig = None
        self.axes = []

    def plot_mission_profile(self, save_path: str = None):
        """
        绘制任务剖面图

        Args:
            save_path: 保存路径（可选）
        """
        history = self.simulator.history

        # 创建图形
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)

        # 1. 高度-时间曲线
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(history['time'], [alt/1000 for alt in history['altitude']], 'b-', linewidth=2)
        ax1.set_xlabel('时间 (s)', fontsize=12)
        ax1.set_ylabel('高度 (km)', fontsize=12)
        ax1.set_title('高度变化', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # 标注阶段转换
        for transition in self.simulator.stage_transitions:
            ax1.axvline(x=transition['time'], color='r', linestyle='--', alpha=0.5)
            ax1.text(transition['time'], transition['altitude']/1000,
                    transition['stage'], rotation=90, fontsize=8)

        # 2. 速度-时间曲线
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.plot(history['time'], history['velocity'], 'g-', linewidth=2)
        ax2.set_xlabel('时间 (s)', fontsize=12)
        ax2.set_ylabel('速度 (m/s)', fontsize=12)
        ax2.set_title('速度变化', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # 3. 高度-速度曲线（下降轨迹）
        ax3 = fig.add_subplot(gs[1, 0])
        ax3.plot([alt/1000 for alt in history['altitude']], history['velocity'], 'r-', linewidth=2)
        ax3.set_xlabel('高度 (km)', fontsize=12)
        ax3.set_ylabel('速度 (m/s)', fontsize=12)
        ax3.set_title('下降轨迹', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.invert_xaxis()  # 反转x轴，使高度从右到左递减

        # 4. 燃料消耗
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.plot(history['time'], history['fuel'], 'm-', linewidth=2)
        ax4.set_xlabel('时间 (s)', fontsize=12)
        ax4.set_ylabel('剩余燃料 (kg)', fontsize=12)
        ax4.set_title('燃料消耗', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)

        # 5. 推力-时间曲线
        ax5 = fig.add_subplot(gs[2, 0])
        ax5.plot(history['time'], [t/1000 for t in history['thrust']], 'c-', linewidth=2)
        ax5.set_xlabel('时间 (s)', fontsize=12)
        ax5.set_ylabel('推力 (kN)', fontsize=12)
        ax5.set_title('推力输出', fontsize=14, fontweight='bold')
        ax5.grid(True, alpha=0.3)

        # 6. 任务统计信息
        ax6 = fig.add_subplot(gs[2, 1])
        ax6.axis('off')

        # 创建统计文本
        stats_text = f"""
        任务统计 Mission Statistics
        ═══════════════════════════════════

        结果: {'✅ 成功着陆' if self.simulator.lander.stage.value == 'Success' else '❌ 坠毁'}

        总时间: {self.simulator.lander.time_elapsed:.1f} 秒
        最大G力: {self.simulator.max_g_force:.2f} g

        初始条件:
          • 高度: 125.0 km
          • 速度: 5800 m/s
          • 质量: 3200 kg

        最终状态:
          • 高度: {self.simulator.lander.altitude:.1f} m
          • 速度: {self.simulator.lander.velocity:.2f} m/s
          • 质量: {self.simulator.lander.mass:.1f} kg
          • 剩余燃料: {self.simulator.lander.fuel:.1f} kg

        阶段转换:
        """

        for transition in self.simulator.stage_transitions:
            stats_text += f"\n  {transition['time']:6.1f}s → {transition['stage']}"

        ax6.text(0.1, 0.5, stats_text, fontsize=10, verticalalignment='center',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # 设置整体标题
        fig.suptitle('🚀 火星登陆任务剖面 - Mars Landing Mission Profile 🔴',
                    fontsize=16, fontweight='bold')

        # 保存或显示
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        else:
            plt.show()

        return fig

    def create_animation(self, save_path: str = None, fps: int = 30):
        """
        创建动画（实时模拟可视化）

        Args:
            save_path: 保存路径（MP4格式）
            fps: 帧率
        """
        # TODO: 实现实时动画
        # 这需要在模拟运行时实时更新图表
        pass


def plot_comparison(simulators: list, labels: list, save_path: str = None):
    """
    比较多个模拟结果

    Args:
        simulators: MarsLandingSimulator实例列表
        labels: 标签列表
        save_path: 保存路径
    """
    if not MATPLOTLIB_AVAILABLE:
        print("matplotlib未安装，无法绘制比较图")
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    colors = ['b', 'g', 'r', 'c', 'm', 'y']

    for i, (sim, label) in enumerate(zip(simulators, labels)):
        color = colors[i % len(colors)]
        history = sim.history

        # 高度-时间
        axes[0, 0].plot(history['time'], [alt/1000 for alt in history['altitude']],
                       color=color, label=label, linewidth=2)

        # 速度-时间
        axes[0, 1].plot(history['time'], history['velocity'],
                       color=color, label=label, linewidth=2)

        # 高度-速度
        axes[1, 0].plot([alt/1000 for alt in history['altitude']], history['velocity'],
                       color=color, label=label, linewidth=2)

        # 燃料
        axes[1, 1].plot(history['time'], history['fuel'],
                       color=color, label=label, linewidth=2)

    # 设置标签和标题
    axes[0, 0].set_xlabel('时间 (s)')
    axes[0, 0].set_ylabel('高度 (km)')
    axes[0, 0].set_title('高度变化')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].set_xlabel('时间 (s)')
    axes[0, 1].set_ylabel('速度 (m/s)')
    axes[0, 1].set_title('速度变化')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].set_xlabel('高度 (km)')
    axes[1, 0].set_ylabel('速度 (m/s)')
    axes[1, 0].set_title('下降轨迹')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].invert_xaxis()

    axes[1, 1].set_xlabel('时间 (s)')
    axes[1, 1].set_ylabel('剩余燃料 (kg)')
    axes[1, 1].set_title('燃料消耗')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    fig.suptitle('火星登陆模拟比较', fontsize=16, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"比较图已保存到: {save_path}")
    else:
        plt.show()

    return fig


if __name__ == "__main__":
    print("这是可视化模块，请从主模拟器导入使用")
    print("示例:")
    print("  from simulator import MarsLandingSimulator")
    print("  from visualizer import MarsLandingVisualizer")
    print("  ")
    print("  sim = MarsLandingSimulator()")
    print("  sim.run(verbose=False)")
    print("  ")
    print("  viz = MarsLandingVisualizer(sim)")
    print("  viz.plot_mission_profile()")
