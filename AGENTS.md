# Repository Guidelines

## Project Structure & Module Organization
- `src/app/config.py` で環境変数を一元管理し、`load_config()` が常に `AppConfig` を返します。
- `src/app/data/` には Repository Pattern 実装 (`sqlite_repo.py`, `oracle_repo.py`) があり、`create_repository()` で自動切り替え。
- `src/app/services/` がデータ整形ロジックを担い、Streamlit ページは描画に専念します。
- `src/app/charts/` に Plotly チャート関数をまとめ、`pages/` 以下の UI から呼び出します。
- `data/` 直下には SQLite モック DB (`test.db`) と `data/<product>/specs.csv` があり、実データはコミットしないでください。

## Build, Test, and Development Commands
- `uv pip sync pyproject.toml` で依存を同期（必ず Python 3.13 環境）。
- `uv run streamlit run main.py` でダッシュボードを起動。`.env` の `DB_BACKEND` で SQLite / Oracle を切り替え。
- Lint/format を入れる場合は `uv run ruff check` `uv run ruff format` を推奨。

## Coding Style & Naming Conventions
- Python は PEP8 + 4スペースインデント。モジュール名は `snake_case`、クラスは `PascalCase`。
- `src/app/services/*` は副作用を持たず、DataFrame を返す純粋関数を基本とする。
- Plotly 関連は `src/app/charts` にまとめ、UI ファイルへ生の Plotly コードを書かない。
- 新しい設定値は `AppConfig` に追加し、ページから直接 `os.getenv` を呼ばない。

## Testing Guidelines
- まだ自動テストは未導入。将来は `tests/services/test_yield_service.py` のようにサービス層を `pytest` で検証する想定。
- 仕様確認は SQLite モードで `streamlit run main.py` → ページ操作、Bulk/Parameter の切り替えを必ず確認。
- 実データで検証する場合は Oracle 接続情報を `.env` に設定し、差分が発生した SQL を記録すること。

## Commit & Pull Request Guidelines
- コミットメッセージは `type(scope): summary` 形式（例: `feat(data): add oracle repo`）。時刻のみのメッセージは禁止。
- PR には目的、主な変更点、テスト結果（例: `DB_BACKEND=sqlite streamlit run main.py`）を必ず記載。
- UI に影響する変更時はスクリーンショットを添付し、必要なら spec CSV 更新方法も説明。

## Security & Configuration Tips
- `.env` / `.streamlit/secrets.toml` を使い、認証情報をコードやログに残さない。
- Oracle 接続情報を扱う際は、利用テーブル・ビュー名を `oracle_repo.py` のコメントに追記しておくと引き継ぎが容易。
- 実データを SQLite に落とし込む際は匿名化（LotID, WaferID をダミー化）してからコミットしてください。
