# 📈 半導体製造ダッシュボード（再構築版）

Streamlit で動作する歩留まり / WAT 監視ダッシュボードを一から再設計しました。  
設定は `DB_BACKEND` によって **SQLiteモック** と **Oracle本番** を即座に切り替えられます。  
品種の定義は `config/products.yaml` で一元管理され、フォルダ構成と実DBの `PRODUCT_ID` を安全に紐づけられます。

---

## 🚀 クイックスタート

```bash
uv pip sync pyproject.toml   # 依存関係をインストール（pyyaml/oracledb含む）
cp .env.example .env         # 必要なら雛形をコピー
vim config/products.yaml     # 品種設定を編集
streamlit run main.py        # もしくは uv run streamlit run main.py

`config/products.yaml` が存在しない場合は `data/` 直下のサブフォルダから自動検出しますが、実運用では YAML を編集して品種ID・表示名・Oracle上の `PRODUCT_ID` を明示してください。
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
  specs.py         # config/specs 内の Spec YAML を読み込み
  products.py      # YAML から製品メタデータを読み込み
pages/             # Streamlit サブページ
data/              # SQLite DB と specs サンプル
config/products.yaml # 品種ごとの設定（name, label, data_subdir, source_name など）
```

---

## 🧾 品種設定（config/products.yaml）

```yaml
products:
  - name: productA          # UIでの識別子
    label: "Product A"      # サイドバー表示名
    source_name: "SCP117A"  # DBクエリに渡す PRODUCT_ID
    stages: ["CP", "FT"]    # 表示したい工程
    spec_file: productA.yaml  # config/specs/productA.yaml を参照
```

- `config/products.yaml` が存在すれば最優先で使用されます。  
- `source_name` を Oracle 実データの `PRODUCT_ID` に合わせれば、フォルダ名とDB名が異なっていても問題ありません。  
- 管理限界値は `config/specs/<file>.yaml` に分割して記述し、`spec_file` で参照します。大量パラメータでも Git 管理しやすい構成です。

YAMLを用意しない場合は `data/` 以下のフォルダ名がそのまま品種 ID として扱われます。

---

## 🧱 アーキテクチャ

- **Config**: `AppConfig` が単一の真実となり、Streamlit からも CLI からも同じ設定を参照。
- **Repository Pattern**: `create_repository()` でバックエンドを生成し、UI 側は実装を意識しない。
- **Service Layer**: 加工ロジックは `YieldService` / `WATService` に集約し、ページは描画のみ担当。
- **Charts**: Plotly 図は `src/app/charts/` に分離し、スタイル統一と再利用性を改善。

---

## 🧪 テストとデータ

- `data/test.db` には `yields` / `bin_data` / `wat_data` のモックが含まれ、`bin_data` は `BinNo_BinName` + `EffectiveNum` を持つ Oracle 風の集計済みテーブルです。SQLite ドライバのみで動作確認できます。
- 実データに近いモックを作りたい場合は `config/products.yaml` に品種を追加し、`spec_file` で `config/specs/*.yaml` を参照、必要なら `test.db` を更新してください。
- 既存CSVは互換性のため残せますが、今後は YAML で一元管理することを推奨します。
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

---

## 🔮 将来の拡張アイデア

- **自動テストとCI**：`pytest` + GitHub Actions を導入し、SQLite モックを用いたリグレッションテストを自動化。
- **品種ごとの権限管理**：`config/products.yaml` にロール情報を追加し、特定ユーザーのみ特定製品へアクセスできるよう Streamlit 認証と連携。
- **データ更新オーケストレーション**：Airflow / Dagster 等で Oracle → SQLite のモック更新をスケジュールし、より本番に近い検証環境を維持。
- **観測性の強化**：Application Insights や OpenTelemetry を追加してクエリ時間・キャッシュヒット率を計測、パフォーマンスのボトルネックを可視化。
- **ビジュアル強化**：Plotly テンプレートの共通化やダークテーマ対応、トレンドチャートへのアノテーション機能追加。
