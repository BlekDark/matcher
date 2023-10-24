from src.uof import AbstractUnitOfWork
from src.repo import SourceRepository, SportsRepository, UserRepository, StatusRepository, PermissionRepository, \
    ParametersRepository, ConfigRepository, ResultRepository, RunRepository, TaskRepository, CustomMatchRepository
from src.config import DB_HOST, DB_NAME, DB_USER, DB_PASS
import psycopg2
import asyncpg
from asyncpg import create_pool


class PostgresUnitOfWork(AbstractUnitOfWork):
    def __init__(self, pool):
        self._pool = pool
        self.session = None
        self.transaction = None

    async def __aenter__(self):
        self.session = await self._pool.acquire()

        self.source_repo = SourceRepository(session=self.session)
        self.sport_repo = SportsRepository(session=self.session)
        self.user_repo = UserRepository(session=self.session)
        self.status_repo = StatusRepository(session=self.session)
        self.permission_repo = PermissionRepository(session=self.session)
        self.parameters_repo = ParametersRepository(session=self.session)
        self.config_repo = ConfigRepository(session=self.session)
        self.task_repo = TaskRepository(session=self.session)
        self.run_repo = RunRepository(session=self.session)
        self.result_repo = ResultRepository(session=self.session)
        self.custom_match_repo = CustomMatchRepository(session=self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.transaction:
            await self.transaction.rollback()
            self.transaction = None
        await self.session.close()
        self.session = None

    async def begin(self):
        self.transaction = self.session.transaction()
        await self.transaction.start()

    async def commit(self):
        if self.transaction:
            await self.transaction.commit()
            self.transaction = None

    async def rollback(self):
        if self.transaction:
            await self.transaction.rollback()
            self.transaction = None
