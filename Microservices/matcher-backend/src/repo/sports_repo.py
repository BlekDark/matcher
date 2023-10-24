from src.repo import AbstractRepository
import src.exceptions as exceptions


class SportsRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.sport_types")
        return results


    async def create(self, *args, **kwargs):
        name = kwargs.get('name', None)
        is_cyber = kwargs.get('is_cyber', None)
        if not name or not is_cyber:
            raise exceptions.InvalidParameters()

        select_query = "SELECT * FROM matcher.sport_types as st WHERE st.name = $1 and st.is_cyber = $2"
        result_search_name = await self.session.fetch(select_query, name, is_cyber)

        # check if the data exists
        if not result_search_name:
            insert_query = "INSERT INTO matcher.sport_types as st (name, is_cyber) VALUES ($1, $2) RETURNING id"
            result = await self.session.fetch(insert_query, name, is_cyber)
            return result[0]['id']
        else:
            raise exceptions.EntryAlreadyExists(f"The entry with name={name} exists in the database!")

    async def modify(self, *args, **kwargs):
        id = kwargs.get('id', None)
        name = kwargs.get('name', None)
        if not (id and name):
            raise exceptions.InvalidParameters()

        columns = []
        values = []
        for col, val in kwargs.items():
            if col != 'id' and val is not None:
                columns.append(col)
                values.append(val)

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.sport_types as st WHERE s.id = $1)"
        check_query = await self.session.fetch(check_query, id)

        if check_query[0]['exists']:
            update_query = "UPDATE matcher.sport_types as st SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE st.id = $1"

            await self.session.fetch(update_query, id, *values)
            return True

        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        id = kwargs.get('id', None)
        name = kwargs.get('name', None)
        if not (id or name):
            raise exceptions.InvalidParameters('No id or name values to delete are provided!')

        select_query = "SELECT * FROM matcher.sport_types as st WHERE {} = $1"
        delete_query = "DELETE FROM matcher.sport_types as st WHERE {} = $1"

        attribute_name = 'id' if id else 'name'
        attribute_value = int(kwargs.get(attribute_name)) if attribute_name == 'id' else kwargs.get(attribute_name)

        results = await self.session.fetch(select_query, attribute_value)

        if len(results) != 0:
            results = await self.session.fetch(delete_query, attribute_value)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with {attribute_name}={attribute_value}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        result = await self.session.fetch(f"SELECT * FROM matcher.sport_types as st WHERE st.id = $1", entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result

    async def get_by_name(self, sport_name: str):
        result = await self.session.fetch(f"SELECT st.id FROM matcher.sport_types as st WHERE st.name = $1", sport_name)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result
