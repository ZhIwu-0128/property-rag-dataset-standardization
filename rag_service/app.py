"""
FastAPI 应用入口

4个API路由 + 生命周期管理（启动时创建组件、关闭时释放资源）。

【日志安全】只记录请求路径、状态码、耗时，绝不记录query和内容。
"""

import time
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

import config
from models import EmbeddingQueryRequest, RerankRequest, RAGQueryRequest, SearchResponse
from inference_client import InferenceClient
from vector_store import QdrantSearchClient
from embedding_worker import EmbeddingWorkerPool
from rerank_worker import RerankWorkerPool
from rag_orchestrator import RAGOrchestrator

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("rag_service")

inference_client: InferenceClient | None = None
qdrant_client: QdrantSearchClient | None = None
embedding_pool: EmbeddingWorkerPool | None = None
rerank_pool: RerankWorkerPool | None = None
orchestrator: RAGOrchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global inference_client, qdrant_client, embedding_pool, rerank_pool, orchestrator

    logger.info("=== RAG服务启动中 ===")
    inference_client = InferenceClient()
    qdrant_client = QdrantSearchClient()
    embedding_pool = EmbeddingWorkerPool(inference_client, qdrant_client)
    embedding_pool.start()
    rerank_pool = RerankWorkerPool(inference_client)
    rerank_pool.start()
    orchestrator = RAGOrchestrator(embedding_pool, rerank_pool)
    logger.info("=== RAG服务启动完成 ===")

    yield

    logger.info("=== RAG服务关闭中 ===")
    if embedding_pool:
        embedding_pool.shutdown()
    if rerank_pool:
        rerank_pool.shutdown()
    if inference_client:
        inference_client.close()
    if qdrant_client:
        qdrant_client.close()
    logger.info("=== RAG服务已关闭 ===")


app = FastAPI(
    title="RAG 检索服务",
    description="基于 Qwen3-Embedding + Qwen3-Reranker + Qdrant 的两阶段检索API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    latency = (time.perf_counter() - start) * 1000
    logger.info("%s %s → %d, %.1fms", request.method, request.url.path, response.status_code, latency)
    return response


@app.post("/api/rag/query", response_model=SearchResponse)
async def rag_query(request: RAGQueryRequest):
    """完整RAG：Embedding召回 + Rerank精排"""
    if orchestrator is None:
        raise HTTPException(503, "服务尚未就绪")
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: orchestrator.query(query=request.query, top_k=request.top_k, top_n=request.top_n),
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        logger.error("RAG查询失败: %s", type(e).__name__)
        raise HTTPException(500, "查询处理失败")


@app.post("/api/embedding/query", response_model=SearchResponse)
async def embedding_query(request: EmbeddingQueryRequest):
    """仅向量检索"""
    if orchestrator is None:
        raise HTTPException(503, "服务尚未就绪")
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: orchestrator.embedding_only(query=request.query, top_k=request.top_k),
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        logger.error("Embedding查询失败: %s", type(e).__name__)
        raise HTTPException(500, "查询处理失败")


@app.post("/api/rerank/query", response_model=SearchResponse)
async def rerank_query(request: RerankRequest):
    """仅重排序"""
    if orchestrator is None:
        raise HTTPException(503, "服务尚未就绪")
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: orchestrator.rerank_only(query=request.query, documents=request.documents, top_n=request.top_n),
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    except Exception as e:
        logger.error("Rerank查询失败: %s", type(e).__name__)
        raise HTTPException(500, "查询处理失败")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "embedding_threads": config.EMBEDDING_THREAD_COUNT, "rerank_threads": config.RERANK_THREAD_COUNT}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
