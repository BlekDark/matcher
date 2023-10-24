from src.uof import PostgresUnitOfWork
from src.service_layer.utils import handle_error,  make_response
import src.exceptions as exceptions
import logging

logger = logging.getLogger("backend-matcher")



async def get_permission(uof: PostgresUnitOfWork):
    """

    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            permissions = await uof.permission_repo.get()
            result = [
                {
                    'permission_id': permission_id,
                    'permission_name': permission_name,
                }
                for permission_id, permission_name in permissions
            ]
            await uof.commit()
            logger.info(f'Get all permissions - OK')
            return make_response(result=result)
        except Exception as e:
            return await handle_error(uof, e)


async def get_permission_by_id(uof: PostgresUnitOfWork, permission_id: int):
    """
    :param uof:
    :param permission_id:
    :return:
    {'status_code', 'detail', 'result'}
    """
    async with uof:
        try:
            await uof.begin()
            entry = await uof.permission_repo.get_by_id(entry_id=permission_id)
            await uof.commit()
            logger.info(f'Permission entry, id={permission_id} was retrieved')
            return make_response(result=entry)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"Permission entry with id={permission_id} does not exist!")
            return make_response(status_code=404, detail=f"Permission entry with id={permission_id} does not exist!")
        except Exception as e:
            return await handle_error(uof, e)


async def add_permission(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                'type': kwargs.get('type'),
            }
            result = await uof.permission_repo.create(**data)
            await uof.commit()
            logger.info(f"Data with id={kwargs.get('id', None)} entered into the database permission")
            return make_response(result=result)
        except exceptions.EntryAlreadyExists:
            await uof.rollback()
            logger.error(f"The entry with id={kwargs.get('id', None)} exists in the database permissions!")
            return make_response(status_code=404,
                        detail=f"The entry with id={kwargs.get('id', None)} exists in the database permissions!")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Absent type")
            return make_response(status_code=400,
                            detail="Absent type")
        except Exception as e:
            return await handle_error(uof, e)


async def modify_permission(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                'id': kwargs.get('id'),
                'type': kwargs.get('type'),
            }
            result = await uof.permission_repo.modify(**data)
            await uof.commit()
            logger.info(f"Data with id={kwargs.get('id', None)} entered into the database permissions")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"The entry with id={kwargs.get('id', None)} not exists in the database permissions!")
            return make_response(status_code=404,
                        detail=f"The entry with id={kwargs.get('id', None)} not exists in the database permissions!")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Absent id and/or type")
            return make_response(status_code=400, detail="Absent id and/or type")
        except Exception as e:
            return await handle_error(uof, e)


async def delete_permission(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                "id": kwargs.get('id', None),
                "type": kwargs.get('type', None)
            }
            result = await uof.permission_repo.delete(**data)
            await uof.commit()
            logger.info(f"Data with id={kwargs.get('id', None)} delete into the database permissions")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"No entry with name:{kwargs.get('name', None)}, id: {kwargs.get('id', None)}")
            return make_response(status_code=404, detail=f"No entry with name:{kwargs.get('name', None)}, "
                                                         f"id: {kwargs.get('id', None)}")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Absent id or type")
            return make_response(status_code=400, detail="Absent id or type")
        except Exception as e:
            return await handle_error(uof, e)

