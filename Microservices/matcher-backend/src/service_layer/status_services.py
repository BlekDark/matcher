from src.uof import PostgresUnitOfWork
from src.service_layer.utils import handle_error,  make_response
import src.exceptions as exceptions
import logging

logger = logging.getLogger("backend-matcher")


async def get_statuses(uof: PostgresUnitOfWork):
    """

    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            statuses = await uof.status_repo.get()
            result = [
                {
                    'status_id': status_id,
                    'status': status,
                }
                for status_id, status in statuses
            ]
            await uof.commit()
            logger.info(f'Get all statuses - OK')
            return make_response(result=result)

        except Exception as e:
            return await handle_error(uof, e)


async def get_status_by_id(uof: PostgresUnitOfWork, status_id: int):
    """
    :param uof:
    :param status_id:
    :return:
    {'status_code', 'detail', 'result'}
    """
    async with uof:
        try:
            await uof.begin()
            entry = await uof.status_repo.get_by_id(entry_id=status_id)
            await uof.commit()
            logger.info(f'Status entry, id={status_id} was retrieved')
            return make_response(result=entry)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"Status entry with id={status_id} does not exist!")
            return make_response(status_code=404, detail=f"Status entry with id={status_id} does not exist!")
        except Exception as e:
            return await handle_error(uof, e)


async def add_status(uof: PostgresUnitOfWork, **kwargs):
    """

    :param uof:
    :param request:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                'status': kwargs.get('status'),
            }
            result = await uof.status_repo.create(**data)
            await uof.commit()
            logger.info(f"Data with status={kwargs.get('status', None)} entered into the database status")
            return make_response(result=result)
        except exceptions.EntryAlreadyExists:
            await uof.rollback()
            logger.error(f"The entry with status={kwargs.get('status', None)} exists in the database statuses!")
            return make_response(status_code=404,
                                 detail=f"The entry with status={kwargs.get('status', None)} "
                                        f"exists in the database statuses!")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"Absent status={kwargs.get('status', None)} is the request")
            return make_response(status_code=400,
                                 detail=f"Absent status={kwargs.get('status', None)} is the request")
        except Exception as e:
            return await handle_error(uof, e)



async def modify_status(uof: PostgresUnitOfWork, **kwargs):
    """

    :param uof:
    :param request:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                'id': kwargs.get('id'),
                'status': kwargs.get('status'),
            }
            result = await uof.status_repo.modify(**data)
            logger.info(f"Data with status={kwargs.get('status', None)} entered into the database statuses")
            await uof.commit()
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"The entry with status={kwargs.get('status', None)} not exists in the database statuses!")
            return make_response(status_code=404, detail=f"The entry with status={kwargs.get('status', None)} "
                                                         f"not exists in the database statuses!")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"Absent id={kwargs.get('id', None)} and/or "
                         f"status={kwargs.get('status', None)} is the request")
            return make_response(status_code=400, detail=f"Absent id={kwargs.get('id', None)} and/or "
                                                         f"status={kwargs.get('status', None)} is the request")
        except Exception as e:
            return await handle_error(uof, e)


async def delete_status(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :param request:
    :return:
    """
    async with uof:
        try:
            await uof.begin()

            data = {
                "id": kwargs.get('id', None),
                "status": kwargs.get('status', None)
            }
            result = await uof.status_repo.delete(**data)
            await uof.commit()
            logger.info(f"Data with status:{kwargs.get('status', None)}, id: {kwargs.get('id', None)} "
                        f"delete into the database statuses")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"No entry with status:{kwargs.get('status', None)}, id: {kwargs.get('id', None)} "
                         f"in the database statuses")
            return make_response(status_code=404,
                                 detail=f"No entry with name:{kwargs.get('name', None)}, "
                                        f"id: {kwargs.get('id', None)} in the database statuses")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Absent id or status")
            return make_response(status_code=400, detail="Absent id or status")
        except Exception as e:
            return await handle_error(uof, e)
