from src.repo import AbstractRepository
import src.exceptions as exceptions


class UserRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.users")
        return results

    async def create(self, *args, **kwargs):
        name = kwargs.get('name', None)
        permission_id = kwargs.get('permission_id', None)
        if not (name and permission_id):
            raise exceptions.InvalidParameters()

        select_query = "SELECT * FROM matcher.users as u WHERE u.name =  $1"
        result_search_type = await self.session.fetch(select_query, name)

        # check if the data exists
        if not result_search_type:
            insert_query = "INSERT INTO matcher.users as u (name, permission_id) VALUES ($1, $2) RETURNING id"
            result = await self.session.fetch(insert_query, name, int(permission_id))
            return result[0]['id']
        else:
            raise exceptions.EntryAlreadyExists(f"The entry with name={kwargs.get('name')} exists in the database!")

    async def modify(self, *args, **kwargs):
        user_id = kwargs.get('id', None)
        permission_id = kwargs.get('permission_id', None)
        name = kwargs.get('name', None)
        if not (user_id and permission_id and name):
            raise exceptions.InvalidParameters()

        columns = []
        values = []
        for col, val in kwargs.items():
            if col != 'id' and val is not None:
                columns.append(col)
                values.append(val)

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.users as u WHERE u.id = $1)"

        check_query = await self.session.fetch(check_query, user_id)

        if check_query[0]['exists']:
            update_query = "UPDATE matcher.users as s SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE s.id = $1"

            await self.session.fetch(update_query, user_id, *values)
            return True
        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        user_id = kwargs.get('id', None)
        name = kwargs.get('name', None)
        if not (user_id or name):
            raise exceptions.InvalidParameters('No id or name values to delete are provided!')

        attribute_name = 'id' if id else 'name'
        attribute_value = int(kwargs.get(attribute_name)) if attribute_name == 'id' else kwargs.get(attribute_name)

        select_query = f"SELECT * FROM matcher.users as u WHERE {attribute_name} = $1"
        delete_query = f"DELETE FROM matcher.users as u WHERE {attribute_name} = $1"

        results = await self.session.fetch(select_query, attribute_value)

        if len(results) != 0:
            results = await self.session.fetch(delete_query, attribute_value)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with {attribute_name}={attribute_value}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        result = await self.session.fetch("SELECT * FROM matcher.users as u WHERE u.id = $1", entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result

