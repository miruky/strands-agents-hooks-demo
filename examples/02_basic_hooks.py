"""例2: 基本的なHooksの使い方

agent.add_hook()でフックを登録し、ツール呼び出し前後にログを出力する例です。
型ヒントからイベントタイプが自動推論されます。
"""

from strands import Agent, tool
from strands.hooks import BeforeToolCallEvent, AfterToolCallEvent


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


@tool
def greet(name: str) -> str:
    """挨拶メッセージを生成します。

    Args:
        name: 挨拶する相手の名前
    """
    return f"こんにちは、{name}さん！"


def log_tool_call(event: BeforeToolCallEvent) -> None:
    """ツール呼び出し前のログ"""
    print(f"  [BEFORE] ツール呼び出し: {event.tool_use['name']}")
    print(f"  [BEFORE] 入力: {event.tool_use['input']}")


def log_tool_result(event: AfterToolCallEvent) -> None:
    """ツール呼び出し後のログ"""
    status = event.result.get("status", "unknown")
    print(f"  [AFTER]  ツール完了: {event.tool_use['name']} (status: {status})")


def main():
    agent = Agent(
        system_prompt="あなたは計算と挨拶ができるアシスタントです。",
        tools=[calculate, greet],
    )

    # 型ヒントからイベントタイプを自動推論
    agent.add_hook(log_tool_call)
    agent.add_hook(log_tool_result)

    print("=== Hooks デモ ===\n")
    agent("まず太郎さんに挨拶して、その後 123 * 456 を計算してください")


if __name__ == "__main__":
    main()
