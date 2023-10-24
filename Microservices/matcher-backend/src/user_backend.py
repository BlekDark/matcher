# FastAPI import
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi import APIRouter

# Project src import
from src.config import DB_HOST, DB_NAME, DB_USER, DB_PASS
from src.uof import PostgresUnitOfWork
import src.service_layer as service

# Utils import
import logging
import asyncpg
import asyncio
from typing import Optional


logger = logging.getLogger("backend-matcher")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s|%(levelname)s| %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


pool = None

router = APIRouter()
fastapi_app = FastAPI(title='User Backend FastApi', docs_url='/api/v1/docs', openapi_url='/api/v1/openapi.json', redoc_url='/api/v1/redocs',)
endpoint_lock = asyncio.Lock()

origins = [
    # DEV ORIGINS
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:4173",
    "http://127.0.0.1:8888",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    # PROD ORIGINS
    "https://77.50.186.230:443",
    "http://77.50.186.230:80",
    "http://77.50.186.230:32222",
]

# uncomment on dev
# fastapi_app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


####################################################################################################
# FastAPI utils


@router.on_event("startup")
async def startup_event():
    logger.removeHandler(logger.handlers[1])
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


@router.on_event("shutdown")
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


@router.get("/source/")
async def get_sources(source_id: Optional[int] = None,
                      source_name: Optional[int] = None,
                      uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all sources |\
    :return: [{source_id, source_name, source_url, timestamp}, ..]
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


@router.post("/source/")
async def create_source(request: Request,
                        uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Add new source in db |\
    :request:{"name": bk1, "url": www.link1}
    :return: id
    """
    data = await request.json()
    result = await service.add_source(uof, **data)
    if result.get("status_code") != 200:
        return HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.put("/source/")
async def modify_source(request: Request,
                        uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Modify information about a source in db |\
    :request:{"id": id1, "name": bk1, "url": www.link1}
    :return: True
    """
    data = await request.json()
    result = await service.modify_source(uof, **data)
    if result.get("status_code") != 200:
        return HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.delete("/source/")
async def delete_source(request: Request,
                        uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Delete source by id or name |\
    :request: {"name": name} / {"id": id}
    :return: True
    """
    data = await request.json()
    result = await service.delete_source(uof, **data)
    if result.get("status_code") != 200:
        return HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.get("/source/{source_id}")
async def get_source_by_id(source_id: int,
                           uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Return sources by id or name |\
    :return: {source_id, source_name, source_url}
    """
    result = await service.get_source_by_id(uof, source_id=source_id)
    if result.get("status_code") != 200:
        return HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


#####################################################################################################################
# types


@router.get("/types/")
async def get_sport_types(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all sport types |\
    :return: [{sport_id, sport_name, is_cyber}, ..]
    """
    response = await service.get_sport_types(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.post("/types/")
async def create_sport_type(request: Request,
                            uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Create the sport type |\
    :request: {"name": name} / {"id": id} |\
    :return: id
    """
    data = await request.json()
    response = await service.create_sport_type(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# config


@router.get("/config/")
async def get_configuration(default: bool = False,
                            source1_id: Optional[int] = None,
                            source2_id: Optional[int] = None,
                            uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return config files for particular pair or default ones |\
    :param default:
    :param source1_id:
    :param source2_id:
    """
    data = {'default': default, 'source1_id': source1_id, 'source2_id': source2_id}
    response = await service.get_config(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.post("/config/")
async def create_configuration(request: Request,
                               uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    add or modify config for 2 sources |\
    :request: {source1_id, source2_id, default},
    :return:
    """
    data = await request.json()
    response = await service.create_modify_config(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.delete("/config/")
async def delete_configuration(request: Request,
                               uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    :request: {source1_id, source2_id, param_id, sport_id},
    :return: True
    """
    data = await request.json()
    response = await service.delete_config(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# tasks


@router.get("/tasks/")
async def get_tasks(source1_id: int, source2_id: int, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Get all tasks |\
    :request: {source1_id, source2_id},
    :return:
    """
    response = await service.get_tasks_by_sources(uof, source1_id, source2_id)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# pairs


@router.get("/pairs/")
async def get_results(source1_id: Optional[int] = None,
                      source2_id: Optional[int] = None,
                      task_id: Optional[int] = None,
                      started_at: Optional[float] = None,
                      finished_at: Optional[float] = None,
                      uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Get all pairs by sources, time interval and task_id |\
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


@router.post("/pairs/")
async def create_results(request: Request,
                         uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Add pairs |\
    :request: {run_id: List[res]}, где res
           res = {
                      'event1': json,
                      'event2':json,
                      'is_match': True,
                      'mismatch':True
                     }

    |\
    :return: number of pairs added
    """
    data = await request.json()
    response = await service.create_results(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.put("/pairs/")
async def modify_results(request: Request,
                         uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Modify pairs |\
    :request: {'results'[  {result_id: int,
    'mismatch':False
    'is_match': True/False
    },
    ...
    ]} |\
    :return: number of pairs modify
    """
    data = await request.json()
    response = await service.modify_results(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.delete("/pairs/")
async def delete_results(request: Request,
                         uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Delete result |\
    :param request: {"results": [result_ids]} |\
    :return: number of pairs delete
    """
    data = await request.json()
    response = await service.delete_results(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# User


@router.get("/users/")
async def get_user(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all users

    :return:
    """
    response = await service.get_user(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.post("/users/")
async def create_users(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Add new user
    :request:{"name": bk1, "permission_id": id}
    :return: id
    """
    data = await request.json()
    result = await service.add_user(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.put("/users/")
async def modify_user(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        modify name or permission_id user
    :request:{"id": id, "name": name, "permission_id": id}
    :return: True
    """
    data = await request.json()
    result = await service.modify_user(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.delete("/users/")
async def delete_user(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Delete user by id or name
    :request:{"id": id} or {"name": name}
    :return: True
    """
    data = await request.json()
    result = await service.delete_user(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.get("/users/{user_id}")
async def get_user_by_id(user_id: int, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        get user by id
        :return:
    """
    result = await service.get_user_by_id(uof, user_id=user_id)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


####################################################################################################
# Permissions

@router.get("/permission/")
async def get_permission(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all permission
    :return:
    """
    response = await service.get_permission(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.post("/permission/")
async def create_permission(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Add new permission
    :request:{"type": bk1}
    :return: id
    """
    data = await request.json()
    result = await service.add_permission(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.put("/permission/")
async def modify_permission(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        modify permission
    :request:{"id": id1, "type": type}
    :return: True
    """
    data = await request.json()
    result = await service.modify_permission(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.delete("/permission/")
async def delete_permission(permission_id, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        delete permission by id
    :request: id |\
    :return: True
    """
    data = {"id": permission_id}
    result = await service.delete_permission(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.get("/permission/{permission_id}")
async def get_permission_by_id(permission_id: int, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        get permission by id
    :return:
    """
    result = await service.get_permission_by_id(uof, permission_id=permission_id)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


####################################################################################################
# Parameters

@router.get("/parameter/")
async def get_parameter(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all parameters
    :return:
    """
    response = await service.get_parameters(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.post("/parameter/")
async def create_parameter(request: Request,
                           uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        add new parameter
    :request:{"name": bk1, "name": str}
    :return: id
    """
    data = await request.json()
    result = await service.add_parameter(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.put("/parameter/")
async def modify_parameter(request: Request,
                           uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        modify parameter
    :request:{"id": id1, "name": name, "default_value": default_value}
    :return: True
    """
    data = await request.json()
    result = await service.modify_parameter(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.delete("/parameter/")
async def delete_parameter(parameter_id,
                           uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        delete parameter by id or name
    :request: {"name": name} / {"id": "id"}
    :return: True
    """
    data = {"id": int(parameter_id)}
    result = await service.delete_parameter(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.get("/parameter/{parameter_id}")
async def get_parameter_by_id(parameter_id: int,
                              uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        get parameter by id
    """
    result = await service.get_parameter_by_id(uof, parameter_id=parameter_id)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


#####################################################################################################################
# Statuses

@router.get("/status/")
async def get_status(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return all statuses
    :return:
    """
    response = await service.get_statuses(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.post("/status/")
async def create_status(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        Add new status, return id
    :request:{"status": status}
    :return: id
    """
    data = await request.json()
    result = await service.add_status(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.put("/status/")
async def modify_status(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        modify status
    :request:{"id": id, "status": status}
    :return: True
    """
    data = await request.json()
    result = await service.modify_status(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.delete("/status/")
async def delete_status(status_id, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        delete status bu id
    :request: name/id
    :return: True
    """
    data = {"id": status_id}
    result = await service.delete_status(uof, **data)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result


@router.get("/status/{status_id}")
async def get_status_by_id(status_id: int, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
        return status by id
    """
    result = await service.get_status_by_id(uof, status_id=status_id)
    if result.get("status_code") != 200:
        raise HTTPException(status_code=result.get("status_code"), detail=result.get("detail"))
    return result

#####################################################################################################################
# test_ task

@router.post("/test_task/")
async def test_task(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    sends data to the matcher
    :param request:{
         task_id: int,
         parameters: Dict[]
    } |\
    :response:
    """
    data = await request.json()
    response = await service.run_test_task(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# custom test_ matcher

# @router.get("/custom_match/")
# async def custom_match(unmatched: Optional[bool] = True, uof: PostgresUnitOfWork = Depends(get_uof)):
#     """
#     get results of quality check
#     :param unmatched Optional
#     :return: response
#     """
#
#     response = await service.get_custom_match_results(uof, unmatched)
#     if response.get("status_code") != 200:
#         raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
#     return response


# @router.post("/custom_match/")
# async def custom_match(request: Request, all_results: Optional[bool] = False, uof: PostgresUnitOfWork = Depends(get_uof)):
#     """
#     sends data to the test_ matcher
#     :param request Optional
#     {
#          {
#             sport: str,
#             event1: {
#                 team1: str,
#                 team2: str,
#                 league: str
#             },
#             event2: {
#                 team1: str,
#                 team2: str,
#                 league: str
#             },
#             is_cyber: bool
#         }
#     }
#     :return: response
#     """
#
#     try:
#         data = await request.json()
#     except ValueError:
#         data = None
#
#     response = await service.run_custom_match(uof, data, all_results)
#     if response.get("status_code") != 200:
#         raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
#     return response


@router.post("/custom_match_stable/")
async def custom_match_stable(request: Request, date: Optional[str] = '', uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Send data to the test_ matcher

    Args:
        request (Request, optional): Optional request body.
        date (str, optional): Optional date parameter.

    Request Body:
        [
            {
                date: str,
                data: [
                    {
                        "sport": str,
                        "event1": {
                                    "event_id": str(uuid4),
                                    "event_name": str,
                                    "league": str,
                                    "team1": str,
                                    "team2": str
                                    },
                        "event2": {
                                    "event_id": str(uuid4),
                                    "event_name": str,
                                    "league": str,
                                    "team1": str,
                                    "team2": str
                                    },
                        "is_cyber": int
                    },
                ]
            },
        ]

    Returns:
        response: The response.
    """

    try:
        data = await request.json()
    except ValueError:
        data = None

    if endpoint_lock.locked():
        return {
            'status_code': 200,
            'detail': "OK",
            'result': "Matcher is currently busy. Please try again later.."
        }

    async with endpoint_lock:
        response = await service.run_custom_match_stable(uof, data, date)
        if response.get("status_code") != 200:
            raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
        return response


@router.get("/custom_match_stable/")
async def custom_match_stable(date: Optional[str] = '', uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Get results of quality check

    Args:
        date (str, optional): Optional date parameter.

    Returns:
        response: The response.
    """

    response = await service.get_custom_match_results_stable(uof, date)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.post("/custom_match/")
async def custom_match(request: Request,
                       filename: Optional[str] = 'input_data.json',
                       date: Optional[str] = '',
                       uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Send data to the test_ matcher

    Args:
        filename (str, optional): uses 'input_data.json' as default.
        request (Request, optional): Optional request body.
        date (str, optional): Optional date parameter.

    Request Body:
        [
            {
                date: str,
                data: [
                    {
                        "sport": str,
                        "event1": {
                                    "event_id": str(uuid4),
                                    "event_name": str,
                                    "league": str,
                                    "team1": str,
                                    "team2": str
                                    },
                        "event2": {
                                    "event_id": str(uuid4),
                                    "event_name": str,
                                    "league": str,
                                    "team1": str,
                                    "team2": str
                                    },
                        "is_cyber": int
                    },
                ]
            },
        ]

    Returns:
        response: The response.
    """

    try:
        data = await request.json()
    except ValueError:
        data = None

    if endpoint_lock.locked():
        return {
            'status_code': 200,
            'detail': "OK",
            'result': "Matcher is currently busy. Please try again later.."
        }

    async with endpoint_lock:
        response = await service.run_custom_match(uof, filename, data, date, pool, without_crossed=False)
        if response.get("status_code") != 200:
            raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
        return response


@router.post("/remove_crosshairs/")
async def remove_crosshairs(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    remove crosshairs
    :param
    input.json, processed_data.json

    ...
    :return:
    resultForDel.json, input_data_without_crossed.json
    """

    response = await service.run_remove_crosshairs(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.post("/custom_match_without_crossed/")
async def custom_match_without_crossed(request: Request,
                       filename: Optional[str] = 'input_data_without_crossed.json',
                       date: Optional[str] = '',
                       uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Send data without crossed to the test_ matcher

    Args:
        filename (str, optional): uses 'input_data_without_crossed.json.json' as default.
        request (Request, optional): Optional request body.
        date (str, optional): Optional date parameter.
    Returns:
        response: The response.
    """

    try:
        data = await request.json()
    except ValueError:
        data = None

    if endpoint_lock.locked():
        return {
            'status_code': 200,
            'detail': "OK",
            'result': "Matcher is currently busy. Please try again later.."
        }

    async with endpoint_lock:
        response = await service.run_custom_match(uof, filename, data, date, pool, without_crossed=True)
        if response.get("status_code") != 200:
            raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
        return response


@router.post("/revers_match/")
async def revers_match(request: Request, all_results: Optional[bool] = False, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    sends data to the revers matcher
    :param request Optional
    ...
    :return: response
    """

    try:
        data = await request.json()
    except ValueError:
        data = None

    response = await service.run_revers_match(uof, data, all_results)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@router.get("/custom_match_status/{hash}")
async def custom_match_status(hash, uof: PostgresUnitOfWork = Depends(get_uof)):
    """

    """


    response = await service.get_custom_match_status(uof, hash)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


#####################################################################################################################
# manual matches

@router.get("/manual_matches/")
async def get_configuration(uof: PostgresUnitOfWork = Depends(get_uof)):
    """
    Return whitelist and banlist.
    :param uof:
    :return:
    """
    response = await service.get_manual_matches(uof)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response

fastapi_app.include_router(router, prefix="/api/v1")
