"""
Rerank 工作线程池

与EmbeddingWorkerPool架构相同，区别在于处理的是"query + 候选文档 → 精排打分"。

线程数 = config.RERANK_THREAD_COUNT (默认4)

【数据安全】query和文档内容仅在内存中流转，推理请求走内网HTTP。
"""

import logging
import queue
import threading
from concurrent.futures import Future

import config
from models import RerankTask

logger = logging.getLogger(__name__)


class RerankWorkerPool:

    def __init__(self, inference_client):
        self._inference = inference_client
        self._queue: queue.Queue = queue.Queue(maxsize=config.QUEUE_MAX_SIZE)
        self._threads: list[threading.Thread] = []
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        for i in range(config.RERANK_THREAD_COUNT):
            t = threading.Thread(
                target=self._worker_loop,
                name=f"rerank-worker-{i}",
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        logger.info("Rerank线程池启动完成，线程数=%d", config.RERANK_THREAD_COUNT)

    def submit(self, query: str, documents: list[str]) -> Future:
        """提交重排序任务，返回Future"""
        future = Future()
        task = RerankTask(query=query, documents=documents, future=future)
        try:
            self._queue.put(task, block=False)
        except queue.Full:
            raise RuntimeError(f"Rerank队列已满(maxsize={config.QUEUE_MAX_SIZE})")
        return future

    def shutdown(self):
        if not self._running:
            return
        self._running = False
        for _ in range(len(self._threads)):
            self._queue.put(None)
        for t in self._threads:
            t.join(timeout=10)
        logger.info("Rerank线程池已关闭")

    def _worker_loop(self):
        while self._running:
            task = self._queue.get()
            if task is None:
                break
            try:
                self._process_task(task)
            except Exception as e:
                logger.error("Rerank任务处理失败: %s", e)
                task.future.set_exception(e)
            finally:
                self._queue.task_done()

    def _process_task(self, task: RerankTask):
        scored = self._inference.rerank(task.query, task.documents)
        top_results = scored[:config.TOP_N_RERANK]
        results = []
        for idx, score in top_results:
            results.append({
                "text": task.documents[idx],
                "score": score,
                "original_index": idx,
            })
        task.future.set_result(results)
