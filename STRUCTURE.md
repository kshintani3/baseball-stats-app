# NPB Baseball Statistics App - Complete Structure

## Scraper Module

```
scraper/
├── cli.py                               # fetch / fetch-all のエントリーポイント
├── config.py                            # DBパス、URL、チーム名マッピング
├── loaders/
│   └── db_loader.py                     # Baseball Reference 取得結果を SQLite に upsert
├── normalize/
│   └── normalizer.py                    # 旧データ整形ロジック
└── sources/
    ├── baseball_reference/
    │   ├── fetcher.py                   # HTTP取得 + HTMLコメント内テーブル展開
    │   ├── league_index.py              # 年度ごとの league ID 解決
    │   ├── batting_scraper.py           # 打者成績取得
    │   ├── pitching_scraper.py          # 投手成績取得
    │   └── team_scraper.py              # チーム成績取得
    └── npb_official/
        ├── fetchers/                    # NPB公式HTML取得
        └── parsers/                     # 球団別個人成績・勝敗表の解析
```

## Key Features

### Current data source
- 現行の実行経路は `Baseball Reference` を第1候補にし、取得失敗時は `NPB公式` にフォールバックする
- Baseball Reference 側はリーグ単位の成績ページ、NPB公式側は球団別個人成績ページと勝敗表を使う
- リクエスト間に 3 秒待機を入れる

### CLI Interface (`scraper/cli.py`)

```bash
# 単年取得
python cli.py fetch --year 2024
python cli.py fetch --year 2024 --type batters
python cli.py fetch --year 2024 --type pitchers
python cli.py fetch --year 2024 --type teams

# 複数年取得
python cli.py fetch-all --start 2020 --end 2024
python cli.py fetch-all --start 2020 --end 2024 --type teams
```

- `fetch` / `fetch-all` は取得から DB 書き込みまでを一度に実行する
- 出力先 DB は `data/baseball.db`
- DB ファイルが存在しない場合は、スクレイパー実行時またはバックエンド起動時に生成される
- `teams` / `batters` / `pitchers` は個別実行できる
- 現状のフロント既定値は `batters: min_pa=300`, `pitchers: min_ip=100`

### Database loading
- `db_loader.py` は `players`, `batter_season_stats`, `pitcher_season_stats`, `team_season_stats` を upsert する
- バックエンド起動時の初期投入は `stat_definitions` と `teams` のみ
- 選手・シーズン成績データはスクレイパー経由でのみ投入する

## Notes

- `normalize/normalizer.py` は旧構成の残存物
- `sources/npb_official/` は現在の CLI からフォールバック経路として使用される
- 実データ取得フローに統一され、同梱の成績データや生成コードは持たない
