from src.repo import AbstractRepository
import src.exceptions as exceptions


class SourceRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.sources")
        return results

    async def create(self, *args, **kwargs):
        name = kwargs.get('name', None)
        url = kwargs.get('url', None)
        if not name or not url:
            raise exceptions.InvalidParameters()

        select_query = "SELECT * FROM matcher.sources as s WHERE s.name = $1"
        result_search_name = await self.session.fetch(select_query, name)

        # check if the data exists
        if not result_search_name:
            insert_query = "INSERT INTO matcher.sources as s (name, url) VALUES ($1, $2) RETURNING id"
            result = await self.session.fetch(insert_query, name, url)
            return result[0]['id']
        else:
            raise exceptions.EntryAlreadyExists(f"The entry with name={name} exists in the database!")

    async def modify(self, *args, **kwargs):
        id = kwargs.get('id', None)
        if not id or len(kwargs) < 2:  # помимо id должен быть как минимум еще 1 аргумент
            raise exceptions.InvalidParameters()

        columns = []
        values = []
        for col, val in kwargs.items():
            if col != 'id' and val is not None:
                columns.append(col)
                values.append(val)

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.sources as s WHERE s.id = $1)"
        check_query = await self.session.fetch(check_query, id)

        if check_query[0]['exists']:
            update_query = "UPDATE matcher.sources as s SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE s.id = $1"

            await self.session.fetch(update_query, id, *values)
            return True
        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        id = kwargs.get('id', None)
        name = kwargs.get('name', None)
        if not (id or name):
            raise exceptions.InvalidParameters('No id or name values to delete are provided!')

        attribute_name = 'id' if id else 'name'
        attribute_value = kwargs.get(attribute_name)

        select_query = f"SELECT * FROM matcher.sources as s WHERE {attribute_name} = $1"
        delete_query = f"DELETE FROM matcher.sources as s WHERE {attribute_name} = $1"

        results = await self.session.fetch(select_query, attribute_value)

        if len(results) != 0:
            results = await self.session.fetch(delete_query, attribute_value)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with {attribute_name}={attribute_value}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        result = await self.session.fetch(f"SELECT * FROM matcher.sources as s WHERE s.id = $1", entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result
