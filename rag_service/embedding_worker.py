"""
Embedding 工作线程池

生产者-消费者模式：N个后台线程死循环从队列取任务 → 推理服务器取向量 → Qdrant检索 → 结果放回Future。

线程数 = config.EMBEDDING_THREAD_COUNT (默认4)

【数据安全】全部数据在队列、Future、变量间流转，纯内存操作。
"""

import logging
import queue
import threading
from concurrent.futures import Future

import config
from models import EmbeddingTask

logger = logging.getLogger(__name__)


class EmbeddingWorkerPool:

    def __init__(self, inference_client, qdrant_client):
        self._inference = inference_client
        self._qdrant = qdrant_client
        self._queue: queue.Queue = queue.Queue(maxsize=config.QUEUE_MAX_SIZE)
        self._threads: list[threading.Thread] = []
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        for i in range(config.EMBEDDING_THREAD_COUNT):
            t = threading.Thread(
                target=self._worker_loop,
                name=f"embedding-worker-{i}",
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        logger.info("Embedding线程池启动完成，线程数=%d", config.EMBEDDING_THREAD_COUNT)

    def submit(self, query: str) -> Future:
        """提交查询任务，返回Future用于获取结果"""
        future = Future()
        task = EmbeddingTask(query=query, future=future)
        try:
            self._queue.put(task, block=False)
        except queue.Full:
            raise RuntimeError(f"Embedding队列已满(maxsize={config.QUEUE_MAX_SIZE})")
        return future

    def shutdown(self):
        """优雅关闭：发哨兵信号让线程退出"""
        if not self._running:
            return
        self._running = False
        for _ in range(len(self._threads)):
            self._queue.put(None)
        for t in self._threads:
            t.join(timeout=10)
        logger.info("Embedding线程池已关闭")

    def _worker_loop(self):
        while self._running:
            task = self._queue.get()
            if task is None:
                break
            try:
                self._process_task(task)
            except Exception as e:
                logger.error("Embedding任务处理失败: %s", e)
                task.future.set_exception(e)
            finally:
                self._queue.task_done()

    def _process_task(self, task: EmbeddingTask):
        vector = self._inference.get_embedding(task.query)
        results = self._qdrant.search(query_vector=vector, top_k=config.TOP_K_RETRIEVAL)
        task.future.set_result(results)
