from src.repo import AbstractRepository
import src.exceptions as exceptions
import json
from asyncpg.exceptions import UniqueViolationError
import logging

logger = logging.getLogger("backend-matcher")


class CustomMatchRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    async def get_custom_results(self, unmatched):

        if unmatched:
            select_query = f'SELECT DISTINCT ON (event1, event2) * FROM matcher.custom_unmatched_data'
        else:
            select_query = f'SELECT DISTINCT ON (event1, event2) * FROM matcher.custom_data'

        results = await self.session.fetch(select_query)
        return results

    # async def save_all_data(self, **kwargs):
    #     event1 = json.dumps(kwargs.get('event1', None))
    #     event2 = json.dumps(kwargs.get('event2', None))
    #     overall_similarity = kwargs.get('overall_similarity', None)
    #     teams_similarity = kwargs.get('teams_similarity', None)
    #     league_similarity = kwargs.get('league_similarity', None)
    #     sport = kwargs.get('sport', None)
    #     is_cyber = bool(kwargs.get('is_cyber', None))
    #     is_swapped = kwargs.get('is_swapped', None)
    #     is_match = kwargs.get('is_match', None)
    #
    #     insert_query = f"INSERT INTO matcher.custom_data as c (event1, event2, overall_similarity, teams_similarity, " \
    #                    f"league_similarity, sport, is_cyber, is_swapped, is_match) " \
    #                    f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
    #     result = await self.session.fetchval(insert_query, event1, event2, overall_similarity, teams_similarity,
    #                                          league_similarity, sport, is_cyber, is_swapped, is_match)
    #     return result
    #
    # async def save_unmatched_data(self, **kwargs):
    #     event1 = json.dumps(kwargs.get('event1', None))
    #     event2 = json.dumps(kwargs.get('event2', None))
    #     overall_similarity = kwargs.get('overall_similarity', None)
    #     teams_similarity = kwargs.get('teams_similarity', None)
    #     league_similarity = kwargs.get('league_similarity', None)
    #     sport = kwargs.get('sport', None)
    #     is_cyber = bool(kwargs.get('is_cyber', None))
    #     is_swapped = kwargs.get('is_swapped', None)
    #     is_match = kwargs.get('is_match', None)
    #
    #     insert_query = f"INSERT INTO matcher.custom_unmatched_data as c (event1, event2, overall_similarity, teams_similarity, " \
    #                    f"league_similarity, sport, is_cyber, is_swapped, is_match) " \
    #                    f"VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"
    #     result = await self.session.fetchval(insert_query, event1, event2, overall_similarity, teams_similarity,
    #                                          league_similarity, sport, is_cyber, is_swapped, is_match)
    #     return result

    async def save_all_data(self, processed_date, **kwargs):
        event1 = kwargs.get('event1', None)
        event2 = kwargs.get('event2', None)
        event1_id = event1.get('event_id', None) if event1 else None
        event2_id = event2.get('event_id', None) if event2 else None
        event1 = json.dumps(event1)
        event2 = json.dumps(event2)
        overall_similarity = kwargs.get('overall_similarity', None)
        teams_similarity = kwargs.get('teams_similarity', None)
        league_similarity = kwargs.get('league_similarity', None)
        sport = kwargs.get('sport', None)
        is_cyber = bool(kwargs.get('is_cyber', None))
        is_swapped = kwargs.get('is_swapped', None)
        is_match = kwargs.get('is_match', None)
        mismatch = kwargs.get('mismatch', None)

        insert_query = f"""
            INSERT INTO matcher.custom_matched_data
            (date, event1, event2, event1_id, event2_id, overall_similarity, teams_similarity, league_similarity, sport, is_cyber, is_swapped, is_match, mismatch) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """
        try:
            result = await self.session.fetchval(insert_query, processed_date, event1, event2, event1_id, event2_id,
                                                 overall_similarity, teams_similarity, league_similarity, sport,
                                                 is_cyber, is_swapped, is_match, mismatch)
            return result
        except UniqueViolationError:
            await self.session.execute('ROLLBACK')
            logger.warning(f"Pair with event1_id: {event1_id} and event2_id: {event2_id} already exists. Skipping.")

    async def save_unmatched_data(self, processed_date, **kwargs):
        event_id = kwargs.get('event_id', None)
        sport = kwargs.get('sport', None)
        event_name = kwargs.get('event_name', None)
        team1 = kwargs.get('team1', None)
        team2 = kwargs.get('team2', None)
        league_name = kwargs.get('league_name', None)
        is_cyber = bool(kwargs.get('is_cyber', None))

        insert_query = f"""
                    INSERT INTO matcher.custom_unmatched_data
                    (date, event_id, sport, event_name, team1, team2, league_name, is_cyber) 
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    """
        try:
            result = await self.session.fetchval(insert_query, processed_date, event_id, sport, event_name, team1,
                                                 team2, league_name, is_cyber)
            return result
        except UniqueViolationError:
            await self.session.execute('ROLLBACK')
            logger.warning(f"Result with event_id: {event_id} already exist. Skipping.")

    async def get_matched_results(self, date):
        select_query = 'SELECT * FROM matcher.custom_matched_data'
        if date:
            select_query += ' WHERE date=$1'
            results = await self.session.fetch(select_query, date)
        else:
            results = await self.session.fetch(select_query)
        return results

    async def get_unmatched_results(self, date):
        select_query = 'SELECT * FROM matcher.custom_unmatched_data'
        if date:
            select_query += ' WHERE date=$1'
            results = await self.session.fetch(select_query, date)
        else:
            results = await self.session.fetch(select_query)
        return results

    async def get_processed_data_info(self):
        select_query = 'SELECT * FROM matcher.processed_data_info'
        return await self.session.fetch(select_query)


    async def get_processed_data_info_by_id(self, hash):
        if not hash:
            raise exceptions.InvalidParameters('No id or type values to delete are provided!')
        result = await self.session.fetch('SELECT * FROM matcher.processed_data_info WHERE hash = $1', hash)
        if not result:
            raise exceptions.EntryDoesNotExist()
        return result


    async def save_processed_data_info(self, sha256_hash, process_start, process_end, **kwargs):
        total_pairs_sent = kwargs.get('total_pairs_sent', 0)
        correct_matches = kwargs.get('correct_matches', 0)
        mismatched_pairs = kwargs.get('mismatches', 0)
        unmatched_results = kwargs.get('unmatched', 0)

        correct_matches_percentage = f'{round(correct_matches / total_pairs_sent * 100, 2)}%'
        mismatched_pairs_percentage = f'{round(mismatched_pairs / total_pairs_sent * 100, 2)}%'
        unmatched_pairs_percentage = f'{round(unmatched_results / total_pairs_sent * 100, 2)}%'

        insert_query = f"""
                    INSERT INTO matcher.processed_data_info
                    (hash, total_pairs_sent, correct_matches, mismatched_pairs, unmatched_results, correct_matches_percentage, mismatched_pairs_percentage, unmatched_pairs_percentage, process_start, process_end) 
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """
        result = await self.session.fetchval(insert_query, sha256_hash, total_pairs_sent, correct_matches, mismatched_pairs, unmatched_results, correct_matches_percentage, mismatched_pairs_percentage, unmatched_pairs_percentage, process_start, process_end)
        return result

    async def save_custom_match_start_info(self, sha256_hash, process_start):
        insert_query = f"""
                    INSERT INTO matcher.processed_data_info
                    (hash, process_start) 
                    VALUES ($1, $2)
                    """
        result = await self.session.fetchval(insert_query, sha256_hash, process_start)
        return result

    async def save_custom_match_end_info(self, sha256_hash, process_end, **kwargs):
        total_pairs_sent = kwargs.get('total_pairs_sent', 0)
        correct_matches = kwargs.get('correct_matches', 0)
        mismatched_pairs = kwargs.get('mismatches', 0)
        unmatched_results = kwargs.get('unmatched', 0)

        correct_matches_percentage = f'{round(correct_matches / total_pairs_sent * 100, 2)}%'
        mismatched_pairs_percentage = f'{round(mismatched_pairs / total_pairs_sent * 100, 2)}%'
        unmatched_pairs_percentage = f'{round(unmatched_results / total_pairs_sent * 100, 2)}%'

        update_query = """
                          UPDATE matcher.processed_data_info
                          SET total_pairs_sent = $2,
                              correct_matches = $3,
                              mismatched_pairs = $4,
                              unmatched_results = $5,
                              correct_matches_percentage = $6,
                              mismatched_pairs_percentage = $7,
                              unmatched_pairs_percentage = $8,
                              process_end = $9
                          WHERE hash = $1
                          """
        result = await self.session.fetchval(update_query, sha256_hash, total_pairs_sent, correct_matches, mismatched_pairs, unmatched_results, correct_matches_percentage, mismatched_pairs_percentage, unmatched_pairs_percentage, process_end)
        return result

    async def save_test_matcher_metadata(self, **kwargs):
        task_id = kwargs.get('task_id')
        remove_candidate_threshold = kwargs.get('remove_candidate_threshold')
        confident_threshold = kwargs.get('confident_threshold')
        minimal_sim_threshold = kwargs.get('minimal_sim_threshold')
        final_sim_ratio = kwargs.get('final_sim_ratio')
        bk1_event_count = kwargs.get('bk1_event_count')
        bk2_event_count = kwargs.get('bk2_event_count')
        all_event_count = kwargs.get('all_event_count')

        insert_query = f"""
                        INSERT INTO matcher.test_matcher_metadata
                        (task_id, remove_candidate_threshold, confident_threshold, minimal_sim_threshold, final_sim_ratio, bk1_event_count, bk2_event_count, all_event_count) 
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                        """
        result = await self.session.fetchval(insert_query, task_id, remove_candidate_threshold, confident_threshold, minimal_sim_threshold, final_sim_ratio, bk1_event_count, bk2_event_count, all_event_count)
        return result

    async def get_test_matcher_metadata(self, task_id):
        select_query = 'SELECT remove_candidate_threshold, confident_threshold, minimal_sim_threshold, ' \
                       'final_sim_ratio, bk1_event_count, bk2_event_count, all_event_count FROM matcher.test_matcher_metadata as tmm WHERE tmm.task_id = $1'

        results = await self.session.fetch(select_query, task_id)
        return results

    async def truncate_tables(self):
        truncate_query = """
                         TRUNCATE TABLE matcher.custom_matched_data, matcher.custom_unmatched_data RESTART IDENTITY CASCADE
                         """
        result = await self.session.fetchval(truncate_query)
        return result

