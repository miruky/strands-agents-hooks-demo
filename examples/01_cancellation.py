"""例1: キャンセルメカニズム

agent.cancel()を使ってタイムアウトによるキャンセルを実装する例です。
スレッドセーフかつ冪等なキャンセルの動作を確認できます。
"""

import threading
import time

from strands import Agent


def timeout_watchdog(agent: Agent, timeout: float) -> None:
    """タイムアウト後にエージェントをキャンセルする"""
    time.sleep(timeout)
    agent.cancel()


def main():
    agent = Agent()

    # 10秒後にキャンセル（デモ用に短めに設定）
    watchdog = threading.Thread(target=timeout_watchdog, args=(agent, 10.0))
    watchdog.start()

    print("エージェントを起動します（10秒後にタイムアウト）...")
    result = agent("100個の素数を見つけて、それぞれの特徴を詳しく説明してください")
    watchdog.join()

    if result.stop_reason == "cancelled":
        print("\nタイムアウトによりキャンセルされました")
    else:
        print(f"\n正常終了（stop_reason: {result.stop_reason}）")


if __name__ == "__main__":
    main()
