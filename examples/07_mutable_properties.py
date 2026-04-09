"""例7: 変更可能なイベントプロパティの活用

cancel_tool, selected_tool, result, retry など
Hooksの変更可能プロパティを組み合わせた実践的な例です。
"""

from strands import Agent, tool
from strands.hooks import (
    HookProvider,
    HookRegistry,
    BeforeToolCallEvent,
    AfterToolCallEvent,
)


@tool
def get_user_data(user_id: str) -> str:
    """ユーザーデータを取得します。

    Args:
        user_id: ユーザーID
    """
    # デモ用のモックデータ
    users = {
        "user001": "名前: 田中太郎, メール: tanaka@example.com, 部署: 開発部",
        "user002": "名前: 鈴木花子, メール: suzuki@example.com, 部署: 営業部",
        "admin": "名前: 管理者, メール: admin@example.com, 権限: root",
    }
    return users.get(user_id, f"ユーザー '{user_id}' は見つかりません")


@tool
def delete_record(record_id: str) -> str:
    """レコードを削除します。

    Args:
        record_id: 削除するレコードのID
    """
    return f"レコード '{record_id}' を削除しました"


class SecurityGuard(HookProvider):
    """セキュリティポリシーを適用するHookProvider

    - adminユーザーのデータ取得をブロック（cancel_tool）
    - 削除操作の結果にログ情報を追記（result改変）
    """

    def register_hooks(self, registry: HookRegistry) -> None:
        registry.add_callback(BeforeToolCallEvent, self.enforce_policy)
        registry.add_callback(AfterToolCallEvent, self.audit_log)

    def enforce_policy(self, event: BeforeToolCallEvent) -> None:
        tool_name = event.tool_use["name"]
        tool_input = event.tool_use["input"]

        # adminユーザーのデータ取得をブロック
        if tool_name == "get_user_data" and tool_input.get("user_id") == "admin":
            event.cancel_tool = (
                "セキュリティポリシー: 管理者アカウントのデータは直接取得できません。"
                "別のユーザーIDを指定してください。"
            )
            print("  [SECURITY] adminデータへのアクセスをブロックしました")

        # 削除操作に対する警告ログ
        if tool_name == "delete_record":
            print(f"  [SECURITY] 削除操作を検出: record_id={tool_input.get('record_id')}")

    def audit_log(self, event: AfterToolCallEvent) -> None:
        tool_name = event.tool_use["name"]

        # 削除操作の結果に監査ログを追記
        if tool_name == "delete_record":
            original = event.result.get("content", [{}])[0].get("text", "")
            event.result["content"][0]["text"] = (
                f"{original} [監査ログ: 操作記録済み, タイムスタンプ付き]"
            )
            print("  [AUDIT] 削除操作の監査ログを記録しました")


def main():
    agent = Agent(
        system_prompt="あなたはデータ管理アシスタントです。",
        tools=[get_user_data, delete_record],
        hooks=[SecurityGuard()],
    )

    print("=== セキュリティHook デモ ===\n")
    agent(
        "以下を順番に実行してください: "
        "1. user001のデータを取得 "
        "2. adminのデータを取得 "
        "3. user002のデータを取得 "
        "4. レコードrec-123を削除"
    )


if __name__ == "__main__":
    main()
