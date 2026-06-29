# Notebooks

公开仓库默认不上传真实 Notebook。

原因：

- Notebook 输出区可能包含真实工单文本；
- 输出区可能包含标签路径、原始 ID、来源文件名；
- 即使代码脱敏，输出也可能泄密。

如需公开 Notebook，请先执行：

```bash
python scripts/strip_notebook_outputs.py notebooks
```
