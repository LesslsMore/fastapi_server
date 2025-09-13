from fastapi import FastAPI

from anime.controller import router as anime_controller
from controller.CronController import CronController
from controller.collect_controller import collectController
from controller.film_controller import filmController
from controller.index_controller import indexController
from controller.manage_controller import manageController
from controller.spider_controller import spiderController
from controller.user_controller import userController


def app_router(app: FastAPI):
    app.include_router(prefix='/api', router=anime_controller)
    app.include_router(prefix='/api', router=indexController)
    app.include_router(prefix='/api', router=userController)
    manageController.include_router(collectController)
    manageController.include_router(CronController)
    manageController.include_router(spiderController)
    manageController.include_router(userController)
    manageController.include_router(filmController)
    app.include_router(prefix='/api', router=manageController)
