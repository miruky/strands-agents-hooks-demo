"""例3: LoggingPlugin

Pluginの基本構造を示す例です。
@hookと@toolデコレータを使って、Hooksとツールを一つのクラスにまとめます。
"""

from strands import Agent, tool
from strands.plugins import Plugin, hook
from strands.hooks import BeforeToolCallEvent, AfterToolCallEvent


class LoggingPlugin(Plugin):
    """すべてのツール呼び出しをログ出力するPlugin"""

    name = "logging-plugin"

    @hook
    def log_before_tool(self, event: BeforeToolCallEvent) -> None:
        print(f"  [LOG] ツール呼び出し: {event.tool_use['name']}")
        print(f"  [LOG] 入力: {event.tool_use['input']}")

    @hook
    def log_after_tool(self, event: AfterToolCallEvent) -> None:
        print(f"  [LOG] ツール完了: {event.tool_use['name']}")

    @tool
    def debug_print(self, message: str) -> str:
        """デバッグメッセージを出力します。

        Args:
            message: 出力するメッセージ
        """
        print(f"  [DEBUG] {message}")
        return f"出力完了: {message}"


@tool
def calculate(expression: str) -> str:
    """数式を計算します。

    Args:
        expression: 計算する数式（例: "2 + 3"）
    """
    try:
        result = eval(expression)  # noqa: S307 - デモ用
        return f"計算結果: {expression} = {result}"
    except Exception as e:
        return f"計算エラー: {e}"


def main():
    # Pluginを渡すだけで、HooksもToolsも自動登録
    agent = Agent(
        system_prompt="あなたは計算とデバッグ出力ができるアシスタントです。",
        tools=[calculate],
        plugins=[LoggingPlugin()],
    )

    print("=== LoggingPlugin デモ ===\n")
    agent("まず 'Plugin動作確認' とデバッグ出力して、その後 99 * 99 を計算してください")


if __name__ == "__main__":
    main()
