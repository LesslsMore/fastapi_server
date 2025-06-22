from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from typing import Union

from plugin.db import pg_engine
from service.spider_logic import SpiderLogic
from utils.log_util import logger

job_stores = {
    'default': SQLAlchemyJobStore(engine=pg_engine)
}

scheduler = AsyncIOScheduler()
scheduler.configure(jobstores=job_stores)


# 重写Cron定时
class MyCronTrigger(CronTrigger):
    @classmethod
    def from_crontab(cls, expr: str, timezone=None):
        values = expr.split()
        if len(values) != 6 and len(values) != 7:
            raise ValueError('Wrong number of fields; got {}, expected 6 or 7'.format(len(values)))

        second = values[0]
        minute = values[1]
        hour = values[2]
        if '?' in values[3]:
            day = None
        elif 'L' in values[5]:
            day = f"last {values[5].replace('L', '')}"
        elif 'W' in values[3]:
            day = cls.__find_recent_workday(int(values[3].split('W')[0]))
        else:
            day = values[3].replace('L', 'last')
        month = values[4]
        if '?' in values[5] or 'L' in values[5]:
            week = None
        elif '#' in values[5]:
            week = int(values[5].split('#')[1])
        else:
            week = values[5]
        if '#' in values[5]:
            day_of_week = int(values[5].split('#')[0]) - 1
        else:
            day_of_week = None
        year = values[6] if len(values) == 7 else None
        return cls(
            second=second,
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            week=week,
            day_of_week=day_of_week,
            year=year,
            timezone=timezone,
        )

    @classmethod
    def __find_recent_workday(cls, day: int):
        now = datetime.now()
        date = datetime(now.year, now.month, day)
        if date.weekday() < 5:
            return date.day
        else:
            diff = 1
            while True:
                previous_day = date - timedelta(days=diff)
                if previous_day.weekday() < 5:
                    return previous_day.day
                else:
                    diff += 1


class SchedulerUtil:
    """
    定时任务相关方法
    """

    @classmethod
    async def init_system_scheduler(cls):
        """
        应用启动时初始化定时任务

        :return:
        """
        logger.info('开始启动定时任务...')
        scheduler.start()
        logger.info('系统初始定时任务加载成功')

    @classmethod
    async def close_system_scheduler(cls):
        """
        应用关闭时关闭定时任务

        :return:
        """
        scheduler.shutdown()
        logger.info('关闭定时任务成功')

    @classmethod
    def get_scheduler_job(cls, job_id: Union[str, int]):
        """
        根据任务id获取任务对象

        :param job_id: 任务id
        :return: 任务对象
        """
        query_job = scheduler.get_job(job_id=str(job_id))

        return query_job

    @classmethod
    def add_scheduler_job(cls, job_id, job_name, time, ids, cron_expression):
        """
        根据输入的任务对象信息添加任务

        :param job_info: 任务对象信息
        :return:
        """
        # job_func = eval(job_info.invoke_target)
        # job_executor = job_info.job_executor
        # if iscoroutinefunction(job_func):
        #     job_executor = 'default'
        scheduler.add_job(
            # func=eval(job_info.invoke_target),
            func=SpiderLogic.batch_collect,
            trigger=MyCronTrigger.from_crontab(cron_expression),
            args=(time, ids),
            # kwargs=json.loads(job_info.job_kwargs) if job_info.job_kwargs else None,
            id=str(job_id),
            name=job_name,
            replace_existing=True,
            # misfire_grace_time=1000000000000 if job_info.misfire_policy == '3' else None,
            # coalesce=True if job_info.misfire_policy == '2' else False,
            # max_instances=3 if job_info.concurrent == '0' else 1,
            # jobstore=job_info.job_group,
            # executor=job_executor,
        )

    @classmethod
    def remove_scheduler_job(cls, job_id: Union[str, int]):
        """
        根据任务id移除任务

        :param job_id: 任务id
        :return:
        """
        query_job = cls.get_scheduler_job(job_id=job_id)
        if query_job:
            scheduler.remove_job(job_id=str(job_id))

    @classmethod
    def get_scheduler_job(cls, job_id: Union[str, int]):
        """
        根据任务id获取任务对象

        :param job_id: 任务id
        :return: 任务对象
        """
        query_job = scheduler.get_job(job_id=str(job_id))

        return query_job

    @classmethod
    def list_scheduler_job(cls):
        """
        根据任务id获取任务对象

        :param job_id: 任务id
        :return: 任务对象
        """
        query_job = scheduler.get_jobs()

        return query_job


import hashlib
from typing import List


def generate_id(ids: List[str], time: int, spec: str) -> str:
    # 将参数拼接成一个字符串
    input_str = f"{ids}{time}{spec}"

    # 使用 MD5 生成哈希值
    md5_hash = hashlib.md5(input_str.encode("utf-8")).hexdigest()

    return md5_hash
