# RAG 检索服务 — 完整测试 Notebook

数据来源：热线工单物业投诉内容  
按顺序逐节运行，每节独立可重跑。

## 使用说明

### 前置条件
- 已安装依赖：`pip install fastapi uvicorn httpx pydantic qdrant-client grpcio`
- `config.py` 中已填写正确的推理服务器地址、Qdrant 地址和 API Key
- 服务已启动：`nohup uvicorn app:app --host 0.0.0.0 --port 8001 &`
- 关闭服务：`fuser -k 8001/tcp`

### 测试内容

| 节 | 内容 | 依赖 |
|----|------|------|
| 0 | 环境准备 | - |
| 1 | 8个模块导入检查 | - |
| 2 | 当前所有配置一览 | config.py |
| 3 | 推理服务器测试（物业场景query→向量） | 推理服务器 |
| 4 | Qdrant连接测试（collection、数据量） | Qdrant |
| 5 | 串联检索（query→向量→Qdrant→文档） | 推理+Qdrant |
| 6 | 线程池并发测试（8条查询4线程） | 推理+Qdrant |
| 7 | RAG编排器测试（USE_RERANK开关） | 推理+Qdrant |
| 8 | FastAPI接口测试 | 推理+Qdrant+服务 |
| 9 | 结果汇总 | - |

### 第7节 USE_RERANK 开关说明

```python
USE_RERANK = False   # 仅 Embedding 向量检索（reranker未部署时）
USE_RERANK = True    # 完整 RAG：Embedding召回 + Rerank精排（reranker部署后）
```

reranker部署后，将 `config.py` 中的 `RERANK_API_URL` 填好，然后改 `USE_RERANK = True` 即可。
