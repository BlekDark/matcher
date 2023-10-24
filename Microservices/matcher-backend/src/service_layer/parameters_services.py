from src.uof import PostgresUnitOfWork
from src.service_layer.utils import handle_error,  make_response
import src.exceptions as exceptions
import logging

logger = logging.getLogger("backend-matcher")



async def get_parameters(uof: PostgresUnitOfWork):
    """
    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            result = await uof.parameters_repo.get()
            await uof.commit()
            logger.info(f'Get all parameters - OK')
            return make_response(result=result)
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=404, detail=f"Something went wrong:\n{e}")


async def get_parameter_by_id(uof: PostgresUnitOfWork, parameter_id: int):
    """
    :param uof:
    :param parameter_id:
    :return:
    {'status_code', 'detail', 'result'}
    """
    async with uof:
        try:
            await uof.begin()
            entry = await uof.parameters_repo.get_by_id(entry_id=parameter_id)
            await uof.commit()
            logger.info(f'Parameter entry, id={parameter_id} was retrieved')
            return make_response(result=entry)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"Parameter entry with id={parameter_id} does not exist!")
            return make_response(status_code=404, detail=f"Parameter entry with id={parameter_id} does not exist!")

        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=404, detail=f"Something went wrong:\n{e}")


async def add_parameter(uof: PostgresUnitOfWork, **kwargs):
    """

    :param uof:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            data = {
                'name': kwargs.get('name'),
                'default_value': kwargs.get('default_value')
            }
            result = await uof.parameters_repo.create(**data)
            await uof.commit()
            logger.info(f"Data with name={kwargs.get('name', None)} entered into the database parameters")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"The entry with name={kwargs.get('name', None)} exists in the database parameters!")
            return make_response(status_code=400, detail=f"The entry with name={kwargs.get('name', None)} exists in the database parameters!")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error("Absent name")
            return make_response(status_code=404, detail=f"Absent name")
        except Exception as e:
            return await handle_error(uof, e)


async def modify_parameter(uof: PostgresUnitOfWork, **kwargs):
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
                'default_value': kwargs.get('default_value')
            }
            result = await uof.parameters_repo.modify(**data)
            await uof.commit()
            logger.info(f"Data with name={kwargs.get('name', None)} entered into the database parameters")
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"The entry with name={kwargs.get('name', None)} not exists in the database parameters!")
            return make_response(status_code=404, detail=f"The entry with id={kwargs.get('id', None)} does not exist in the database parameters!")
        except Exception as e:
            return await handle_error(uof, e)


async def delete_parameter(uof: PostgresUnitOfWork, **kwargs):
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
            result = await uof.parameters_repo.delete(**data)
            logger.info(f"Data with name:{kwargs.get('name', None)}, id: {kwargs.get('id', None)} delete into the database parameters")
            await uof.commit()
            return make_response(result=result)
        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"No entry with name:{kwargs.get('name', None)}, id: {kwargs.get('id', None)}")
            return make_response(status_code=404, detail=f"No entry with name:{kwargs.get('name', None)}, id: {kwargs.get('id', None)}")
        except Exception as e:
            return await handle_error(uof, e)
