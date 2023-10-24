from src.repo import AbstractRepository
import src.exceptions as exceptions


class RunRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.runs")
        return results

    async def create(self, *args, **kwargs):
        if not (kwargs.get('task_id', None) and
                kwargs.get('sport_id', None)):
            raise exceptions.InvalidParameters()
        insert_query = "INSERT INTO matcher.runs as r ( " + ",".join([f"{k}" for k in kwargs.keys()]) \
                       + ") VALUES ( " + ",".join([f"${i + 1}" for i in range(len(kwargs.keys()))]) + ") RETURNING id"
        row_id = await self.session.fetchval(insert_query, *tuple(kwargs.values()))
        return row_id

    async def modify(self, *args, **kwargs):
        id = kwargs.get('id', None)
        if not id or len(kwargs) < 2:  # apart from id there must be at least one more argument
            raise exceptions.InvalidParameters()

        columns = []
        values = []
        for col, val in kwargs.items():
            if col != 'id' and val is not None:
                columns.append(col)
                values.append(val)

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.runs as r WHERE r.id = $1)"
        entry_exists = await self.session.fetchval(check_query, id)

        if entry_exists:
            update_query = "UPDATE matcher.runs as r SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE r.id = $1"
            await self.session.execute(update_query, id, *values)
            return True
        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        id = kwargs.get('id', None)
        if not id:
            raise exceptions.InvalidParameters()

        select_query = "SELECT * FROM matcher.runs as r WHERE r.id = $1"
        delete_query = "DELETE FROM matcher.runs as r WHERE r.id = $1"

        results = await self.session.fetch(select_query, id)

        if len(results) != 0:
            await self.session.execute(delete_query, id)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with id={id}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        select_query = 'SELECT * FROM matcher.runs as r WHERE r.id = $1'
        result = await self.session.fetch(select_query, entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result

    async def get_num_done_runs(self, task_id: int):
        """
        Count how many runs of the task is done
        :param task_id:
        :return:
        """
        select_query = 'SELECT COUNT(*) FROM matcher.runs as r WHERE r.task_id = $1 AND r.runtime IS NOT NULL'
        result = await self.session.fetchval(select_query, task_id)
        if result is None:
            raise exceptions.EntryDoesNotExist()
        return result

    async def get_by_task_id(self, task_id: int):
        select_query = 'SELECT r.id, r.sport_id, r.status_user, r.status_observer, r.runtime, ' \
                       'r.source1_data, r.source2_data FROM matcher.runs r WHERE r.task_id = $1'
        results = await self.session.fetch(select_query, task_id)
        if results[0] is None:
            raise exceptions.EntryDoesNotExist()
        return results

    async def get_task(self, run_id: int):
        select_query = 'SELECT r.task_id FROM matcher.runs as r WHERE r.id = $1'
        result = await self.session.fetchval(select_query, run_id)
        if result is None:
            raise exceptions.EntryDoesNotExist()
        return result

    async def get_source_data_by_task_id(self, task_id: int):
        select_query = 'SELECT r.source1_data, r.source2_data FROM matcher.runs r WHERE r.task_id = $1'
        results = await self.session.fetch(select_query, task_id)
        if len(results) == 0:
            raise exceptions.EntryDoesNotExist()
        return results
