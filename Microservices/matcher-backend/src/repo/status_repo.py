from src.repo import AbstractRepository
import src.exceptions as exceptions


class StatusRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.statuses")
        return results

    async def create(self, *args, **kwargs):
        status = kwargs.get('status', None)
        if not status:
            raise exceptions.InvalidParameters()
        select_query = "SELECT * FROM matcher.statuses as s WHERE s.status =  $1"
        result_search_type = await self.session.fetch(select_query, status)

        # check if the data exists
        if not result_search_type:
            insert_query = "INSERT INTO matcher.statuses as s (status) VALUES ($1) RETURNING id"
            result = await self.session.fetch(insert_query, status)
            return result[0]['id']
        else:
            raise exceptions.EntryAlreadyExists(f"The entry with status={kwargs.get('status')} exists in the database!")

    async def modify(self, *args, **kwargs):
        status_id = kwargs.get('id', None)
        status = kwargs.get('status', None)
        if not (status_id and status):
            raise exceptions.InvalidParameters()

        columns = []
        values = []
        for col, val in kwargs.items():
            if col != 'id' and val is not None:
                columns.append(col)
                values.append(val)

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.statuses as s WHERE s.id =  $1)"
        check_query = await self.session.fetch(check_query, status_id)

        if check_query[0]['exists']:
            update_query = "UPDATE matcher.statuses as s SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE s.id = $1"

            await self.session.fetch(update_query, status_id, *values)
            return True
        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        status_id = int(kwargs.get('id', None))
        status = kwargs.get('status', None)
        if not (status_id or status):
            raise exceptions.InvalidParameters('No id or name values to delete are provided!')

        attribute_name = 'id' if status_id else 'type'
        attribute_value = int(kwargs.get(attribute_name)) if attribute_name == 'id' else kwargs.get(attribute_name)

        select_query = f"SELECT * FROM matcher.statuses as s WHERE {attribute_name} = $1"
        delete_query = f"DELETE FROM matcher.statuses as s WHERE {attribute_name} = $1"

        results = await self.session.fetch(select_query, attribute_value)

        if len(results) != 0:
            results = await self.session.fetch(delete_query, attribute_value)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with {attribute_name}={attribute_value}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        result = await self.session.fetch("SELECT * FROM matcher.statuses as s WHERE s.id = $1", entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result
