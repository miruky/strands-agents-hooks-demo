"""例6: ToolUsageGuard（メインのハンズオン）

ツールの呼び出し回数を制限するHookProviderの実装デモです。
shellツールが暴走することなく、制限回数に達したらモデルに回答を促します。

実行方法:
    python -m examples.06_tool_usage_guard
"""

import sys
import os

# srcモジュールをインポートできるようにパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strands import Agent, tool
from src.tool_usage_guard import ToolUsageGuard


@tool
def check_server(target: str) -> str:
    """サーバーの状態を確認します。

    Args:
        target: 確認対象（例: "cpu", "memory", "disk", "network", "processes"）
    """
    # デモ用のモックレスポンス
    mock_responses = {
        "cpu": "CPU使用率: 45.2%, コア数: 8, ロードアベレージ: 1.23, 2.05, 1.87",
        "memory": "メモリ使用率: 72.1%, 合計: 16GB, 使用中: 11.5GB, 空き: 4.5GB",
        "disk": "ディスク使用率: 58.3%, 合計: 512GB, 使用中: 298GB, 空き: 214GB",
        "network": "ネットワーク: eth0 up, RX: 1.2GB, TX: 890MB, 接続数: 142",
        "processes": "プロセス数: 287, Running: 3, Sleeping: 282, Zombie: 2",
    }
    result = mock_responses.get(
        target.lower(),
        f"'{target}' の情報: 正常稼働中",
    )
    return result


@tool
def run_diagnostic(command: str) -> str:
    """診断コマンドを実行します。

    Args:
        command: 実行する診断コマンド
    """
    # デモ用のモックレスポンス
    return f"コマンド '{command}' の実行結果: 異常なし"


def main():
    # check_serverは3回まで、run_diagnosticは2回まで、その他は5回まで
    guard = ToolUsageGuard(
        max_counts={
            "check_server": 3,
            "run_diagnostic": 2,
        },
        default_max=5,
    )

    agent = Agent(
        system_prompt="あなたはシステム管理者です。サーバーの状態を調査して報告してください。",
        tools=[check_server, run_diagnostic],
        hooks=[guard],
    )

    print("=== ToolUsageGuard デモ ===")
    print("check_server: 最大3回, run_diagnostic: 最大2回\n")

    result = agent("サーバーの状態を徹底的に調査してください。CPU、メモリ、ディスク、ネットワーク、プロセスをすべて確認し、診断コマンドも実行してください。")

    print(f"\n=== 使用状況サマリー ===")
    summary = guard.get_summary()
    print(f"合計ツール呼び出し: {summary['total_calls']}回")
    for tool_name, count in summary["per_tool"].items():
        print(f"  {tool_name}: {count}回")


if __name__ == "__main__":
    main()
