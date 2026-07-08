"""
数据模型定义

所有数据模型都在内存中实例化，请求结束后被Python垃圾回收。
"""

from typing import Any, Optional
from pydantic import BaseModel, Field


class EmbeddingQueryRequest(BaseModel):
    """单独向量检索请求"""
    query: str = Field(..., description="查询文本")
    top_k: Optional[int] = Field(default=None, description="返回数量")


class RerankRequest(BaseModel):
    """单独重排序请求"""
    query: str = Field(..., description="查询文本")
    documents: list[str] = Field(..., description="待排序的文档列表")
    top_n: Optional[int] = Field(default=None, description="返回前N条")


class RAGQueryRequest(BaseModel):
    """完整RAG查询请求：embedding召回 + rerank精排"""
    query: str = Field(..., description="查询文本")
    top_k: Optional[int] = Field(default=None, description="向量检索候选数")
    top_n: Optional[int] = Field(default=None, description="重排序后返回数")


class SearchResult(BaseModel):
    """单条检索结果"""
    text: str = Field(..., description="文档文本内容")
    score: float = Field(..., description="相关性分数")
    metadata: Optional[dict[str, Any]] = Field(default=None, description="附加元信息")


class SearchResponse(BaseModel):
    """检索响应体"""
    results: list[SearchResult] = Field(..., description="检索结果列表")
    latency_ms: float = Field(..., description="总耗时(毫秒)")


class EmbeddingTask:
    """Embedding阶段的任务对象（内部流转用）"""
    def __init__(self, query: str, future: Any):
        self.query = query
        self.future = future


class RerankTask:
    """Rerank阶段的任务对象（内部流转用）"""
    def __init__(self, query: str, documents: list[str], future: Any):
        self.query = query
        self.documents = documents
        self.future = future
