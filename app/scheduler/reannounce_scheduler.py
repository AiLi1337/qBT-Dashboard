from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
    from apscheduler.triggers.interval import IntervalTrigger  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - exercised indirectly in local fallback
    AsyncIOScheduler = None
    IntervalTrigger = None

from app.domain import QBInstance
from app.services import QBInstanceService

_logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _FallbackJob:
    id: str
    func: object
    args: list[object]
    interval_minutes: int
    task: asyncio.Task | None = None


class _FallbackAsyncScheduler:
    def __init__(self) -> None:
        self.running = False
        self._jobs: dict[str, _FallbackJob] = {}

    def start(self) -> None:
        self.running = True
        for job in self._jobs.values():
            self._start_job(job)

    def shutdown(self, wait: bool = False) -> None:
        self.running = False
        for job in list(self._jobs.values()):
            self._cancel_job(job, wait=wait)

    def get_jobs(self) -> list[_FallbackJob]:
        return list(self._jobs.values())

    def get_job(self, job_id: str) -> _FallbackJob | None:
        return self._jobs.get(job_id)

    def remove_job(self, job_id: str) -> None:
        job = self._jobs.pop(job_id, None)
        if job is not None:
            self._cancel_job(job)

    def add_job(
        self,
        func,
        trigger,
        args: list[object],
        id: str,
        replace_existing: bool,
        coalesce: bool,
        max_instances: int,
    ) -> None:
        if replace_existing and id in self._jobs:
            self.remove_job(id)
        interval_minutes = getattr(trigger, "minutes", 60)
        job = _FallbackJob(id=id, func=func, args=args, interval_minutes=interval_minutes)
        self._jobs[id] = job
        if self.running:
            self._start_job(job)

    def _start_job(self, job: _FallbackJob) -> None:
        if job.task is not None and not job.task.done():
            return
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        job.task = loop.create_task(self._run_job(job))

    async def _run_job(self, job: _FallbackJob) -> None:
        # ponytail: first run immediately, then sleep between iterations
        while self.running and job.id in self._jobs:
            try:
                await job.func(*job.args)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                _logger.error("Scheduler job %s failed: %s", job.id, exc)
            if not self.running or job.id not in self._jobs:
                break
            await asyncio.sleep(job.interval_minutes * 60)

    @staticmethod
    def _cancel_job(job: _FallbackJob, wait: bool = False) -> None:
        if job.task is not None and not job.task.done():
            job.task.cancel()


class _FallbackIntervalTrigger:
    def __init__(self, minutes: int) -> None:
        self.minutes = minutes


class ReannounceScheduler:
    def __init__(self, service: QBInstanceService) -> None:
        self.service = service
        if AsyncIOScheduler is None:
            self.scheduler = _FallbackAsyncScheduler()
            self._trigger_factory = _FallbackIntervalTrigger
        else:
            self.scheduler = AsyncIOScheduler(timezone="UTC")
            self._trigger_factory = IntervalTrigger

    def start(self) -> None:
        if not self.scheduler.running:
            self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)

    def sync_instances(self, instances: list[QBInstance]) -> None:
        expected_ids = {self.job_id(item.id) for item in instances if self._should_schedule(item)}
        for job in list(self.scheduler.get_jobs()):
            if job.id not in expected_ids:
                self.scheduler.remove_job(job.id)
        for instance in instances:
            self.upsert_instance(instance)

    def upsert_instance(self, instance: QBInstance) -> None:
        job_id = self.job_id(instance.id)
        if not self._should_schedule(instance):
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
            return
        self.scheduler.add_job(
            self.service.run_reannounce,
            trigger=self._trigger_factory(minutes=instance.interval_minutes),
            args=[instance.id, "scheduled"],
            id=job_id,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

    @staticmethod
    def _should_schedule(instance: QBInstance) -> bool:
        return instance.enabled and instance.reannounce_enabled

    @staticmethod
    def job_id(instance_id: int) -> str:
        return f"qb-instance-{instance_id}"
