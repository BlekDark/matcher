import json
from typing import Optional
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from src.uof import PostgresUnitOfWork
import src.service_layer as service
import logging
import asyncpg
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

    response = await service.get_sources(uof, **data)
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


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
    :return: id
    """
    data = await request.json()
    response = await service.create_sport_type(uof, **json.loads(data))
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

#####################################################################################################################
# matcher endpoints
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
       pairs: List[Dict],
       updated_at: timestamp
    }
    """
    data = await request.json()
    response = await service.finish_run(uof, **json.loads(data))
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response

@fastapi_app.get("/manual_matches/")
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


#####################################################################################################################
# custom test_ matcher endpoints

@fastapi_app.get("/pairs_custom/")
async def get_results(task_id, uof: PostgresUnitOfWork = Depends(get_uof)):
    """
                По task_id возвращает данные по ранам, параметры, и информацию о количестве событий и матчей
        :request: task_id
        :return: {
            status_code
            detail
            result: {
                runs: [],
                parameters: {},
                count: {},
                runtime: int
            }
        }
        """

    response = await service.get_results_custom(uof, int(task_id))
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response


@fastapi_app.post("/save_metadata")
async def save_metadata(request: Request, uof: PostgresUnitOfWork = Depends(get_uof)):
    # TODO write docs
    data = await request.json()
    response = await service.save_metadata(uof, **json.loads(data))
    if response.get("status_code") != 200:
        raise HTTPException(status_code=response.get("status_code"), detail=response.get("detail"))
    return response
