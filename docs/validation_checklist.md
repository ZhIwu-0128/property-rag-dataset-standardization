# Validation Checklist

## 文件级检查

- [ ] JSONL 文件存在；
- [ ] manifest 文件存在；
- [ ] JSONL 每行都是合法 JSON；
- [ ] 样本总数与 manifest 一致；
- [ ] split 文件行数相加等于全量。

## 字段级检查

- [ ] `id` 存在；
- [ ] `data_content[0].content` 存在；
- [ ] `annotation` 存在；
- [ ] `final_result` 存在；
- [ ] `split_info.split` 存在；
- [ ] `metadata.schema_version` 存在；
- [ ] `metadata.rag_config.embedding_text_field` 存在；
- [ ] `metadata.rag_config.do_not_embed_fields` 包含 `metadata`。

## 安全检查

- [ ] 不包含真实姓名；
- [ ] 不包含手机号；
- [ ] 不包含身份证号；
- [ ] 不包含真实地址；
- [ ] 不包含真实 Excel、JSONL、embedding 向量；
- [ ] Notebook 输出已清空。
