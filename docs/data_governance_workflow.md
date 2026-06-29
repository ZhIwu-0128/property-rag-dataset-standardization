# Data Governance Workflow

```text
字段盘点
→ schema 设计
→ 标准 JSONL 转换
→ train / validation / test 拆分
→ dataset_manifest 生成
→ 旧数据归档与新旧映射
→ 数据集验收
→ metadata 扩展
→ 文档生成
→ RAG payload 设计
```

## 关键治理原则

1. 新数据保持干净；
2. 旧数据单独归档；
3. 新旧关系通过 crosswalk 追溯；
4. 全局配置进入 dataset manifest；
5. 每条记录可通过 metadata 获得基本自解释能力；
6. Notebook 输出公开前必须清空。
