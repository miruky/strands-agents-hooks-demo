"""例5: Steeringによるメールトーン制御

LLMSteeringHandlerを使って、メール送信前に
トーンのチェックを行うSteeringの例です。
"""

from strands import Agent, tool
from strands.vended_plugins.steering import LLMSteeringHandler


@tool
def send_email(recipient: str, subject: str, message: str) -> str:
    """メールを送信します。

    Args:
        recipient: 宛先メールアドレス
        subject: 件名
        message: 本文
    """
    print(f"\n  [EMAIL] To: {recipient}")
    print(f"  [EMAIL] Subject: {subject}")
    print(f"  [EMAIL] Body: {message[:100]}...")
    return f"メール送信完了: {recipient}"


def main():
    handler = LLMSteeringHandler(
        system_prompt="""
        メールの送信前に、以下のルールを検証してください：
        - メッセージのトーンがプロフェッショナルであること
        - 攻撃的・否定的な表現が含まれていないこと
        - フレンドリーな挨拶で始まっていること
        ルールに違反している場合は、改善のフィードバックを提供してください。
        """
    )

    agent = Agent(
        tools=[send_email],
        plugins=[handler],
    )

    print("=== Steering デモ: メールトーン制御 ===\n")
    print("怒りのメールを送ろうとしても、Steeringが介入して丁寧な表現に修正させます。\n")

    response = agent("会議をキャンセルし続けるクライアントに怒りのメールを送って")
    print(f"\n最終結果: {response}")


if __name__ == "__main__":
    main()
