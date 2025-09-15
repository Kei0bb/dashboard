# Project概要
半導体fabless企業のためのdashbord.streamlitを使ってシンプルながら整理された使いやすいものを作成。なるべくモジュール化してメンンテナンスしやすく。

## ページ構成
Home
Yield
WAT SPC

### ライブラリ
streamlit
plotly
pandas
sqlalchemy

### 実装機能
- 本番環境はoracledbですがtest用に別のdbを使用 (テスト用にSQLiteを使用)
- pageはnavibarで実装
- yield, spc pageにsidebarにselectboxを配置し品種を選択、品種リストはcsvに保存。src/modules内にモジュール化
- sidebarで選択した品種を引数にして、dbでデータをfetch。db情報はsecrets.tomlに。src/modules内にモジュール化
- 上記のデータを元にyield、spc等ををplotlyで実装していく、なるべくsrc/modeules内にモジュール化して呼び出し
- テストデータはサブグループデータとYieldデータを含むように更新
- WAT SPCページではIndividual Chart（ロット単位トレンドチャート）を実装
- USL/LSLをCSVから読み込み、SPCチャートに表示する機能を追加
- UI/UX改善として、`wide`レイアウトと`st.columns`による配置、サイドバータイトルの追加

### その他
- project管理はuv add, syncで

