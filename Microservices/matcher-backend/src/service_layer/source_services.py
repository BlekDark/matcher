from src.uof import PostgresUnitOfWork
from src.service_layer.utils import handle_error,  make_response
import src.exceptions as exceptions
import logging
import time

logger = logging.getLogger("backend-matcher")


async def get_sources(uof: PostgresUnitOfWork, **kwargs):
    """
    Return all sources
    :param uof:
    :param kwargs {source_id, source_name}
    :return: [{source_id, source_name, source_url, timestamp}]
    """
    async with uof:
        # start_time_db = time.time()
        try:
            await uof.begin()
            sources = await uof.source_repo.get()
            result = [
                {
                    'source_id': source_id,
                    'source_name': sources_name,
                    'source_url': source_url,
                    'timestamp': await uof.task_repo.get_source_timestamp(source_id=source_id)
                }
                for source_id, sources_name, source_url in sources
            ]
            await uof.commit()
            # end_time_db = time.time()
            # logger.info(f'Time taken for DB operation: {end_time_db - start_time_db} seconds')
            logger.info(f'Get all sources - OK')
            return make_response(result=result)
        except Exception as e:
            return await handle_error(uof, e)


async def get_sources_plain(uof: PostgresUnitOfWork):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            result = await uof.source_repo.get()
            await uof.commit()
            logger.info(f'Get all sources - OK')
            return make_response(result=result)
        except Exception as e:
            return await handle_error(uof, e)


async def get_source_by_id(uof: PostgresUnitOfWork, source_id: int):
    """
    :param uof:
    :param source_id:
    :return:
    {'status_code', 'detail', 'result'}
    """
    async with uof:
        try:
            await uof.begin()
            entry = await uof.source_repo.get_by_id(entry_id=source_id)
            await uof.commit()
            logger.info(f'Source entry, id={source_id} was retrieved')
            return make_response(result=entry)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"Source entry with id={source_id} does not exist!")
            return make_response(status_code=404, detail=f"Source entry with id={source_id} does not exist!")
        except Exception as e:
            return await handle_error(uof, e)


async def add_source(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                'name': kwargs.get('name'),
                'url': kwargs.get('url'),
            }
            result = await uof.source_repo.create(**data)
            await uof.commit()
            logger.info(f"Data with name={kwargs.get('name', None)} entered into the database sources")
            return make_response(result=result)
        except exceptions.EntryAlreadyExists:
            await uof.rollback()
            logger.error(f"The entry with name={kwargs.get('name', None)} exists in the database sources!")
            return make_response(status_code=404, detail=f"The entry with name={kwargs.get('name', None)} exists in the database sources!")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Absent name and/or url")
            return make_response(status_code=404, detail="Absent name and/or url")
        except Exception as e:
            return await handle_error(uof, e)


async def modify_source(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                'id': kwargs.get('id'),
                'name': kwargs.get('name'),
                'url': kwargs.get('url'),
            }
            result = await uof.source_repo.modify(**data)
            await uof.commit()
            logger.info(f"Data with name={kwargs.get('name', None)} entered into the database sources")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"The entry with name={kwargs.get('name', None)} not exists in the database sources!")
            return make_response(status_code=404, detail=f"The entry with name={kwargs.get('name', None)} not exists in the database sources!")
        except Exception as e:
            return await handle_error(uof, e)


async def delete_source(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                "id": kwargs.get('id', None),
                "name": kwargs.get('name', None)
            }
            result = await uof.source_repo.delete(**data)
            await uof.commit()
            logger.info(f"Data with name:{kwargs.get('name', None)}, id: {kwargs.get('id', None)} delete into the "
                        f"database sources")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"No entry with name:{kwargs.get('name', None)}, id: {kwargs.get('id', None)}")
            return make_response(status_code=404, detail=f"No entry with name:{kwargs.get('name', None)}, id: {kwargs.get('id', None)}")
        except Exception as e:
            return await handle_error(uof, e)
