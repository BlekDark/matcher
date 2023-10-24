from src.repo import AbstractRepository
import src.exceptions as exceptions


class ResultRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get(self, *args, **kwargs):
        results = await self.session.fetch("SELECT * FROM matcher.results")
        return results

    async def create(self, *args, **kwargs):
        if not (kwargs.get('run_id', None) and
                kwargs.get('event1', None) and
                kwargs.get('event2', None)):
            raise exceptions.InvalidParameters()

        insert_query = "INSERT INTO matcher.results as r ( " + ",".join([f"{k}" for k in kwargs.keys()]) \
                       + ") VALUES ( " + ",".join([f"${i + 1}" for i in range(len(kwargs))]) + ") RETURNING id"
        data_to_insert = tuple(kwargs.values())
        result = await self.session.fetch(insert_query, *data_to_insert)
        return result[0]['id']

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

        check_query = "SELECT EXISTS(SELECT 1 FROM matcher.results as r WHERE r.id = $1)"
        check_query = await self.session.fetch(check_query, id)

        if check_query[0]['exists']:
            update_query = "UPDATE matcher.results as r SET " + ", ".join(
                [f"{col} = ${i + 2}" for i, col in enumerate(columns)]) + " WHERE r.id = $1"

            await self.session.fetch(update_query, id, *values)
            return True
        else:
            raise exceptions.EntryDoesNotExist()

    async def delete(self, *args, **kwargs):
        if not (kwargs.get('id', None)):
            raise exceptions.InvalidParameters()

        cursor = self.session.cursor()
        attribute_name = 'id'
        attribute_value = kwargs.get(attribute_name)

        select_query = f"SELECT * FROM matcher.results as r WHERE {attribute_name} = $1"
        delete_query = f"DELETE FROM matcher.results as r WHERE {attribute_name} = $1"

        results = await self.session.fetch(select_query, attribute_value)

        if len(results) != 0:
            results = await self.session.fetch(delete_query, attribute_value)
            return True
        else:
            raise exceptions.EntryDoesNotExist(f'No entry with {attribute_name}={attribute_value}')

    async def get_by_id(self, entry_id: int, *args, **kwargs):
        result = await self.session.fetch("SELECT * FROM matcher.results as r WHERE r.id = $1", entry_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result

    async def get_by_run_id(self, run_id: int):
        results = await self.session.fetch(
            'SELECT r.id, r.event1 , r.event2 , r.is_match, r.mismatch, \
             r.overall_similarity, r.teams_similarity, r.league_similarity, r.is_swapped  FROM matcher.results r WHERE r.run_id = $1',
            run_id)
        return results

    async def get_task(self, result_id: int):
        select_query = 'SELECT r2.task_id FROM matcher.runs r2 WHERE r2.id = (SELECT r.run_id FROM matcher.results r WHERE r.id = $1)'
        result = await self.session.fetch(select_query, result_id)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result[0]['task_id']

    async def get_manual_matches(self):
        raw_whitelist = await self.session.fetch("""select
                                                    r.event1->>'team1' as event1_team1,
                                                    r.event1->>'team2' as event1_team2,
                                                    r.event1->>'league_name' as event1_league,
                                                    r.event2->>'team1' as event2_team1,
                                                    r.event2->>'team2' as event2_team2, 
                                                    r.event2->>'league_name' as event2_league,
                                                    r.is_swapped,
                                                    r.event1->>'event_name' as event1_name,
                                                    r.event2->>'event_name' as event2_name,
                                                    r.id as result_id
                                                    from matcher.results r where r.is_match  = true and r.mismatch is not null  """)

        raw_banlist = await self.session.fetch("""  select
                                                    r.event1->>'team1' as event1_team1,
                                                    r.event1->>'team2' as event1_team2,
                                                    r.event1->>'league_name' as event1_league,
                                                    r.event2->>'team1' as event2_team1,
                                                    r.event2->>'team2' as event2_team2, 
                                                    r.event2->>'league_name' as event2_league,
                                                    r.is_swapped,
                                                    r.event1->>'event_name' as event1_name,
                                                    r.event2->>'event_name' as event2_name,
                                                    r.id as result_id
                                                from matcher.results r where r.is_match  = false""")
        return raw_whitelist, raw_banlist

