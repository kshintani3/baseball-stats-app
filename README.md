# NPB Stats — 自分専用プロ野球データ分析アプリ

NPB 1軍の打者・投手・チーム成績を手元で自由に分析するためのWebアプリです。
ランキング、選手詳細、複数選手の比較、シーズン推移グラフを、好きな指標・条件で手軽に閲覧できます。

**データソース:** [Baseball Reference](https://www.baseball-reference.com) を優先し、取得できない場合は [NPB公式](https://npb.jp/) にフォールバック

---

## 全体の流れ

```
[STEP 1] 環境を準備する
    ↓
[STEP 2] スクレイパーで実データを取得する
    ↓
[STEP 3] アプリを起動して http://localhost:3000 にアクセスする
```

---

## STEP 1 — 環境の準備

### 必要なもの

| ツール | 用途 | 確認コマンド |
|--------|------|-------------|
| Docker | バックエンド・フロントエンドのコンテナ起動 | `docker --version` |
| Docker Compose | 複数コンテナの一括管理 | `docker compose version` |
| Python 3.10以上 | スクレイパーの手動実行（実データ取得時のみ） | `python3 --version` |

> Docker Desktop（Mac/Windows）をインストールすれば Docker と Docker Compose の両方が揃います。

### ディレクトリ構成

```
baseball-app/
├── docker-compose.yml       # ← アプリの起動設定
├── data/
│   └── baseball.db          # ← SQLiteデータベース（スクレイパー実行で生成）
├── backend/                 # FastAPI（Python）
│   └── app/
│       ├── api/routes/      # APIエンドポイント
│       ├── models/          # DBモデル（SQLAlchemy）
│       ├── services/        # ビジネスロジック
│       └── repositories/    # DB操作
├── frontend/                # Next.js（TypeScript）
│   ├── app/                 # ページ（ダッシュボード・ランキング・詳細・比較）
│   ├── components/          # 共通コンポーネント
│   └── lib/api.ts           # APIクライアント
└── scraper/                 # Baseball Reference / NPB公式 からのデータ取得ツール
    ├── sources/
    │   ├── baseball_reference/   # 第1候補のデータ取得元
    │   │   ├── fetcher.py        # HTTP取得 + コメント展開
    │   │   ├── league_index.py   # 年度 → リーグID の自動検出
    │   │   ├── batting_scraper.py
    │   │   ├── pitching_scraper.py
    │   │   └── team_scraper.py
    │   └── npb_official/         # 403 / 0件時のフォールバック
    ├── loaders/             # DB投入
    ├── config.py            # 設定（URL・チームコードマッピングなど）
    └── cli.py               # 手動実行エントリーポイント
```

---

## STEP 2 — スクレイパーで実データを取得する

[Baseball Reference](https://www.baseball-reference.com) の NPB 統計ページを優先して取得し、403 などで取得できない場合は `NPB公式` に自動でフォールバックします。
現在の取り込みデータでは、選手名は NPB公式由来の日本語名で保存されることがあります。

> **注意：** サーバーへの負荷を抑えるため、リクエスト間に自動で 3 秒の待機を入れています。
> 大量の年度をまとめて取得する場合は時間がかかります。

#### 手順

**① スクレイパーのセットアップ（初回のみ）**

```bash
cd baseball-app/scraper
pip install -r requirements.txt
```

**② データを取得して DB に書き込む（fetch）**

スクレイパーは `scraper/` ディレクトリの中から `python cli.py` で実行します。
fetch と DB 書き込みは一度のコマンドで完結します。

```bash
# scraper/ ディレクトリにいる状態で実行
cd baseball-app/scraper

# 1年分（例：2024年）
python cli.py fetch --year 2024

# 複数年まとめて（例：2020〜2024年）
python cli.py fetch-all --start 2020 --end 2024

# 種別を絞って取得（打者のみ / 投手のみ / チームのみ）
python cli.py fetch --year 2024 --type batters
python cli.py fetch --year 2024 --type pitchers
python cli.py fetch --year 2024 --type teams
```

`data/baseball.db` はこの手順で生成されます。初回 `fetch` では、スクレイパーが必要なテーブルと 12 球団のマスタも自動作成します。アプリが起動中でもそのまま実行できます。

`fetch --year 2024` の内部挙動は次の通りです。

- `teams`: Baseball Reference を試し、取得できなければ NPB公式の勝敗表へフォールバック
- `batters`: Baseball Reference を試し、取得できなければ NPB公式の球団別個人打撃成績へフォールバック
- `pitchers`: Baseball Reference を試し、取得できなければ NPB公式の球団別個人投手成績へフォールバック

> **必須:** `docker compose up --build` の前に、少なくとも 1 回は `fetch` か `fetch-all` を実行してください。
> DB が空のままでもバックエンドは起動しますが、ランキングや選手データは表示されません。

> **補足:** 現時点では Baseball Reference 側が 403 を返すことがあり、その場合でも CLI は自動的に NPB公式へ切り替えて続行します。

---

## STEP 3 — アプリの起動

`baseball-app/` ディレクトリで以下のコマンドを実行します。

```bash
cd baseball-app
docker compose up --build
```

初回はDockerイメージのビルドに数分かかります。

以下の2行が出れば起動完了です：

```
baseball-app-backend  | INFO:     Application startup complete.
baseball-app-frontend | ▲ Next.js ready - started server on 0.0.0.0:3000
```

### アクセス先

| URL | 内容 |
|-----|------|
| http://localhost:3000 | アプリ本体（フロントエンド） |
| http://localhost:8000/docs | APIドキュメント（Swagger UI） |
| http://localhost:8000/health | ヘルスチェック |

---

## 各画面の使い方

### ダッシュボード（トップ）

年度を選択すると、その年の OPS 上位・防御率上位のランキングとチーム成績が表示されます。
初期表示では極端な少数打席・少数投球回の選手を避けるため、打者は **300打席以上**、投手は **100投球回以上** で絞っています。
選手名をクリックすると選手詳細ページに遷移します。

### 打者ランキング `/batters`

| 操作 | 内容 |
|------|------|
| 指標を選ぶ | OPS・打率・本塁打・打点など任意の指標で並べ替えができます |
| 球団で絞る | 特定球団の選手だけ表示できます |
| 最小打席で絞る | 既定値は `300`。必要に応じて規定打席相当まで調整できます |
| 表示件数 | 20件・50件・100件から選べます |

### 投手ランキング `/pitchers`

打者と同様の操作に加えて、**先発 / 救援 の切り替え**と**最小投球回フィルタ**があります。
初期値は `100` 投球回です。

### チーム成績 `/teams`

指標別のチームランキングを表示します。年度を切り替えると過去シーズンと比較できます。

### 選手詳細 `/players/[id]`

- 基本情報（球団・守備位置・投打）
- 全シーズンの成績一覧
- シーズン推移グラフ
- 「比較に追加」ボタン → 比較ページに遷移

### 選手比較 `/compare`

最大4人の選手を全指標で横並び比較できます。年度も指定できます。

---

## データの更新方法

シーズン終了後や途中で最新データに更新したいときは、スクレイパーを再実行するだけです。
**アプリの再起動は不要です。**

```bash
# 例：2025年シーズン終了後に更新する
cd baseball-app/scraper
python cli.py fetch --year 2025
```

ブラウザをリロードすると新しいデータが反映されます。

---

## アプリの停止

```bash
docker compose down
```

`data/baseball.db` はコンテナを停止・削除しても消えません。

---

## トラブルシューティング

### ポートが使われていると言われる

別のプロセスが 8000番または 3000番を使っています。

```bash
# Macの場合
lsof -i :8000
lsof -i :3000
```

該当プロセスを停止するか、`docker-compose.yml` のポート番号を変更してください。

### 画面が真っ白・「API Error」が出る

フロントエンドがバックエンドに接続できていないか、バックエンド起動時に DB 初期化で落ちている可能性があります。

```bash
# バックエンドのログを確認
docker compose logs backend

# APIが動いているか確認
curl http://localhost:8000/health
# → {"status":"healthy"} と返ってくればOK
```

### データが表示されない（ランキングが空）

`data/baseball.db` に対象データが入っていない状態です。

- `docker compose up --build` の前に `python cli.py fetch --year 2024` などを実行したか
- `scraper/` ディレクトリから実行しているか
- `data/baseball.db` が生成されているか
- `teams` だけでなく `batters` / `pitchers` も取得したか

を確認してください。

たとえば `teams` だけ取得した状態では、チーム画面は表示できますが、打者・投手ランキングは空のままです。

### スクレイパーで `ModuleNotFoundError` が出る

`scraper/` ディレクトリの中から実行しているか確認してください。

```bash
# 正しい実行方法
cd baseball-app/scraper
python cli.py fetch --year 2024

# NG（baseball-app/ から -m で実行するとパスエラーになる場合があります）
```

### Dockerイメージを一から作り直したい

```bash
docker compose down
docker compose up --build
```

---

## 拡張のヒント

### 新しい指標を追加したいとき

1. `stat_definitions` テーブルに新しい行を追加（stat_key・表示名・カテゴリなどを定義）
2. 対応する stats テーブル（`batter_season_stats` など）にカラムを追加
3. スクレイパーで値を取得・投入

これだけでランキング・比較・グラフへの連携は自動で行われます。コードの大規模な変更は不要です。

### 他リーグ（MLB など）のデータを追加したいとき

Baseball Reference はMLBや他の国際リーグも同様の構造でデータを公開しています。
`scraper/sources/baseball_reference/league_index.py` の encyclopedia URL を変更し、
チームコードマッピング（`scraper/config.py` の `TEAM_NAME_TO_CODE`）を追記するだけで
同じスクレイパーが流用できます。

### 月次推移を追加したいとき

`batter_monthly_stats` / `pitcher_monthly_stats` テーブルはすでに設計されています。
スクレイパーで月次データを取得・投入すれば、APIとフロントエンドは最小限の修正で対応できます。

### PostgreSQL に移行したいとき

`docker-compose.yml` の環境変数を変更するだけです。

```yaml
DATABASE_URL: "postgresql+asyncpg://user:pass@postgres:5432/baseball"
```

---

## 技術スタック

| 層 | 技術 |
|----|------|
| フロントエンド | Next.js 14 / TypeScript / Tailwind CSS / Recharts |
| バックエンドAPI | FastAPI / SQLAlchemy (async) / Pydantic |
| データベース | SQLite（→ PostgreSQL に移行可） |
| スクレイパー | Python / requests / BeautifulSoup4 / pandas |
| データソース | [Baseball Reference](https://www.baseball-reference.com) NPB統計ページ |
| インフラ | Docker / Docker Compose |
