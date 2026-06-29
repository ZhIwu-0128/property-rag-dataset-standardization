# Property RAG Dataset Standardization

本仓库是一个**脱敏公开版项目模板**，用于展示面向政务热线、客服工单、城市治理文本数据的高质量数据集标准化与 RAG 数据底座建设方法。

> 安全说明：本仓库不包含任何真实工单数据、原始 Excel、真实 JSONL、embedding 向量、旧数据归档、新旧映射文件、数据库连接信息或业务敏感信息。`examples/` 中的样例均为合成数据，仅用于展示 schema 和工程流程。

## 项目目标

- 字段盘点与 schema 设计；
- 标准 JSONL 转换；
- train / validation / test 划分；
- dataset manifest 设计；
- 旧数据归档与新旧映射设计；
- 数据质量验收；
- 标准化 metadata 扩展；
- RAG payload 设计；
- GitHub 公开展示的脱敏工程结构。

## 核心原则

只对问题描述文本做 embedding：

```text
embedding_text_field = data_content[0].content
embedding_policy = only_origin_query
```

以下字段不参与 embedding，仅作为检索后的解释、展示、筛选和评估信息：

```text
annotation
final_result
quality_info
semantic_info
split_info
processing_info
metadata
```

## 标准 JSONL 顶层结构

```text
id
rid
data_content
annotation
original_time
last_modified_time
version
license
source
source_details
generated_data_indicator
source_record
final_result
quality_info
semantic_info
split_info
processing_info
metadata
```

## 仓库结构

```text
docs/       数据集 schema、治理流程、RAG payload 和验收清单
examples/   合成样例 JSONL、manifest 和报告
scripts/    脱敏演示脚本
notebooks/  Notebook 说明，公开仓库默认不上传真实 Notebook 输出
```

## 快速验证样例

```bash
python scripts/validate_jsonl_schema.py examples/synthetic_property_rag_sample.jsonl
```

## 简历项目描述

见：

```text
docs/resume_project_summary.md
```
