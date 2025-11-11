# 📈 半導体製造ダッシュボード（再構築版）

Streamlit で動作する歩留まり / WAT 監視ダッシュボードを一から再設計しました。  
設定は `DB_BACKEND` によって **SQLiteモック** と **Oracle本番** を即座に切り替えられます。

---

## 🚀 クイックスタート

```bash
uv pip sync pyproject.toml   # 依存関係をインストール
cp .env.example .env         # 必要なら雛形をコピー
streamlit run main.py        # もしくは uv run streamlit run main.py
```

### 本番（Oracle）での実行手順
1. **依存インストール**  
   ```bash
   uv pip sync pyproject.toml
   ```
   Oracle 接続には `python-oracledb` が必要です（pyproject に含まれています）。
2. **環境変数を設定**  
   `.env` を開き、少なくとも次を指定します。
   ```env
   DB_BACKEND=oracle
   DB_USERNAME=本番DBユーザー
   DB_PASSWORD=本番DBパスワード
   DB_DSN=db-host.example.com:1521/ORCL   # SID または (DESCRIPTION=...) 形式でも可
   ```
3. **接続確認**  
   `uv run python -c "import oracledb; print('connected')"` を実行し、ライブラリがロードできるか確認します。
4. **アプリ起動**  
   ```bash
   uv run streamlit run main.py
   ```
   ブラウザで http://localhost:8501 を開き、サイドバーで品種を選択→`Run Analysis` を押してデータ取得できるか確認してください。

### .env 例
```env
APP_ENV=development
DB_BACKEND=sqlite          # 本番時は oracle
DB_SQLITE_PATH=data/test.db

# Oracle モードで利用
# DB_USERNAME=your_user
# DB_PASSWORD=your_pass
# DB_DSN="(DESCRIPTION=...)"
```

---

## 🗂 ディレクトリ構成

```
src/app/
  config.py        # 環境変数の集約
  data/            # SQLite / Oracle リポジトリ実装
  services/        # UI と DB の橋渡し
  charts/          # Plotly チャート
  specs.py         # specs.csv ローダー
pages/             # Streamlit サブページ
data/              # SQLite DB と specs サンプル
```

---

## 🧱 アーキテクチャ

- **Config**: `AppConfig` が単一の真実となり、Streamlit からも CLI からも同じ設定を参照。
- **Repository Pattern**: `create_repository()` でバックエンドを生成し、UI 側は実装を意識しない。
- **Service Layer**: 加工ロジックは `YieldService` / `WATService` に集約し、ページは描画のみ担当。
- **Charts**: Plotly 図は `src/app/charts/` に分離し、スタイル統一と再利用性を改善。

---

## 🧪 テストとデータ

- `data/test.db` にモックデータが含まれます。SQLite ドライバのみで動作確認可能。
- 追加で CSV を増やしたい場合は `data/<product>/specs.csv` を作成し、`parameter,USL,LSL` 形式で追記してください。
- 将来的に `tests/` ディレクトリを追加し、サービス層を `pytest` で検証することを想定しています。

---

## 🙋‍♀️ よくある操作

| 用途 | コマンド |
| ---- | -------- |
| 依存追加 | `uv add <package>` |
| Lint/format (任意) | `uv run ruff check` / `uv run ruff format` |
| Streamlit 開発サーバ | `uv run streamlit run main.py` |

---

## 📝 コントリビューション

1. issue で改善案を相談  
2. フィーチャーブランチで変更を加える  
3. `README.md` と `AGENTS.md` の関連部分を更新  
4. 最低限の動作確認（SQLite モードでの起動）を記載

再構築版について質問や改善提案があれば、issue / PR でいつでもどうぞ。Happy hacking! 🛠️
