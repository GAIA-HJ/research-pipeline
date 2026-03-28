import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from orchestrator import PipelineOrchestrator
from config import Config

log = logging.getLogger("scheduler")


async def weekly_job():
    log.info("Weekly job triggered")
    config = Config()
    orch = PipelineOrchestrator(config)
    await orch.run_cycle()


def start():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    scheduler = AsyncIOScheduler()
    # Every Saturday at 10:00 AM Riyadh time (UTC+3 = 07:00 UTC)
    scheduler.add_job(weekly_job, "cron", day_of_week="sat", hour=7, minute=0)
    log.info("Scheduler started. Next run: Saturday 10:00 AM Riyadh time")
    scheduler.start()
    asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    start()
