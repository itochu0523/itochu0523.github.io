# タスク: BigQuery SQL 作成・最適化

## テンプレート

```
以下の要件で BigQuery SQL を書いてください。

【目的】


【テーブル構成】
- テーブル名: `project.dataset.table`
- 主なカラム:
  - column_a: STRING
  - column_b: TIMESTAMP
  - column_c: INTEGER

【条件・フィルタ】


【出力カラム】


【パフォーマンス要件】
- 対象期間: （例: 直近30日）
- データ量目安: （例: 日次 100万行）

---

Standard SQL で記述し、以下を守ってください：
1. パーティションカラム (_PARTITIONTIME or 日付カラム) を WHERE に含める
2. SELECT * は使わない
3. 不要な JOIN はしない
4. WITH 句で可読性を上げる
```
