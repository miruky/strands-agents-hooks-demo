"""ToolUsageGuard: ツールの呼び出し回数を制限するHookProvider

Strands Agents SDKのHookProvider protocolを実装し、
エージェントが特定のツールを過剰に呼び出すことを防ぎます。

使い方:
    guard = ToolUsageGuard(max_counts={"shell": 3}, default_max=5)
    agent = Agent(tools=[shell], hooks=[guard])
"""

from threading import Lock

from strands.hooks import (
    AfterToolCallEvent,
    BeforeInvocationEvent,
    BeforeToolCallEvent,
    HookProvider,
    HookRegistry,
)


class ToolUsageGuard(HookProvider):
    """ツールの呼び出し回数を制限し、使用状況を記録するHook"""

    def __init__(self, max_counts: dict[str, int] | None = None, default_max: int = 10):
        """
        Args:
            max_counts: ツール名をキー、最大呼び出し回数を値とする辞書。
                        指定されていないツールにはdefault_maxが適用される。
            default_max: max_countsに含まれないツールのデフォルト上限。
        """
        self.max_counts = max_counts or {}
        self.default_max = default_max
        self.tool_counts: dict[str, int] = {}
        self.total_calls = 0
        self._lock = Lock()

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeInvocationEvent, self.reset_counts)
        registry.add_callback(BeforeToolCallEvent, self.check_limit)
        registry.add_callback(AfterToolCallEvent, self.log_result)

    def reset_counts(self, event: BeforeInvocationEvent) -> None:
        """リクエスト開始時にカウントをリセット"""
        with self._lock:
            self.tool_counts = {}
            self.total_calls = 0

    def check_limit(self, event: BeforeToolCallEvent) -> None:
        """ツール呼び出し前に上限チェック"""
        tool_name = event.tool_use["name"]
        with self._lock:
            count = self.tool_counts.get(tool_name, 0) + 1
            self.tool_counts[tool_name] = count

        max_count = self.max_counts.get(tool_name, self.default_max)
        if count > max_count:
            event.cancel_tool = (
                f"ツール '{tool_name}' は上限 {max_count} 回に達しました。"
                f"これ以上このツールを呼び出さないでください。"
                f"現在の情報で回答を生成してください。"
            )

    def log_result(self, event: AfterToolCallEvent) -> None:
        """ツール実行後にログ出力"""
        with self._lock:
            self.total_calls += 1
        status = event.result.get("status", "unknown")
        print(f"  [{self.total_calls}] {event.tool_use['name']}: {status}")

    def get_summary(self) -> dict:
        """使用状況のサマリーを返す"""
        return {
            "total_calls": self.total_calls,
            "per_tool": dict(self.tool_counts),
        }
