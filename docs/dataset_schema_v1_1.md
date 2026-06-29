# Dataset Schema v1.1

## 设计目标

v1.1 schema 用于描述面向 RAG 检索和分类评估的标准 JSONL 记录。

## 顶层字段

| 字段 | 含义 |
|---|---|
| `id` | 标准数据集内部唯一 ID |
| `rid` | 外部关联 ID，可为空数组 |
| `data_content` | 核心文本内容，`data_content[0].content` 为 embedding 字段 |
| `annotation` | 标准标注摘要与 AI/人工候选标注 |
| `source_record` | 来源文件、行号、原始 ID 的脱敏引用 |
| `final_result` | 最终业务结果，包括二分类、三级标签、理由 |
| `quality_info` | AI/人工对比、数据性质、标签一致性等质量信息 |
| `semantic_info` | 语义聚类相关信息 |
| `split_info` | train / validation / test |
| `processing_info` | 标准化处理过程信息 |
| `metadata` | v1.1 新增的标准化数据集上下文 |

## metadata 字段

`metadata` 用于记录：

```text
dataset_name
schema_version
metadata_scope
manifest_ref
base_dataset
split_config
rag_config
```

`metadata` 不参与 embedding，也不建议默认全量进入 Qdrant payload。
