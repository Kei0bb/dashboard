# SONAR スキーマ データ辞書

## 🧩 テーブル: `SEMI_CP_HEADER`

  No   カラム名            データ型            NULL可     説明
  ---- ------------------- ------------------- ---------- ------------------------
  1    SUBSTRATE_ID        VARCHAR2(32 BYTE)   NOT NULL   基板ID（主要キー）
  2    LOT_ID              VARCHAR2(24 BYTE)   可         ロットID
  3    WAFER_ID            NUMBER(3,0)         NOT NULL   ウェハ番号
  4    FRAME_ID            VARCHAR2(32 BYTE)   可         フレームID
  5    PRODUCT_ID          VARCHAR2(32 BYTE)   NOT NULL   製品ID
  6    SUPPLIER_NAME       VARCHAR2(32 BYTE)   可         サプライヤ名
  7    MAX_ROW             NUMBER(10,0)        可         最大行数（チップ配列）
  8    MAX_COL             NUMBER(10,0)        可         最大列数（チップ配列）
  9    CREATE_DATE         DATE                可         登録日（作成日）
  10   MODIFY_DATE         DATE                可         更新日
  11   PROCESS             VARCHAR2(16 BYTE)   NOT NULL   工程名
  12   WAFER_X             NUMBER(10,0)        可         ウェハ座標X
  13   WAFER_Y             NUMBER(10,0)        可         ウェハ座標Y
  14   TESTER_NAME         VARCHAR2(32 BYTE)   可         テスタ名
  15   MAIN_PROGRAM_NAME   VARCHAR2(64 BYTE)   可         メインプログラム名
  16   REV01               VARCHAR2(32 BYTE)   可         リビジョン1
  17   REV02               VARCHAR2(32 BYTE)   可         リビジョン2
  18   FAB_PRODUCT_ID      VARCHAR2(32 BYTE)   可         FAB側製品ID
  19   FACILITY            VARCHAR2(32 BYTE)   可         製造拠点名
  20   PASS_CHIP           NUMBER              可         合格チップ数
  21   PERFECT_PASS_CHIP   NUMBER              可         完全合格チップ数
  22   PASS_CHIP_RATE      NUMBER              可         合格率
  23   REGIST_DATE         DATE                可         登録日時
  24   DEL_FLAG            NUMBER(1,0)         可         論理削除フラグ
  25   REWORK_NEW          NUMBER(2,0)         NOT NULL   リワーク種別コード
  26   REWORK_CNT          NUMBER(2,0)         可         リワーク回数
  27   EFFECTIVE_NUM       NUMBER              可         有効数

**主キー（PK）:**\
`SUBSTRATE_ID`, `WAFER_ID`, `PRODUCT_ID`, `PROCESS`, `REWORK_NEW`

------------------------------------------------------------------------

## 🧮 テーブル: `SEMI_CP_BIN_SUM`

  ---------------------------------------------------------------------------
  No     カラム名        データ型        NULL可      説明
  ------ --------------- --------------- ----------- ------------------------
  1      SUBSTRATE_ID    VARCHAR2(32     NOT NULL    基板ID（外部キー相当）
                         BYTE)                       

  2      LOT_ID          VARCHAR2(24     可          ロットID
                         BYTE)                       

  3      WAFER_ID        NUMBER(3,0)     NOT NULL    ウェハ番号

  4      PRODUCT_ID      VARCHAR2(32     NOT NULL    製品ID
                         BYTE)                       

  5      PROCESS         VARCHAR2(16     NOT NULL    工程名
                         BYTE)                       

  6      BIN_CODE        NUMBER(6,0)     NOT NULL    BIN分類コード

  7      BIN_QUALITY     VARCHAR2(32     可          品質ランク
                         BYTE)                       

  8      BIN_NAME        VARCHAR2(32     可          BIN名称
                         BYTE)                       

  9      BIN_COUNT       NUMBER          可          BINに属するチップ数

  10     CREATE_DATE     DATE            可          作成日時

  11     REGIST_DATE     DATE            可          登録日時

  12     DEL_FLAG        NUMBER(1,0)     可          論理削除フラグ

  13     REWORK_NEW      NUMBER(2,0)     NOT NULL    リワーク種別コード

  14     REWORK_CNT      NUMBER(2,0)     可          リワーク回数
  ---------------------------------------------------------------------------

**主キー（PK）:**\
`SUBSTRATE_ID`, `WAFER_ID`, `PRODUCT_ID`, `PROCESS`, `BIN_CODE`,
`REWORK_NEW`

**外部キー（FK）候補:**\
`(SUBSTRATE_ID, WAFER_ID, PRODUCT_ID, PROCESS, REWORK_NEW)` →
`SEMI_CP_HEADER`

------------------------------------------------------------------------

## 🔗 リレーション概要

  ----------------------------------------------------------------------
  親テーブル            子テーブル            リレーションキー
  --------------------- --------------------- --------------------------
  SEMI_CP_HEADER        SEMI_CP_BIN_SUM       SUBSTRATE_ID, WAFER_ID,
                                              PRODUCT_ID, PROCESS,
                                              REWORK_NEW

  ----------------------------------------------------------------------

**関係:**\
1つのヘッダ情報（基板・製品・工程・リワーク単位）に対して、複数のBINサマリ（分類結果）が紐づく「1対多」構造。

------------------------------------------------------------------------

## 🧩 テーブル: `SEMI_FT_HEADER`

  ---------------------------------------------------------------------------------------------
  No      カラム名            データ型            NULL可         説明
  ------- ------------------- ------------------- -------------- ------------------------------
  1       SUBSTRATE_ID        VARCHAR2(32 BYTE)   可             基板ID

  2       ASSY_LOT_ID         VARCHAR2(32 BYTE)   NOT NULL       アッシーロットID（主要キー）

  3       WAFER_ID            NUMBER(3,0)         可             ウェハ番号

  4       FRAME_ID            VARCHAR2(32 BYTE)   可             フレームID

  5       PRODUCT_ID          VARCHAR2(32 BYTE)   NOT NULL       製品ID

  6       SUPPLIER_NAME       VARCHAR2(32 BYTE)   可             サプライヤ名

  7       MAX_ROW             NUMBER(10,0)        可             最大行数

  8       MAX_COL             NUMBER(10,0)        可             最大列数

  9       CREATE_DATE         DATE                可             作成日

  10      MODIFIED_DATE       DATE                可             更新日

  11      PROCESS             VARCHAR2(16 BYTE)   NOT NULL       工程名

  12      WAFER_X             NUMBER(10,0)        可             ウェハ座標X

  13      WAFER_Y             NUMBER(10,0)        可             ウェハ座標Y

  14      TESTER_NAME         VARCHAR2(32 BYTE)   可             テスタ名

  15      MAIN_PROGRAM_NAME   VARCHAR2(64 BYTE)   可             メインプログラム名

  16      REV01               VARCHAR2(64 BYTE)   可             リビジョン1

  17      REV02               VARCHAR2(32 BYTE)   可             リビジョン2

  18      FAB_PRODUCT_ID      VARCHAR2(32 BYTE)   可             FAB側製品ID

  19      FACILITY            VARCHAR2(32 BYTE)   可             製造拠点

  20      EFFECTIVE_NUM       NUMBER              可             有効チップ数

  21      PERFECT_PASS_CHIP   NUMBER              可             完全合格チップ数

  22      PASS_CHIP           NUMBER              可             合格チップ数

  23      REGIST_DATE         DATE                可             登録日時

  24      DEL_FLAG            NUMBER(1,0)         可             論理削除フラグ

  25      REWORK_NEW          NUMBER(2,0)         NOT NULL       リワーク種別

  26      REWORK_CNT          NUMBER(2,0)         可             リワーク回数
  ---------------------------------------------------------------------------------------------

**主キー（PK）:**\
`ASSY_LOT_ID`, `PRODUCT_ID`, `PROCESS`, `REWORK_NEW`

------------------------------------------------------------------------

## 🧮 テーブル: `SEMI_FT_BIN_SUM`

  No   カラム名       データ型            NULL可     説明
  ---- -------------- ------------------- ---------- --------------------
  1    SUBSTRATE_ID   VARCHAR2(32 BYTE)   可         基板ID
  2    ASSY_LOT_ID    VARCHAR2(32 BYTE)   NOT NULL   アッシーロットID
  3    WAFER_ID       NUMBER(3,0)         NOT NULL   ウェハ番号
  4    PRODUCT_ID     VARCHAR2(32 BYTE)   NOT NULL   製品ID
  5    PROCESS        VARCHAR2(16 BYTE)   NOT NULL   工程名
  6    BIN_CODE       NUMBER(6,0)         NOT NULL   BIN分類コード
  7    BIN_QUALITY    VARCHAR2(32 BYTE)   可         品質ランク
  8    BIN_NAME       VARCHAR2(64 BYTE)   可         BIN名称
  9    BIN_COUNT      NUMBER              可         チップ数
  10   CREATE_DATE    DATE                可         作成日時
  11   REGIST_DATE    DATE                可         登録日時
  12   DEL_FLAG       NUMBER(1,0)         可         論理削除フラグ
  13   REWORK_NEW     NUMBER(2,0)         NOT NULL   リワーク種別コード
  14   REWORK_CNT     NUMBER(2,0)         可         リワーク回数

**主キー（PK）:**\
`ASSY_LOT_ID`, `PRODUCT_ID`, `PROCESS`, `BIN_CODE`, `REWORK_NEW`

**外部キー（FK）候補:**\
`(ASSY_LOT_ID, PRODUCT_ID, PROCESS, REWORK_NEW)` → `SEMI_FT_HEADER`

------------------------------------------------------------------------

## 🔗 リレーション概要（FT工程）

  -----------------------------------------------------------------------
  親テーブル            子テーブル            リレーションキー
  --------------------- --------------------- ---------------------------
  SEMI_FT_HEADER        SEMI_FT_BIN_SUM       ASSY_LOT_ID, PRODUCT_ID,
                                              PROCESS, REWORK_NEW

  -----------------------------------------------------------------------

**関係:**\
1つのFT工程ロットに対して、複数のBIN集計が紐づく「1対多」構造。
