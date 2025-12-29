"""
任务管理器 - 支持 Redis 分布式存储
适用于微信云托管等 Serverless 多实例环境
"""

import os
import json
from typing import Dict, Optional
from datetime import datetime

from app.models import ConvertTask, TaskState, Category

# 尝试导入 redis
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ redis 库未安装，使用内存存储（不支持多实例）")


class RedisTaskManager:
    """Redis 任务管理器 - 支持多实例/Serverless 部署"""

    def __init__(self, redis_url: str):
        self._redis = redis.from_url(redis_url, decode_responses=True)
        self._prefix = "converteasy:task:"
        self._ttl = 24 * 60 * 60  # 24小时自动过期
        print("✅ Redis 任务管理器已初始化")

    def _task_to_dict(self, task: ConvertTask) -> dict:
        """将任务对象转换为字典"""
        return {
            "id": task.id,
            "state": task.state.value,
            "category": task.category.value,
            "target": task.target,
            "source": task.source,
            "input_path": task.input_path,
            "output_path": task.output_path,
            "original_filename": task.original_filename,
            "url": task.url,
            "download_url": task.download_url,
            "preview_url": task.preview_url,
            "error": task.error,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        }

    def _dict_to_task(self, data: dict) -> ConvertTask:
        """将字典转换为任务对象"""
        return ConvertTask(
            id=data["id"],
            state=TaskState(data["state"]),
            category=Category(data["category"]),
            target=data["target"],
            source=data.get("source"),
            input_path=data.get("input_path"),
            output_path=data.get("output_path"),
            original_filename=data.get("original_filename"),
            url=data.get("url"),
            download_url=data.get("download_url"),
            preview_url=data.get("preview_url"),
            error=data.get("error"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.now()
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else datetime.now()
            ),
        )

    def create_task(self, task: ConvertTask) -> None:
        """创建任务"""
        key = f"{self._prefix}{task.id}"
        data = json.dumps(self._task_to_dict(task), ensure_ascii=False)
        self._redis.setex(key, self._ttl, data)

    def get_task(self, task_id: str) -> Optional[ConvertTask]:
        """获取任务"""
        key = f"{self._prefix}{task_id}"
        data = self._redis.get(key)
        if data:
            return self._dict_to_task(json.loads(data))
        return None

    def update_task(self, task: ConvertTask) -> None:
        """更新任务"""
        task.updated_at = datetime.now()
        key = f"{self._prefix}{task.id}"
        # 获取剩余TTL，保持原有过期时间
        ttl = self._redis.ttl(key)
        if ttl < 0:
            ttl = self._ttl
        data = json.dumps(self._task_to_dict(task), ensure_ascii=False)
        self._redis.setex(key, ttl, data)

    def delete_task(self, task_id: str) -> None:
        """删除任务"""
        key = f"{self._prefix}{task_id}"
        self._redis.delete(key)

    def get_all_tasks(self) -> Dict[str, ConvertTask]:
        """获取所有任务"""
        tasks = {}
        pattern = f"{self._prefix}*"
        for key in self._redis.scan_iter(pattern, count=100):
            data = self._redis.get(key)
            if data:
                task = self._dict_to_task(json.loads(data))
                tasks[task.id] = task
        return tasks

    def get_expired_tasks(self, expire_time: int) -> list:
        """获取过期任务（Redis 自动过期，返回空列表）"""
        return []

    def get_stats(self) -> dict:
        """获取任务统计"""
        tasks = list(self.get_all_tasks().values())
        return {
            "total": len(tasks),
            "queued": sum(1 for t in tasks if t.state == TaskState.QUEUED),
            "processing": sum(1 for t in tasks if t.state == TaskState.PROCESSING),
            "finished": sum(1 for t in tasks if t.state == TaskState.FINISHED),
            "error": sum(1 for t in tasks if t.state == TaskState.ERROR),
        }


class MemoryTaskManager:
    """内存任务管理器 - 仅支持单实例（回退方案）"""

    def __init__(self):
        self._tasks: Dict[str, ConvertTask] = {}
        print("⚠️ 使用内存任务管理器（仅支持单实例部署）")

    def create_task(self, task: ConvertTask) -> None:
        """创建任务"""
        self._tasks[task.id] = task

    def get_task(self, task_id: str) -> Optional[ConvertTask]:
        """获取任务"""
        return self._tasks.get(task_id)

    def update_task(self, task: ConvertTask) -> None:
        """更新任务"""
        task.updated_at = datetime.now()
        self._tasks[task.id] = task

    def delete_task(self, task_id: str) -> None:
        """删除任务"""
        if task_id in self._tasks:
            del self._tasks[task_id]

    def get_all_tasks(self) -> Dict[str, ConvertTask]:
        """获取所有任务"""
        return self._tasks.copy()

    def get_expired_tasks(self, expire_time: int) -> list[ConvertTask]:
        """获取过期任务"""
        now = datetime.now()
        expired = []
        for task in self._tasks.values():
            if (now - task.created_at).total_seconds() > expire_time:
                expired.append(task)
        return expired

    def get_stats(self) -> dict:
        """获取任务统计"""
        tasks = list(self._tasks.values())
        return {
            "total": len(tasks),
            "queued": sum(1 for t in tasks if t.state == TaskState.QUEUED),
            "processing": sum(1 for t in tasks if t.state == TaskState.PROCESSING),
            "finished": sum(1 for t in tasks if t.state == TaskState.FINISHED),
            "error": sum(1 for t in tasks if t.state == TaskState.ERROR),
        }


def create_task_manager():
    """
    创建任务管理器 - 根据环境自动选择

    优先使用 Redis（支持多实例），如果 Redis 不可用则回退到内存存储

    环境变量:
        REDIS_URL: Redis 连接地址，例如 redis://user:password@host:port/db
    """
    redis_url = os.getenv("REDIS_URL")

    if redis_url and REDIS_AVAILABLE:
        try:
            manager = RedisTaskManager(redis_url)
            # 测试连接
            manager._redis.ping()
            print("✅ Redis 连接成功")
            return manager
        except Exception as e:
            print(f"⚠️ Redis 连接失败: {e}，回退到内存存储")
    elif redis_url and not REDIS_AVAILABLE:
        print("⚠️ 已配置 REDIS_URL 但 redis 库未安装，请运行: pip install redis")

    return MemoryTaskManager()


# 全局任务管理器实例
task_manager = create_task_manager()
