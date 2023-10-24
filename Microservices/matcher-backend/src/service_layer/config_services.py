from src.uof import PostgresUnitOfWork
from src.service_layer.utils import handle_error,  make_response
import src.exceptions as exceptions
import logging
from datetime import datetime

logger = logging.getLogger("backend-matcher")



async def get_config(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :param kwargs: {default, source1_id, source2_id}
    :return:
    """
    async with uof:
        try:
            await uof.begin()
            parameters = await uof.parameters_repo.get()
            default_values = {p_name: p_val for _, p_name, p_val in parameters}

            if kwargs.get('default', None):
                await uof.commit()
                logger.info(f'Get default config - OK')
                return make_response(result=default_values)

            elif kwargs.get('source1_id', None) and kwargs.get('source2_id', None):
                await uof.source_repo.get_by_id(entry_id=kwargs.get('source1_id'))
                await uof.source_repo.get_by_id(entry_id=kwargs.get('source2_id'))
                id2name = {p_id: p_name for p_id, p_name, _ in parameters}
                result = {'source1_id': kwargs.get('source1_id'),
                          'source2_id': kwargs.get('source2_id'),
                          'types': {}}
                result.update(default_values)
                raw_configs = await uof.config_repo.get_by_sources(source1_id=kwargs.get('source1_id'),
                                                                   source2_id=kwargs.get('source2_id'))
                for e_id, sport_id, param_id, value in raw_configs:
                    if sport_id is not None:
                        if sport_id not in result['types'].keys():
                            result['types'].update({sport_id: {id2name.get(param_id): value}})
                        else:
                            result['types'][sport_id][id2name.get(param_id)] = value
                    else:
                        result[id2name.get(param_id)] = value
                await uof.commit()
                logger.info(f'Get config for {kwargs.get("source1_id")} & {kwargs.get("source2_id")} - OK')
                return make_response(result=result)

            else:
                await uof.rollback()
                logger.error(f"No sources ids given to get configs.")
                return make_response(status_code=404, detail=f"No sources ids given to get configs.")

        except exceptions.EntryDoesNotExist:
            await uof.rollback()
            logger.error(f"Some sources {kwargs.get('source1_id')} or {kwargs.get('source2_id')} "
                         f"do not exist in the database!")
            return make_response(status_code=404, detail=f"Some sources {kwargs.get('source1_id')} or {kwargs.get('source2_id')} do not exist in the database!")
        except Exception as e:
            return await handle_error(uof, e)


async def create_modify_config(uof: PostgresUnitOfWork, **kwargs):
    """
{
    "source1_id": 21,
    "source2_id": 22,
    "types": {
      "2": {
        "MINIMAL_SIM_THRESHOLD": 45,
        "REMOVE_CANDIDATE_THRESHOLD": 80,
        "FINAL_SIM_RATIO": 0.8,
        "CONFIDENT_THRESHOLD": 100
      }
    },
    "MINIMAL_SIM_THRESHOLD": 40,
    "REMOVE_CANDIDATE_THRESHOLD": 75,
    "FINAL_SIM_RATIO": 0.8,
    "CONFIDENT_THRESHOLD": 100
  }
    :param uof:
    :param kwargs: {source1_id, source2_id, default, params}
    :return:
    """
    async with uof:
        try:
            await uof.begin()

            if not (kwargs.get('source1_id', None) and kwargs.get('source2_id', None)) \
                    and kwargs.get('default', None) is None:
                raise exceptions.InvalidParameters()

            parameters = await uof.parameters_repo.get()
            param2id = {p_name: p_id for p_id, p_name, p_val in parameters}
            if kwargs.get('default', None) is not None:
                for name, p_id in param2id.items():
                    if not kwargs.get('default').get(name, None):
                        continue
                    value = kwargs.get('default').get(name)
                    data = {'id': p_id, 'default_value': value}
                    success = await uof.parameters_repo.modify(**data)
                    await uof.commit()

                    if success:
                        logger.debug(f"{name} default value was modified.")

            if kwargs.get('source1_id', None) and kwargs.get('source2_id', None):
                if int(kwargs.get('source1_id')) < int(kwargs.get('source2_id')):
                    s1 = int(kwargs.get('source1_id'))
                    s2 = int(kwargs.get('source2_id'))
                else:
                    s1 = int(kwargs.get('source2_id'))
                    s2 = int(kwargs.get('source1_id'))
                # change values for pair source1 and source2
                for name, p_id in param2id.items():
                    if kwargs.get(name, None) is None:
                        continue
                    r1_id = await uof.config_repo.check_exists(source1_id=s1, source2_id=s2, param_id=p_id)
                    if r1_id is None:
                        data = {
                            'source_id': s1,
                            'param_id': p_id,
                            'value':  float(kwargs.get(name)),
                            'source2_id': s2,
                            'sport_id': None,
                            'updated_at': datetime.now(),
                            'modified_by': None
                        }
                        new_id = await uof.config_repo.create(**data)
                        await uof.commit()
                        if new_id is not None:
                            logger.debug(f"{name} value of {s1} & {s2} sources was created.")
                    else:
                        data = {'id': r1_id, 'value': float(kwargs.get(name))}
                        success = await uof.config_repo.modify(**data)
                        await uof.commit()
                        if success:
                            logger.debug(f"{name} value of {s1} & {s2} sources was modified.")
                # change values for sport in pair  source1 and source2
                for name, p_id in param2id.items():
                    for sp_id, values in kwargs.get("types").items():
                        if values.get(name, None) is None:
                            continue
                        r2_id = await uof.config_repo.check_exists(source1_id=s1, source2_id=s2, param_id=p_id,
                                                                   sport_id=int(sp_id))
                        if r2_id is None:
                            data = {
                                'source_id': s1,
                                'param_id': p_id,
                                'value': float(values.get(name)),
                                'source2_id': s2,
                                'sport_id': int(sp_id),
                                'updated_at': datetime.now(),
                                'modified_by': None
                            }
                            new_id = await uof.config_repo.create(**data)
                            await uof.commit()
                            if new_id is not None:
                                logger.debug(f"{name} value of {s1} & {s2} sources and sport {sp_id} was created.")
                        else:
                            data = {'id': r2_id, 'value': float(values.get(name))}
                            success = await uof.config_repo.modify(**data)
                            await uof.commit()
                            if success:
                                logger.debug(f"{name} value of {s1} & {s2} sources and sport {sp_id} was modified.")
            await uof.commit()
            if kwargs.get('default', None) is not None:
                logger.info(f"Default parameters configuration was successfully modified")
            if kwargs.get('source1_id', None) and kwargs.get('source2_id'):
                logger.info(f"Configuration between {kwargs.get('source1_id')} and {kwargs.get('source2_id')} was "
                            f"created/modified.")
            return make_response()
        except exceptions.InvalidParameters:
            await uof.rollback()
            logger.error(f"No sources ids or default vals given to get configs.")
            return make_response(status_code=404, detail=f"No sources ids or default vals given to get configs.")
        except Exception as e:
            return await handle_error(uof, e)


async def delete_config(uof: PostgresUnitOfWork, **kwargs):
    """
    :param uof:
    :param kwargs: {source1_id, source2_id, params(?)}
    :return:
    """
    async with uof:
        try:
            pass
        except exceptions.InvalidParameters:
            # todo: here more specific logger
            await uof.rollback()
            logger.error(f"No sources ids given to get configs.")
            return make_response(status_code=404, detail=f"No sources ids given to get configs.")
        except Exception as e:
            return await handle_error(uof, e)
