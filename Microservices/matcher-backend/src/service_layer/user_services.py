from src.uof import PostgresUnitOfWork
from src.service_layer.utils import handle_error,  make_response
import src.exceptions as exceptions
import logging

logger = logging.getLogger("backend-matcher")


async def get_user(uof: PostgresUnitOfWork):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            users = await uof.user_repo.get()

            result = [
                {
                    'user_id': user['id'],
                    'name': user['name'],
                    'permission_id': user['permission_id'],
                }
                for user in users
            ]
            await uof.commit()
            logger.info(f'Get all users - OK')
            return make_response(result=result)
        except Exception as e:
            return await handle_error(uof, e)


async def get_user_by_id(uof: PostgresUnitOfWork, user_id: int):
    """

    :param uof:
    :param user_id:
    :return:
    {'status_code', 'detail', 'result'}
    """
    async with uof:
        try:
            await uof.begin()
            entry = await uof.user_repo.get_by_id(entry_id=user_id)
            await uof.commit()
            logger.info(f'User entry, id={user_id} was retrieved')
            return make_response(result=entry)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"User entry with id={user_id} does not exist!")
            return make_response(status_code=404, detail=f"User entry with id={user_id} does not exist!")
        except Exception as e:
            return await handle_error(uof, e)


async def add_user(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            await uof.permission_repo.get_by_id(entry_id=kwargs.get('permission_id'))
            data = {
                'name': kwargs.get('name'),
                'permission_id': kwargs.get('permission_id'),
            }
            result = await uof.user_repo.create(**data)
            await uof.commit()
            logger.info(f"Data with name={kwargs.get('name', None)} entered into the database users")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"The entry with name={kwargs.get('name', None)} does not in the database users!")
            return make_response(status_code=404,
                        detail=f"The entry with name={kwargs.get('name', None)} does not in the database users!")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Absent name and/or permission_id")
            return make_response(status_code=404,
                                 detail=f"Absent name and/or permission_id")
        except exceptions.EntryAlreadyExists:
            await uof.rollback()
            logger.error(f"The permission with id={kwargs.get('permission_id')} exists in the database permissions!")
            return make_response(status_code=404,
                detail=f"The permission with id={kwargs.get('permission_id')} exists in the database permissions!")
        except Exception as e:
            return await handle_error(uof, e)


async def modify_user(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            await uof.permission_repo.get_by_id(entry_id=kwargs.get('permission_id'))
            data = {
                'id': kwargs.get('id'),
                'name': kwargs.get('name'),
                'permission_id': kwargs.get('permission_id'),
            }
            result = await uof.user_repo.modify(**data)
            await uof.commit()
            logger.info(f"Data with name={kwargs.get('name', None)} entered into the database users")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"The entry with name={kwargs.get('name', None)} not exists in the database users!")
            return make_response(status_code=404,
                        detail=f"The entry with name={kwargs.get('name', None)} not exists in the database users!")
        except exceptions.EntryAlreadyExists:
            await uof.rollback()
            logger.error(f"The permission with id={kwargs.get('permission_id')} exists in the database permissions!")
            return make_response(status_code=404,
                    detail=f"The permission with id={kwargs.get('permission_id')} exists in the database permissions!")
        except Exception as e:
            return await handle_error(uof, e)


async def delete_user(uof: PostgresUnitOfWork, **kwargs):
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
            result = await uof.user_repo.delete(**data)
            await uof.commit()
            logger.info(f"Data with name:{kwargs.get('name', None)} delete into the database users")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"No entry with name:{kwargs.get('name', None)}, id: {kwargs.get('id', None)}")
            return make_response(status_code=404, detail=f"No entry with name:{kwargs.get('name', None)}, "
                                                         f"id: {kwargs.get('id', None)}")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"No id: {kwargs.get('id', None)} or name: {kwargs.get('name', None)} values to delete are provided!")
            return make_response(status_code=404,
                                 detail=f"No id: {kwargs.get('id', None)} "
                                        f"or name: {kwargs.get('name', None)} values to delete are provided!")
        # except Exception as e:
        #     return await handle_error(uof, e)
