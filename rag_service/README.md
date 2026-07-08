# RAG 检索服务 (rag_service)

政务热线物业工单 RAG 智能检索服务。基于 Qwen3-Embedding + Qwen3-Reranker + Qdrant 的两阶段检索架构，采用生产者-消费者多线程并发模型，通过 FastAPI 对外提供 HTTP 接口。

## 核心特性

- **两阶段检索**：Embedding 召回（Stage 1）+ Rerank 精排（Stage 2），兼顾速度和精度
- **多线程并发**：独立队列 + 可配置线程池，embedding 和 rerank 各 4 线程并行处理
- **数据安全**：全链路内存流转，日志不记录查询内容，无文件缓存
- **优雅启停**：哨兵信号通知 + 资源正确释放
- **OpenAI 兼容**：推理接口走 OpenAI v1 API 格式，服务间通过内网 HTTP/gRPC 通信

## 架构

```
FastAPI (app.py)
  → RAGOrchestrator (rag_orchestrator.py)
    → EmbeddingWorkerPool (embedding_worker.py) → 推理服务器 + Qdrant
    → RerankWorkerPool (rerank_worker.py)        → 推理服务器
```

## 快速开始

### 1. 配置

编辑 `config.py`，填写实际地址和 Key：

```python
EMBEDDING_API_URL  = "http://IP:端口/v1/embeddings"   # 推理服务器
RERANK_API_URL     = "http://IP:端口/v1/rerank"       # 推理服务器
QDRANT_HOST        = "127.0.0.1"                      # Qdrant IP
QDRANT_PORT        = 6334                             # Qdrant gRPC端口
QDRANT_API_KEY     = "your-key"                       # Qdrant Key
API_KEY            = "your-key"                       # 推理服务器 Key
QDRANT_COLLECTION  = "property_rag_train_v1_1"        # 集合名称
```

### 2. 安装依赖

```bash
pip install fastapi uvicorn httpx pydantic qdrant-client --break-system-packages
```

### 3. 验证（离线，不需要连接外部服务）

```bash
python verify.py
```

### 4. 端到端测试（需连接推理服务器和 Qdrant）

```bash
python test_e2e_embedding.py
```

### 5. 启动服务

```bash
cd rag_service
nohup uvicorn app:app --host 0.0.0.0 --port 8001 > /dev/null 2>&1 &
```

### 6. 测试接口

```python
import requests
print(requests.get("http://127.0.0.1:8001/api/health").json())
print(requests.post("http://127.0.0.1:8001/api/embedding/query",
    json={"query": "电梯故障报修", "top_k": 3}).json())
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/embedding/query` | 向量检索（embedding召回 → Qdrant搜索） |
| POST | `/api/rerank/query` | 重排序（给定候选文档，精确排序） |
| POST | `/api/rag/query` | 完整RAG（两阶段：召回 + 精排） |

## 文件说明

| 文件 | 职责 |
|------|------|
| `config.py` | 所有可配置参数（线程数、地址、Key、检索参数） |
| `models.py` | Pydantic数据模型（请求/响应/内部任务结构） |
| `inference_client.py` | 推理服务器HTTP客户端（embedding + rerank，含重试和去重） |
| `vector_store.py` | Qdrant gRPC客户端 |
| `embedding_worker.py` | Embedding线程池（生产者-消费者，4线程并发） |
| `rerank_worker.py` | Rerank线程池（同上，独立队列和线程池） |
| `rag_orchestrator.py` | RAG编排器（串联两阶段，含embedding_only/完整RAG） |
| `app.py` | FastAPI应用入口（4个路由 + 生命周期管理） |
| `verify.py` | Mock离线验证（9项测试，无需外部依赖） |
| `test_e2e_embedding.py` | Embedding端到端测试（需推理服务器 + Qdrant） |

## 技术选型

| 组件 | 选型 |
|------|------|
| Embedding模型 | Qwen3-embedding 系列（4B/8B），2560维向量 |
| Rerank模型 | Qwen3-reranker 系列（4B/8B），Cross-Encoder |
| 向量数据库 | Qdrant，gRPC协议，HNSW索引 |
| Web框架 | FastAPI（异步支持，自动文档，自动校验） |
| HTTP客户端 | httpx（连接池，超时控制，重试） |
| 并发模型 | threading + queue.Queue（生产者-消费者） |
