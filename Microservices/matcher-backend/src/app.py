import json
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.uof import PostgresUnitOfWork
import src.service_layer as service
import logging
import requests
import os
import asyncio
import asyncpg
import time
from src.config import DB_HOST, DB_NAME, DB_USER, DB_PASS

logger = logging.getLogger("backend-matcher")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s|%(levelname)s| %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

pool = None

fastapi_app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:8888",
    "http://localhost:8081",
    "http://127.0.0.1:8081"
]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


####################################################################################################
# FastAPI utils


@fastapi_app.on_event("startup")
async def startup_event():
    logger.info("App started.")
    global pool
    if pool is None:
        config = {
            "user": DB_USER,
            "database": DB_NAME,
            "password": DB_PASS,
            "host": DB_HOST,
            "min_size": 5,
            "max_size": 80,
        }
        pool = await asyncpg.create_pool(**config)
        logger.info("Connection pool created.")


@fastapi_app.on_event("shutdown")
async def shutdown_event():
    global pool
    if pool:
        await pool.close()
        pool = None
        logger.info("Connection pool removed.")
    logger.info("App stopped.")


async def get_uof():
    return PostgresUnitOfWork(pool)


####################################################################################################
# source


@fastapi_app.get("/source/")
async def get_sources(source_id: Optional[int] = None,
                      source_name: Optional[int] = None,
                      uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all sources
    Format [{source_id, source_name, timestamp}]
    :param source_name:
    :param source_id:
    :return:
    """
    data = {'source_id': source_id,
            'source_name': source_name}

    # start_time_endpoint = time.time()
    response = await service.get_sources(uof, **data)
    # end_time_endpoint = time.time()
    # logger.info(f'Time taken for endpoint: {end_time_endpoint - start_time_endpoint} seconds')
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/source/")
async def create_source(request: Request,
                        uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Добавляет новые источники в БД
    :request:{"name": bk1, "url": www.link1}
    """
    data = await request.json()
    result = await service.add_source(uof, **data)
    if result.get("status_code") != 200:
        return HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.put("/source/")
async def modify_source(request: Request,
                        uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Обновляет информацию об источниках в БД по названиям
    :request:{"id": id1, "name": bk1, "url": www.link1}
    """
    data = await request.json()
    result = await service.modify_source(uof, **data)
    if result.get("status_code") != 200:
        return HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.delete("/source/")
async def delete_source(request: Request,
                        uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Удаляет источник по id или имени
    :request: {"name": "name"} / {"id": "new id"}
    :return: OK
    """
    data = await request.json()
    result = await service.delete_source(uof, **data)
    if result.get("status_code") != 200:
        return HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.get("/source/{source_id}")
async def get_source_by_id(source_id: int,
                           uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Принимает id источника и возвращает json с ег названием и ссылкой на него
    """
    # return {"id": 0, "name": "bk1", "link": "www.link1"}
    result = await service.get_source_by_id(uof, source_id=source_id)
    if result.get("status_code") != 200:
        return HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


#####################################################################################################################
# types


@fastapi_app.get("/types/")
async def get_sport_types(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all sport types
    """
    response = await service.get_sport_types(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/types/")
async def create_sport_type(request: Request,
                            uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Create the sport type
    :param request: {"name": "some_name"},
    """
    data = await request.json()
    response = await service.create_sport_type(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# config


@fastapi_app.get("/config/")
async def get_configuration(default: bool = False,
                            source1_id: Optional[int] = None,
                            source2_id: Optional[int] = None,
                            uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return config files for particular pair or default ones
    :param default:
    :param source1_id:
    :param source2_id:
    :return:
    """
    data = {'default': default, 'source1_id': source1_id, 'source2_id': source2_id}
    response = await service.get_config(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/config/")
async def create_configuration(request: Request,
                               uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    :param request: {source1_id, source2_id, params},
    :return:
    """
    data = await request.json()
    response = await service.create_modify_config(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.delete("/config/")
async def delete_configuration(request: Request,
                               uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    :param request: {source1_id, source2_id, param_id, sport_id},
    :return:
    """
    data = await request.json()
    response = await service.delete_config(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# tasks


@fastapi_app.get("/tasks/")
async def get_tasks(source1_id: int, source2_id: int, uof: PostgresUnitOfWork = Depends(get_uof)):
    response = await service.get_tasks_by_sources(uof, source1_id, source2_id)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# pairs


@fastapi_app.get("/pairs/")
async def get_results(source1_id: Optional[int] = None,
                      source2_id: Optional[int] = None,
                      task_id: Optional[int] = None,
                      started_at: Optional[float] = None,
                      finished_at: Optional[float] = None,
                      uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    :param task_id:
    :param started_at:
    :param finished_at:
    :param source1_id:
    :param source2_id:
    :return:
    """
    data = {
        'source1_id': source1_id,
        'source2_id': source2_id,
        'task_id': task_id,
        'started_at': started_at,
        'finished_at': finished_at
    }
    response = await service.get_results(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/pairs/")
async def create_results(request: Request,
                         uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    {run_id: List[res]}, где res
           res = {
                      'event1': json,
                      'event2':json,
                      'is_match': True, (потому что чел вручную нашел пару событий)
                      'mismatch':True  (потому что он ручной, от пользователя)
                     }

    :param request:
    :return:
    """
    data = await request.json()
    response = await service.create_results(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.put("/pairs/")
async def modify_results(request: Request,
                         uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    {'results'[  {result_id: int,
    'mismatch':False (потому что этот результат найден системой, но уже просмотрен пользователем.
    'is_match': True/False (в зависимости что нажмет юзер галочку или крестик)
    },
    ...
    ]}
    :param request:  [{'result_id', 'modified_fild}]
    :return:
    """
    data = await request.json()
    response = await service.modify_results(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.delete("/pairs/")
async def delete_results(request: Request,
                         uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Delete result
    :param request: {"results": [result_ids]}
    :return:
    """
    data = await request.json()
    response = await service.delete_results(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# User


@fastapi_app.get("/users/")
async def get_user(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all users

    :return:
    """
    response = await service.get_user(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/users/")
async def create_users(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Добавляет нового пользователя в БД
    :request:{"name": bk1, "permission_id": id}
    """
    data = await request.json()
    result = await service.add_user(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.put("/users/")
async def modify_user(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Обновляет информацию об пользователе в БД
    :request:{"id": id1, "name": bk1, "permission_id": id}
    """
    data = await request.json()
    result = await service.modify_user(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.delete("/users/")
async def delete_user(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Удаляет пользователя по id или имени
    :return: OK
    """
    data = await request.json()
    result = await service.delete_user(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.get("/users/{user_id}")
async def get_user_by_id(user_id: int, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Принимает id источника и возвращает json с ег названием и ссылкой на него
    """
    # return {"id": 0, "name": "bk1", "link": "www.link1"}
    result = await service.get_user_by_id(uof, user_id=user_id)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


####################################################################################################
# Permissions

@fastapi_app.get("/permission/")
async def get_permission(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all permission

    :return:
    """
    response = await service.get_permission(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/permission/")
async def create_permission(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Добавляет новую роль в БД
    :request:{"type": bk1}
    """
    data = await request.json()
    result = await service.add_permission(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.put("/permission/")
async def modify_permission(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Обновляет информацию о роли в БД
    :request:{"id": id1, "type": type}
    """
    data = await request.json()
    result = await service.modify_permission(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.delete("/permission/")
async def delete_permission(permission_id, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Удаляет роль по id
    :request: {"name": "name"} / {"id": "new id"}
    :return: OK
    """
    data = {"id": permission_id}
    result = await service.delete_permission(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.get("/permission/{permission_id}")
async def get_permission_by_id(permission_id: int, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Принимает id роли и возвращает json с ее названием
    """
    # return {"id": 0, "name": "bk1", "link": "www.link1"}
    result = await service.get_permission_by_id(uof, permission_id=permission_id)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


####################################################################################################
# Parameters

@fastapi_app.get("/parameter/")
async def get_parameter(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all parameter

    :return:
    """
    response = await service.get_parameters(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/parameter/")
async def create_parameter(request: Request,
                           uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Добавляет новый параметр в БД
    :request:{"name": bk1, "name": str}
    """
    data = await request.json()
    result = await service.add_parameter(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.put("/parameter/")
async def modify_parameter(request: Request,
                           uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Обновляет информацию о параметре в БД
    :request:{"id": id1, "name": name}
    """
    data = await request.json()
    result = await service.modify_parameter(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.delete("/parameter/")
async def delete_parameter(parameter_id,
                           uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Удаляет параметр по id
    :request: {"name": "name"} / {"id": "new id"}
    :return: OK
    """
    data = {"id": int(parameter_id)}
    result = await service.delete_parameter(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.get("/parameter/{parameter_id}")
async def get_parameter_by_id(parameter_id: int,
                              uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Принимает id параметра и возвращает json с ее названием
    """
    # return {"id": 0, "name": "bk1", "link": "www.link1"}
    result = await service.get_parameter_by_id(uof, parameter_id=parameter_id)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


#####################################################################################################################
# Statuses

@fastapi_app.get("/status/")
async def get_status(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all statuses

    :return:
    """
    response = await service.get_statuses(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/status/")
async def create_status(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Add new status, return id
    :request:{"status": status}
    :response: id
    """
    data = await request.json()
    result = await service.add_status(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.put("/status/")
async def modify_status(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        modify status
    :request:{"id": id, "status": status}
    """
    data = await request.json()
    result = await service.modify_status(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.delete("/status/")
async def delete_status(status_id, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        delete status bu id
    :request: name/id
    :return: OK
    """
    data = {"id": status_id}
    result = await service.delete_status(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@fastapi_app.get("/status/{status_id}")
async def get_status_by_id(status_id: int, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        return status by id
    """
    # return {"id": 0, "name": "bk1", "link": "www.link1"}
    result = await service.get_status_by_id(uof, status_id=status_id)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


#####################################################################################################################
# endpoints for matcher

@fastapi_app.post("/start_task/")
async def start_task(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Create task and corresponding runs for each sport_type
    :param request: {source1_id, source2_id, started_at, sport_ids, referent_task}
    """
    data = await request.json()
    response = await service.start_task(uof, **json.loads(data))
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/finish_run/")
async def finish_run(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    finish run and save results
    :param request: {
       run_id: int,
       task_id: int,
       num_events: int,
       runtime: float,
       pairs: List[Tuple2(json, json)],
       updated_at: timestamp
    }
    """
    data = await request.json()
    response = await service.finish_run(uof, **json.loads(data))
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/test_task/")
async def test_task(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    :param request:{
         task_id: int,
         parameters: Dict[]
    }
    :response:
    """
    data = await request.json()
    response = await service.run_test_task(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response

