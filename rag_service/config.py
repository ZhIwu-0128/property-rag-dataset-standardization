"""
RAG 模块配置 — 所有可调参数集中管理

【说明】
本文件为公开版本，所有连接信息已替换为占位符。
部署时需根据实际环境填写地址和 Key，也可通过环境变量覆盖。

【环境变量优先级 > 代码默认值，适合容器化部署】
"""

import os

# ============================================================
# 一、线程池配置
# ============================================================
EMBEDDING_THREAD_COUNT = int(os.getenv("EMBEDDING_THREAD_COUNT", "4"))
RERANK_THREAD_COUNT   = int(os.getenv("RERANK_THREAD_COUNT", "4"))
QUEUE_MAX_SIZE         = int(os.getenv("QUEUE_MAX_SIZE", "1000"))

# ============================================================
# 二、推理服务器配置 (OpenAI v1 API)
# ============================================================
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "http://<IP>:<PORT>/v1/embeddings")
RERANK_API_URL    = os.getenv("RERANK_API_URL",    "http://<IP>:<PORT>/v1/rerank")
EMBEDDING_MODEL   = os.getenv("EMBEDDING_MODEL",   "qwen3-embedding-4b")
RERANK_MODEL      = os.getenv("RERANK_MODEL",      "qwen3-reranker-4b")
API_KEY           = os.getenv("API_KEY",           "<YOUR_API_KEY>")
INFERENCE_TIMEOUT = int(os.getenv("INFERENCE_TIMEOUT", "30"))
MAX_RETRIES       = int(os.getenv("MAX_RETRIES", "2"))

# ============================================================
# 三、Qdrant 向量数据库配置
# ============================================================
QDRANT_HOST     = os.getenv("QDRANT_HOST",     "127.0.0.1")
QDRANT_PORT     = int(os.getenv("QDRANT_PORT", "6334"))
QDRANT_API_KEY  = os.getenv("QDRANT_API_KEY",  "<YOUR_QDRANT_KEY>")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "property_rag_train_v1_1")
QDRANT_TIMEOUT  = int(os.getenv("QDRANT_TIMEOUT", "10"))

# ============================================================
# 四、RAG 检索参数
# ============================================================
TOP_K_RETRIEVAL = int(os.getenv("TOP_K_RETRIEVAL", "100"))
TOP_N_RERANK    = int(os.getenv("TOP_N_RERANK",    "10"))

# ============================================================
# 五、日志配置
# ============================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
