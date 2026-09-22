# itochu0523.github.io

@~/ObsidianVault/claude/CLAUDE.md

## このプロジェクト固有
- 自作アプリ群のポータル・公開リポジトリ
- 公開: GitHub Pages（`main` push で自動反映。デプロイ作業は不要）
- データ保存: 各アプリJSONbinで管理し、iPhone/PC/iPadで同期（今後Firebase等への移行も検討候補）

### アプリ一覧（ディレクトリ = 1アプリ、hunter配下のみ3アプリ同居）

| ディレクトリ / ファイル | アプリ名 |
|---|---|
| `meshi/` | 【料理アプリ】食事分析 |
| `hunter/hunter-quiz.html` 他 | 【学習管理】狩猟免許試験の総合学習管理 |
| `hunter/gun-quiz.html` 他 | ［計画］銃所持許可計画 |
| `hunter/hunter-timeline.html` | 【学習タイムライン】狩猟免許と銃取得のタイムライン管理 |
| `tasks/daily-tasks.html` | 【TODOアプリ】曜日別タスク管理 |
| `pack/packlist.html` | 【持ち物アプリ】複数シーン対応の持ち物チェックリスト |

- `sanpo/`（散歩メモ）: 管理対象アプリの一覧には含めない
- `tasks/patch.py`〜`patch5.py`, `tasks/recipe-app.html`: 用途不明・要確認（消さずに保留）
- `dmc/`, `docs/`: DMC業務系の別ドキュメント（個人アプリ群とは別管理）

### 作業依頼のフォーマット
このリポジトリで作業する際は、冒頭で以下を宣言する。
```
アプリ: <ディレクトリ名 or アプリ名>
やること: <1行>
```
