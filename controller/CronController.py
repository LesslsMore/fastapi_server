import logging

from fastapi import APIRouter, Query

from model.system.virtual_object import FilmCronVo
from utils.get_scheduler import SchedulerUtil, generate_id
from utils.response_util import ResponseUtil

CronController = APIRouter(prefix='/cron')


@CronController.get("/list")
def FilmCronTaskList():
    job_list = SchedulerUtil.list_scheduler_job()
    f_list = []
    for job in job_list:
        f = FilmCronVo(id=job.id, remark=job.name, next=str(job.next_run_time), time=job.args[0], ids=job.args[1])
        f_list.append(f)
    return ResponseUtil.success(data=f_list, msg="影视源站点信息获取成功")


@CronController.get("/find")
def GetFilmCronTask(id: str = Query(..., description="资源站标识")):
    job = SchedulerUtil.get_scheduler_job(id)
    f = FilmCronVo(id=job.id, remark=job.name, next=str(job.next_run_time), time=job.args[0], ids=job.args[1])
    return ResponseUtil.success(data=f, msg="原站点详情信息查找成功")


@CronController.post("/update")
def FilmCronUpdate(vo: FilmCronVo):
    SchedulerUtil.add_scheduler_job(vo.id, vo.remark, vo.time, vo.ids, vo.spec)
    return ResponseUtil.success(msg="更新成功")


@CronController.post("/change")
def ChangeTaskState(vo: FilmCronVo):
    SchedulerUtil.add_scheduler_job(vo.id, vo.remark, vo.time, vo.ids, vo.spec)
    return ResponseUtil.success(msg="更新成功")


@CronController.get("/del")
def DelFilmCron(id: str = Query(..., description="资源站标识")):
    SchedulerUtil.remove_scheduler_job(id)
    return ResponseUtil.success(msg="删除成功")


@CronController.post("/add")
def FilmCronAdd(vo: FilmCronVo):
    job_id = generate_id(vo.ids, vo.time, vo.spec)
    SchedulerUtil.add_scheduler_job(job_id, vo.remark, vo.time, vo.ids, vo.spec)
    return ResponseUtil.success(data=vo, msg="添加成功")

