"""例4: MetricsPlugin（状態を持つPlugin）

Agent Stateを使って、ツール呼び出し回数や実行時間を
リクエストをまたいで追跡するPluginの例です。
"""

import time

from strands import Agent, tool
from strands.plugins import Plugin, hook
from strands.hooks import BeforeToolCallEvent, AfterToolCallEvent


class MetricsPlugin(Plugin):
    """ツール実行のメトリクスをAgent Stateに記録するPlugin"""

    name = "metrics-plugin"

    def init_agent(self, agent) -> None:
        """エージェント初期化時にメトリクスの初期値を設定"""
        if "metrics_call_count" not in agent.state:
            agent.state.set("metrics_call_count", 0)
        if "metrics_total_time_ms" not in agent.state:
            agent.state.set("metrics_total_time_ms", 0.0)
        self._start_times: dict[str, float] = {}

    @hook
    def before_tool(self, event: BeforeToolCallEvent) -> None:
        tool_use_id = event.tool_use.get("toolUseId", "unknown")
        self._start_times[tool_use_id] = time.time()

    @hook
    def after_tool(self, event: AfterToolCallEvent) -> None:
        # カウントを加算
        current_count = event.agent.state.get("metrics_call_count", 0)
        event.agent.state.set("metrics_call_count", current_count + 1)

        # 実行時間を加算
        tool_use_id = event.tool_use.get("toolUseId", "unknown")
        start = self._start_times.pop(tool_use_id, None)
        if start:
            elapsed_ms = (time.time() - start) * 1000
            total = event.agent.state.get("metrics_total_time_ms", 0.0)
            event.agent.state.set("metrics_total_time_ms", total + elapsed_ms)
            print(f"  [METRICS] {event.tool_use['name']}: {elapsed_ms:.1f}ms")


@tool
def slow_task(task_name: str) -> str:
    """時間のかかるタスクをシミュレートします。

    Args:
        task_name: タスクの名前
    """
    time.sleep(0.5)
    return f"タスク '{task_name}' が完了しました"


@tool
def fast_task(task_name: str) -> str:
    """素早いタスクをシミュレートします。

    Args:
        task_name: タスクの名前
    """
    return f"タスク '{task_name}' が即座に完了しました"


def main():
    agent = Agent(
        system_prompt="あなたはタスク実行アシスタントです。",
        tools=[slow_task, fast_task],
        plugins=[MetricsPlugin()],
    )

    print("=== MetricsPlugin デモ ===\n")
    print("--- 1回目のリクエスト ---")
    agent("slow_taskで'データ処理'を実行し、fast_taskで'ログ記録'を実行してください")

    print(f"\nツール呼び出し回数: {agent.state.get('metrics_call_count')}")
    print(f"合計実行時間: {agent.state.get('metrics_total_time_ms'):.1f}ms")

    print("\n--- 2回目のリクエスト ---")
    agent("fast_taskで'通知送信'を実行してください")

    print(f"\n累計ツール呼び出し回数: {agent.state.get('metrics_call_count')}")
    print(f"累計実行時間: {agent.state.get('metrics_total_time_ms'):.1f}ms")


if __name__ == "__main__":
    main()
