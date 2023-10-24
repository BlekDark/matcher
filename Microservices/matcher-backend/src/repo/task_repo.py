from src.repo import AbstractRepository
import src.exceptions as exceptions


class TaskRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.tasks")
        return results

    async def create(self, *args, **kwargs):
        source1_id = kwargs.get('source1_id', None)
        source2_id = kwargs.get('source2_id', None)

        if not (source1_id and source2_id):
            raise exceptions.InvalidParameters()

        keys = ', '.join(kwargs.keys())
        values_positions = ', '.join(f'${i}' for i in range(1, len(kwargs) + 1))
        insert_query = f"INSERT INTO matcher.tasks ({keys}) VALUES ({values_positions}) RETURNING id"
        data_to_insert = tuple(kwargs.values())
        row_id = await self.session.fetchval(insert_query, *data_to_insert)
        return row_id

    async def modify(self, *args, **kwargs):
        task_id = kwargs.get('id', None)
        if not task_id or len(kwargs) < 2:
            raise exceptions.InvalidParameters()

        columns = []
        values = []
        for col, val in kwargs.items():
            if col != 'id' and val is not None:
                columns.append(col)
                values.append(val)

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.tasks as t WHERE t.id = $1)"
        check_query = await self.session.fetch(check_query, task_id)

        if check_query[0]['exists']:
            update_query = "UPDATE matcher.tasks as t SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE t.id = $1"

            await self.session.execute(update_query, task_id, *values)
            return True
        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        task_id = kwargs.get('id', None)
        if not task_id:
            raise exceptions.InvalidParameters()

        attribute_name = 'id'

        delete_query = f"DELETE FROM matcher.tasks as t WHERE {attribute_name} = $1"
        select_query = f"SELECT * FROM matcher.tasks as t WHERE {attribute_name} = $1"

        results = await self.session.fetch(select_query, task_id)

        if len(results) != 0:
            results = await self.session.fetch(delete_query, task_id)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with {attribute_name}={task_id}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        select_query = 'SELECT t.id , t.started_at , t.finished_at , t.status_user , t.status_observer, ' \
                       't.referent_task, t.source1_id, t.source2_id FROM ' \
                       'matcher.tasks as t WHERE t.id = $1 '
        result = await self.session.fetch(select_query, entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result[0]

    async def get_num_sports(self, task_id: int):
        result = await self.session.fetchval('SELECT t.num_sports FROM matcher.tasks as t WHERE t.id = $1', task_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result

    async def get_by_sources(self, source1_id: int, source2_id: int):
        query = """
            SELECT 
                t.id, 
                t.started_at, 
                t.finished_at, 
                t.status_user, 
                t.status_observer, 
                t.referent_task, 
                t.source1_id, 
                t.source2_id,  
                coalesce(sum(r.num_matches), 0) as num_matches,
                coalesce(sum(jsonb_array_length(r.source1_data)), 0) as source1_count,
                coalesce(sum(jsonb_array_length(r.source2_data)), 0) as source2_count
            FROM matcher.tasks t 
            LEFT JOIN matcher.runs r ON t.id = r.task_id
            WHERE ((t.source1_id = $1 AND t.source2_id = $2) OR (t.source1_id = $3 AND t.source2_id = $4))
            AND t.finished_at IS NOT NULL
            GROUP BY t.id, t.started_at, t.finished_at, t.status_user, t.status_observer, t.referent_task, t.source1_id, t.source2_id
        """
        result = await self.session.fetch(query, source1_id, source2_id, source2_id, source1_id)
        # if not result:
        #     raise exceptions.EntryDoesNotExist()
        return result

    async def get_source_timestamp(self, source_id):
        select_query = f'select max(t.started_at)  from matcher.tasks t where ' \
                       f'(t.source1_id = $1 OR t.source2_id = $1) and t.finished_at is not null '
        result = await self.session.fetchval(select_query, source_id)
        return result
