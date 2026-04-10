# strands-agents-hooks-demo

Strands Agents SDK の内部制御メカニズム（Hooks・Plugin・Steering）を実際に動かして学ぶためのサンプルコード集です。

以下の Qiita 記事に対応しています。

- [Strands Agentsの「中身」を理解する：Hooks・Plugin・Steeringで制御可能なエージェントを作る](https://qiita.com/miruky/items/ed50bfcf5630f2a5fb73)

## 前提条件

- Python 3.10 以上
- AWS クレデンシャルの設定（Amazon Bedrock へのアクセス）
- Bedrock で Claude Sonnet 4 モデルへのアクセスが有効化されていること

## セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/miruky/strands-agents-hooks-demo.git
cd strands-agents-hooks-demo

# 仮想環境を作成・有効化
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

# 依存パッケージをインストール
pip install -r requirements.txt
```

## ディレクトリ構成

```
strands-agents-hooks-demo/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── tool_usage_guard.py      # 再利用可能なToolUsageGuardモジュール
├── examples/
│   ├── 01_cancellation.py       # キャンセルメカニズム
│   ├── 02_basic_hooks.py        # 基本的なHooks
│   ├── 03_logging_plugin.py     # LoggingPlugin
│   ├── 04_metrics_plugin.py     # MetricsPlugin（状態管理）
│   ├── 05_steering_email.py     # Steeringによるメールトーン制御
│   ├── 06_tool_usage_guard.py   # ToolUsageGuard（メインハンズオン）
│   └── 07_mutable_properties.py # 変更可能なイベントプロパティ
└── skills/
    └── pdf-processing/
        └── SKILL.md             # Skillsのフォーマット例
```

## 実行方法

リポジトリのルートディレクトリから各サンプルを実行します。

```bash
# 例1: キャンセルメカニズム
python examples/01_cancellation.py

# 例2: 基本的なHooks
python examples/02_basic_hooks.py

# 例3: LoggingPlugin
python examples/03_logging_plugin.py

# 例4: MetricsPlugin（状態を持つPlugin）
python examples/04_metrics_plugin.py

# 例5: Steeringによるメールトーン制御
python examples/05_steering_email.py

# 例6: ToolUsageGuard（メインのハンズオン）
python examples/06_tool_usage_guard.py

# 例7: 変更可能なイベントプロパティの活用
python examples/07_mutable_properties.py
```

## 各サンプルの概要

### 01_cancellation.py

`agent.cancel()` を使ったタイムアウトによるキャンセルの実装例です。別スレッドから安全にエージェントを停止できることを確認します。

### 02_basic_hooks.py

`agent.add_hook()` を使った最もシンプルなフック登録の例です。ツール呼び出しの前後にログを出力します。型ヒントからイベントタイプが自動推論されます。

### 03_logging_plugin.py

`Plugin` 基底クラスを継承し、`@hook` と `@tool` デコレータを使って、ログ出力フックとデバッグ用ツールを一つのクラスにまとめる例です。

### 04_metrics_plugin.py

Agent State を使って、ツール呼び出し回数と実行時間をリクエストをまたいで追跡する Plugin の例です。`init_agent()` での初期化パターンも示します。

### 05_steering_email.py

`LLMSteeringHandler` を使って、メール送信前にトーンをチェックするSteeringの例です。怒りのメールを送ろうとしても、プロフェッショナルな表現に修正されます。

### 06_tool_usage_guard.py

記事のメインハンズオンです。`HookProvider` を実装した `ToolUsageGuard` を使い、ツールの呼び出し回数に制限をかけます。`cancel_tool` プロパティでモデルにフィードバックを返す仕組みを体験できます。

### 07_mutable_properties.py

`cancel_tool`（ツール実行のブロック）と `result`（結果の改変）を組み合わせたセキュリティポリシー適用の例です。管理者データへのアクセスブロックと削除操作の監査ログ追記を実装します。

## ToolUsageGuard を自分のプロジェクトで使う

`src/tool_usage_guard.py` は単独のモジュールとしてコピーして使えます。

```python
from tool_usage_guard import ToolUsageGuard
from strands import Agent

guard = ToolUsageGuard(
    max_counts={"shell": 3, "http_request": 5},
    default_max=10,
)

agent = Agent(
    tools=[...],
    hooks=[guard],
)

result = agent("タスクを実行してください")
print(guard.get_summary())
```

## ライセンス

MIT
