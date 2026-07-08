"""
推理服务器 HTTP 客户端

统一封装与内网推理服务器的HTTP通信（OpenAI v1 API格式）。
embedding和rerank各自通过HTTP发送请求、取回结果。

【数据安全】数据通过内网HTTP传输，全程在内存中，不落盘。
"""

import time
import httpx
from typing import Any

import config


class InferenceClient:

    def __init__(self):
        embedding_pool = config.EMBEDDING_THREAD_COUNT * 2
        rerank_pool = config.RERANK_THREAD_COUNT * 2
        self._auth_headers = {"Authorization": f"Bearer {config.API_KEY}"}

        self._embedding_client = httpx.Client(
            timeout=httpx.Timeout(config.INFERENCE_TIMEOUT),
            limits=httpx.Limits(
                max_connections=embedding_pool,
                max_keepalive_connections=embedding_pool,
            ),
        )
        self._rerank_client = httpx.Client(
            timeout=httpx.Timeout(config.INFERENCE_TIMEOUT),
            limits=httpx.Limits(
                max_connections=rerank_pool,
                max_keepalive_connections=rerank_pool,
            ),
        )

    def get_embedding(self, text: str) -> list[float]:
        """将文本转为向量。OpenAI v1格式: {"data": [{"embedding": [...]}]}"""
        payload = {"input": text, "model": config.EMBEDDING_MODEL}
        response = self._post_with_retry(
            client=self._embedding_client,
            url=config.EMBEDDING_API_URL,
            json_data=payload,
        )
        data = response.json()
        return data["data"][0]["embedding"]

    def rerank(self, query: str, documents: list[str]) -> list[tuple[int, float]]:
        """
        对候选文档精排打分。
        返回 [(原始索引, 相关性分数), ...]，按分数从高到低排列。
        """
        unique_docs, index_map = self._deduplicate(documents)

        payload = {"query": query, "documents": unique_docs, "model": config.RERANK_MODEL}
        response = self._post_with_retry(
            client=self._rerank_client,
            url=config.RERANK_API_URL,
            json_data=payload,
        )
        data = response.json()

        scored = []
        for item in data.get("results", []):
            unique_idx = item["index"]
            score = item["relevance_score"]
            for orig_idx in index_map[unique_idx]:
                scored.append((orig_idx, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored

    def close(self):
        self._embedding_client.close()
        self._rerank_client.close()

    def _post_with_retry(self, client: httpx.Client, url: str, json_data: dict[str, Any]) -> httpx.Response:
        """带指数退避重试的POST请求"""
        last_error = None
        for attempt in range(config.MAX_RETRIES + 1):
            try:
                response = client.post(url, json=json_data, headers=self._auth_headers)
                response.raise_for_status()
                return response
            except (httpx.TimeoutException, httpx.HTTPStatusError, httpx.ConnectError) as e:
                last_error = e
                if attempt < config.MAX_RETRIES:
                    time.sleep(2 ** attempt)
        raise last_error

    def _deduplicate(self, documents: list[str]) -> tuple[list[str], dict[int, list[int]]]:
        """文档去重，记录映射关系。返回 (去重列表, {去重索引: [原始索引列表]})"""
        seen = {}
        unique_docs = []
        index_map = {}
        for orig_idx, doc in enumerate(documents):
            if doc not in seen:
                seen[doc] = len(unique_docs)
                unique_docs.append(doc)
                index_map[seen[doc]] = [orig_idx]
            else:
                index_map[seen[doc]].append(orig_idx)
        return unique_docs, index_map
