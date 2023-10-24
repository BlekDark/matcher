from src.uof import PostgresUnitOfWork
from src.service_layer.utils import handle_error,  make_response
import src.exceptions as exceptions
import logging

logger = logging.getLogger("backend-matcher")


async def get_sport_types(uof: PostgresUnitOfWork):
    """

    :param uof:
    :return:
    {'status_code', 'detail', 'result'}
    """
    response = {'status_code': 200, 'detail': "OK"}
    async with uof:
        try:
            await uof.begin()
            sport_types = await uof.sport_repo.get()
            result = [
                [
                    sport_id,
                    sport_name,
                    is_cyber
                ]
                for sport_id, sport_name, is_cyber in sport_types
            ]
            await uof.commit()
            logger.info(f'Get all sport types - OK')
            return make_response(result=result)
        except Exception as e:
            return await handle_error(uof, e)


async def create_sport_type(uof: PostgresUnitOfWork, **kwargs):
    """

    :param uof:
    :param kwargs: {name}
    :return:
    """
    # response = {'status_code': 200, 'detail': "OK"}
    async with uof:
        try:
            await uof.begin()
            data = {'name': kwargs.get('name'), 'is_cyber': kwargs.get('is_cyber', '0')}
            result = await uof.sport_repo.create(**data)
            await uof.commit()
            logger.info(f"Sport type with name={kwargs.get('name')} was created, id={result}")
            return make_response(result=result)
        except KeyError:
            await uof.rollback()
            logger.error("Given parameters are missing some value.")
            return make_response(status_code=404,
                                 detail="Given parameters are missing some value")
        except exceptions.EntryAlreadyExists:
            await uof.rollback()
            logger.error(f"Sport type {kwargs.get('name')} already exists in database!")
            return make_response(status_code=404,
                                 detail=f"Sport type {kwargs.get('name')} already exists in database!")
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=500,
                                 detail=f"Something went wrong:\n{e}")


async def get_sport_type(uof: PostgresUnitOfWork, sport_name: str, force_create=False):
    """

    :param uof:
    :param sport_name:
    :param force_create:
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            sport_id = await uof.sport_repo.get_by_name(sport_name=sport_name)
            await uof.commit()
            logger.info(f'Get sport_type_id - OK')
            return make_response(result=sport_id)
        except exceptions.EntryDoesNotExist:
            if force_create:
                sport_id = await uof.sport_repo.create(**{'name': sport_name})
                await uof.commit()
                logger.info(f'Sport type with name={sport_name} was created, id={sport_id}')
                return make_response(result=sport_id)
            else:
                await uof.rollback()
                logger.error(f"Sport type {sport_name} does not exist in database!")
                return make_response(status_code=404,
                                     detail=f"Sport type {sport_name} already exists in database!")
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"Given parameters are invalid.")
            return make_response(status_code=400,
                                 detail="Given parameters are invalid.")
        except exceptions.EntryAlreadyExists:
            await uof.rollback()
            logger.error(f"Sport type {sport_name} already exists in database!")
            return make_response(status_code=404,
                                 detail=f"Sport type {sport_name} already exists in database!")
        except Exception as e:
            await uof.rollback()
            logger.error(f"Something went wrong:\n{e}")
            return make_response(status_code=404,
                                 detail=f"Something went wrong:\n{e}")

