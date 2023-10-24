from src.repo import AbstractRepository
import src.exceptions as exceptions


class ConfigRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.configs")
        return results

    async def create(self, *args, **kwargs):
        insert_query = "INSERT INTO matcher.configs (" + ", ".join([f"{k}" for k in kwargs.keys()]) \
                       + ") VALUES (" + ",".join([f"${i + 1}" for i in range(len(kwargs))]) + ") RETURNING id"
        data_to_insert = tuple(kwargs.values())
        result = await self.session.fetch(insert_query, *data_to_insert)
        return result[0]['id']

    async def modify(self, *args, **kwargs):
        id = kwargs.get('id', None)
        if not id or len(kwargs) < 2:
            raise exceptions.InvalidParameters()

        columns = []
        values = []
        for col, val in kwargs.items():
            if col != 'id' and val is not None:
                columns.append(col)
                values.append(val)

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.configs WHERE id = $1)"
        check_query_result = await self.session.fetch(check_query, id)

        if check_query_result[0]['exists']:
            update_query = "UPDATE matcher.configs SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE id = $1"
            await self.session.fetch(update_query, id, *values)
            return True
        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        id = kwargs.get('id', None)
        if not id:
            raise exceptions.InvalidParameters('No id value to delete is provided!')

        select_query = "SELECT * FROM matcher.configs WHERE id = $1"
        delete_query = "DELETE FROM matcher.configs WHERE id = $1"

        results = await self.session.fetch(select_query, id)
        if len(results) != 0:
            results = await self.session.fetch(delete_query, id)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with id={id}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        result = await self.session.fetch("SELECT * FROM matcher.configs WHERE id = $1", entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result

    async def get_by_sources(self, source1_id: int, source2_id: int):
        s1, s2 = (source1_id, source2_id) if source1_id < source2_id else (source2_id, source1_id)
        select_query = 'SELECT id, sport_id, param_id, value FROM matcher.configs WHERE source_id = $1 AND source2_id = $2'
        result = await self.session.fetch(select_query, s1, s2)
        return result

    async def check_exists(self, source1_id: int, source2_id: int, param_id: int, sport_id: int = None):
        if sport_id is not None:
            select_query = 'SELECT id FROM matcher.configs WHERE source_id = $1 AND source2_id = $2 AND param_id = $3 AND sport_id = $4'
            result = await self.session.fetch(select_query, source1_id, source2_id, param_id, sport_id)
        else:
            select_query = 'SELECT id FROM matcher.configs WHERE source_id = $1 AND source2_id = $2 AND param_id = $3 AND sport_id is NULL'
            result = await self.session.fetch(select_query, source1_id, source2_id, param_id)
        return result[0]['id'] if result else None
