# Security and Data Safety

本仓库为脱敏公开版项目模板，不应包含任何真实业务数据。

## 禁止提交

- 真实工单文本；
- 原始 Excel、CSV、JSONL；
- embedding 向量；
- 数据库连接配置；
- Qdrant 连接配置；
- `.env` 文件；
- 带真实输出的 Notebook；
- 任何个人信息或敏感业务信息。

## 提交前检查

```bash
find . -name "*.xlsx" -o -name "*.npy" -o -name ".env"
find . -name "*.jsonl" -not -path "./examples/*"
grep -R "身份证\|电话\|手机号\|住址\|original_id\|source_file" .
```
