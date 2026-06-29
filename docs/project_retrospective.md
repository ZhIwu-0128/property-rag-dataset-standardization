# Project Retrospective

## 项目价值

这个项目的价值不在于简单调用向量数据库，而在于把原始业务标注数据治理为可复现、可审计、可用于 RAG 的数据底座。

## 关键设计取舍

### 旧数据单独归档

新 JSONL 保持干净；旧数据通过归档和 crosswalk 追溯。

### 每条记录新增标准化 metadata

metadata 提升单条记录自解释能力，但不参与 embedding，也不默认进入 Qdrant payload。

### 只对问题描述 embedding

标签、理由和人工/AI 判断保留为 payload，避免召回噪声。

## 经验总结

高质量 RAG 项目首先是数据治理项目，其次才是模型和向量数据库项目。
