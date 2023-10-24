from typing import Protocol


class AbstractUnitOfWork(Protocol):

    def __exit__(self, *args):
        raise NotImplementedError

    def commit(self):
        raise NotImplementedError

    def rollback(self):
        raise NotImplementedError

    def __enter__(self):
        pass
