"""
RAG 编排器

串联 embedding 召回和 rerank 精排两个阶段，完成完整的 RAG 查询。

提供三个入口：
- query():          完整RAG (Embedding + Rerank)
- embedding_only(): 仅向量检索
- rerank_only():    仅精排重排序

【数据安全】全部数据在局部变量中流转，编排完成后自动释放。
"""

import time
import logging
from typing import Optional

import config
from models import SearchResult, SearchResponse

logger = logging.getLogger(__name__)


class RAGOrchestrator:

    def __init__(self, embedding_pool, rerank_pool):
        self._embedding_pool = embedding_pool
        self._rerank_pool = rerank_pool

    def query(self, query: str, top_k: Optional[int] = None, top_n: Optional[int] = None) -> SearchResponse:
        """完整RAG：Stage1 Embedding召回 → Stage2 Rerank精排"""
        start_time = time.perf_counter()
        k = top_k if top_k is not None else config.TOP_K_RETRIEVAL
        n = top_n if top_n is not None else config.TOP_N_RERANK

        # Stage 1: Embedding 召回
        logger.info("Stage1 Embedding召回开始，top_k=%d", k)
        stage1_start = time.perf_counter()
        embedding_future = self._embedding_pool.submit(query)
        candidate_results = embedding_future.result()
        stage1_latency = (time.perf_counter() - stage1_start) * 1000
        logger.info("Stage1 完成，候选数=%d，耗时=%.1fms", len(candidate_results), stage1_latency)

        if not candidate_results:
            return SearchResponse(results=[], latency_ms=stage1_latency)

        # Stage 2: Rerank 精排
        logger.info("Stage2 Rerank精排开始，候选数=%d，top_n=%d", len(candidate_results), n)
        documents = [item["text"] for item in candidate_results]
        rerank_future = self._rerank_pool.submit(query, documents)
        reranked_results = rerank_future.result()[:n]

        total_latency = (time.perf_counter() - start_time) * 1000
        logger.info("Stage2 完成，最终结果=%d，总耗时=%.1fms", len(reranked_results), total_latency)

        final_results = []
        for item in reranked_results:
            original_idx = item.get("original_index", 0)
            metadata = None
            if original_idx < len(candidate_results):
                metadata = candidate_results[original_idx].get("metadata")
            final_results.append(SearchResult(
                text=item["text"], score=item["score"], metadata=metadata,
            ))
        return SearchResponse(results=final_results, latency_ms=total_latency)

    def embedding_only(self, query: str, top_k: Optional[int] = None) -> SearchResponse:
        """仅Embedding向量检索（跳过Rerank）"""
        start = time.perf_counter()
        k = top_k if top_k is not None else config.TOP_K_RETRIEVAL
        future = self._embedding_pool.submit(query)
        results = future.result()
        latency = (time.perf_counter() - start) * 1000
        return SearchResponse(
            results=[SearchResult(**r) for r in results],
            latency_ms=latency,
        )

    def rerank_only(self, query: str, documents: list[str], top_n: Optional[int] = None) -> SearchResponse:
        """仅Rerank精排（跳过Embedding检索）"""
        start = time.perf_counter()
        n = top_n if top_n is not None else config.TOP_N_RERANK
        future = self._rerank_pool.submit(query, documents)
        results = future.result()[:n]
        latency = (time.perf_counter() - start) * 1000
        return SearchResponse(
            results=[SearchResult(**r) for r in results],
            latency_ms=latency,
        )
