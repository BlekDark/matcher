from src.repo import AbstractRepository
import src.exceptions as exceptions


class PermissionRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.permissions")
        return results

    async def create(self, *args, **kwargs):
        type = kwargs.get('type', None)
        if not type:
            raise exceptions.InvalidParameters()

        select_query = "SELECT * FROM matcher.permissions as p WHERE p.type =  $1"
        result_search_type = await self.session.fetch(select_query, type)

        # check if the data exists
        if not result_search_type:
            insert_query = "INSERT INTO matcher.permissions as p (type) VALUES ($1) RETURNING id"
            result = await self.session.fetch(insert_query, type)
            return result[0]['id']
        else:
            raise exceptions.EntryAlreadyExists(f"The entry with type={kwargs.get('type')} exists in the database!")

    async def modify(self, *args, **kwargs):
        id_permission = kwargs.get('id', None)
        type_permission = kwargs.get('type', None)
        if not (id_permission and type_permission):
            raise exceptions.InvalidParameters()

        columns = []
        values = []
        for col, val in kwargs.items():
            if col != 'id' and val is not None:
                columns.append(col)
                values.append(val)

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.permissions as p WHERE p.id = $1)"
        check_query = await self.session.fetch(check_query, id_permission)

        if check_query[0]['exists']:
            update_query = "UPDATE matcher.permissions as p SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE p.id = $1"

            await self.session.fetch(update_query, id_permission, *values)
            return True
        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        id_permission = int(kwargs.get('id', None))
        type_permission = kwargs.get('type', None)
        if not (id_permission or type_permission):
            raise exceptions.InvalidParameters('No id or type values to delete are provided!')

        attribute_name = 'id' if id_permission else 'type'
        attribute_value = int(kwargs.get(attribute_name)) if attribute_name == 'id' else kwargs.get(attribute_name)

        select_query = f"SELECT * FROM matcher.permissions as p WHERE {attribute_name} = $1"
        delete_query = f"DELETE FROM matcher.permissions as p WHERE {attribute_name} = $1"

        results = await self.session.fetch(select_query, attribute_value)

        if len(results) != 0:
            results = await self.session.fetch(delete_query, attribute_value)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with {attribute_name}={attribute_value}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        result = await self.session.fetch("SELECT * FROM matcher.permissions as p WHERE p.id = $1", entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result
