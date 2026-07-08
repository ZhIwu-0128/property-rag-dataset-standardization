# Property RAG — 政务热线 AI 智能检索系统

本仓库展示面向政务热线工单场景的 **AI 语义检索引擎**完整工程实践：从非结构化文本的数据治理，到大模型驱动的向量语义检索，再到 AI 服务的工程化部署。

> 安全说明：本仓库不包含任何真实工单数据或敏感信息。`examples/` 为合成样例，`rag_service/config.py` 为脱敏配置模板。

---

## 项目全景

```
┌─ 数据工程 ─────────────────────────────────────────────┐
│  原始工单 → Schema标准化 → 质量验收 → Embedding向量化   │
│            → Qdrant向量数据库入库 (AI数据底座)          │
└────────────────────────────┬──────────────────────────┘
                             │
┌─ AI检索引擎 ───────────────────────────────────────────┐
│  用户查询 → Embedding语义向量 → Qdrant粗召回(Top-K)     │
│           → Cross-Encoder精排(Top-N) → 相似工单结果     │
│                                                         │
│  🚀 多线程并发 | ⚡ 毫秒级检索 | 🔒 数据全链路不落地   │
└────────────────────────────┬──────────────────────────┘
                             │
┌─ AI服务工程化 ─────────────────────────────────────────┐
│  FastAPI + OpenAI v1 API | 健康检查 | 自动重试 | 优雅启停 │
└───────────────────────────────────────────────────────┘
```

---

## 核心 AI 能力

### 语义理解（Embedding）
基于 Qwen3-Embedding-4B 大模型，将自然语言查询（如"电梯老坏"）映射为 2560 维语义向量，在 Qdrant 向量数据库中通过 HNSW 算法毫秒级定位语义相似的工单——超越传统关键词匹配。

### 精准排序（Reranker）
基于 Qwen3-Reranker-4B Cross-Encoder 模型，对粗召回候选进行逐对精细语义比对，识别"电梯故障无人维修"与"升降设备损坏物业长时间未处理"为同一类诉求。

### 并发引擎
生产者-消费者多线程架构，支持可配置并发数（默认4线程），独立队列管理 embedding 和 rerank 两阶段，队列溢出保护。

---

## 仓库结构

```text
docs/           数据 schema、治理流程、RAG payload 设计、验收清单
examples/       合成样例 JSONL、manifest 和质量报告
scripts/        数据校验与处理脚本
notebooks/      Jupyter Notebook 说明
rag_service/    AI 检索服务源码
  ├── config.py             配置中心（模型、线程池、向量库参数）
  ├── models.py             Pydantic 数据模型
  ├── inference_client.py   AI 推理服务器客户端（Embedding + Rerank）
  ├── vector_store.py       Qdrant 向量数据库客户端（gRPC）
  ├── embedding_worker.py   Embedding 并发线程池
  ├── rerank_worker.py      Rerank 并发线程池
  ├── rag_orchestrator.py   两阶段检索编排器
  ├── app.py                FastAPI AI 服务入口
  ├── verify.py             Mock 离线验证（9项自动化测试）
  └── README.md
```

## 快速开始

```bash
cd rag_service
pip install fastapi uvicorn httpx pydantic qdrant-client

# 离线验证（无需外部AI服务）
python verify.py

# 配置实际地址后启动AI服务
nohup uvicorn app:app --host 0.0.0.0 --port 8001 &

# API 调用
curl http://127.0.0.1:8001/api/health
curl -X POST http://127.0.0.1:8001/api/embedding/query \
  -H "Content-Type: application/json" \
  -d '{"query": "电梯故障报修无人处理", "top_k": 5}'
```

## API 接口

| 方法 | 路径 | AI 能力 |
|------|------|---------|
| GET | `/api/health` | 服务健康检查 |
| POST | `/api/embedding/query` | 语义向量检索 |
| POST | `/api/rerank/query` | Cross-Encoder 精排 |
| POST | `/api/rag/query` | 完整 AI 检索（召回+精排） |

## 数据治理原则

**Embedding Only 策略** — 仅对问题描述文本进行向量化：

```text
embedding_text = data_content[0].content   # 仅原始问题描述
```

标签层级、判断理由、质量元数据等结构化字段作为 Qdrant Payload 保留，**不参与 embedding**，避免语义噪声，提升召回精准度。

## 标准 JSONL Schema

```text
id · rid · data_content · annotation · original_time
last_modified_time · version · license · source
final_result · quality_info · semantic_info
split_info · processing_info · metadata
```

## 简历项目描述

见 `rag_service/resume_project_summary_updated.md` 或 `docs/resume_project_summary.md`
