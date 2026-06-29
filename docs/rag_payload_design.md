# RAG Payload Design

## embedding 字段

```text
data_content[0].content
```

不要把标签、理由、metadata、质量信息拼进 embedding 文本，否则容易引入召回噪声。

## 建议 payload

```json
{
  "id": "demo_001",
  "query": "合成问题描述",
  "split": "train",
  "final_label": "是",
  "final_label_id": 1,
  "final_tags": {
    "level_1": "公共设施",
    "level_2": "电梯管理",
    "level_3": "电梯故障"
  },
  "reason": "简要判断理由",
  "tag_reason": "简要标签理由",
  "source_file": "synthetic_source",
  "semantic_cluster_id": 1
}
```

## 不建议默认进入 payload

- 完整旧数据；
- 完整 `reason_details` 长列表；
- 大段 processing 信息；
- dataset manifest；
- 大量重复 metadata。
