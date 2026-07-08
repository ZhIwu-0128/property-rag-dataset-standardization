"""
Qdrant 向量数据库客户端 (gRPC)

连接方式: gRPC 非加密, 端口 6334, API Key 认证
适配 qdrant-client >= 1.18.0

【数据安全】Qdrant部署在内网，查询结果直接返回到内存，不落盘。
"""

from typing import Optional
from qdrant_client import QdrantClient

import config


class QdrantSearchClient:

    def __init__(self):
        self._client = QdrantClient(
            host=config.QDRANT_HOST,
            port=config.QDRANT_PORT,
            api_key=config.QDRANT_API_KEY,
            prefer_grpc=True,
            https=False,
            timeout=config.QDRANT_TIMEOUT,
        )

    def search(
        self,
        query_vector: list[float],
        top_k: int,
        filter_conditions: Optional[dict] = None,
    ) -> list[dict]:
        """
        向量相似度搜索。使用 query_points() (qdrant-client 1.18.0+)。
        返回 [{"text": ..., "score": ..., "metadata": {...}}, ...]
        """
        results = self._client.query_points(
            collection_name=config.QDRANT_COLLECTION,
            query=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        formatted = []
        for point in results.points:
            payload = point.payload or {}
            formatted.append({
                "text": payload.get("text", ""),
                "score": float(point.score),
                "metadata": {k: v for k, v in payload.items() if k != "text"},
            })
        return formatted

    def close(self):
        self._client.close()
