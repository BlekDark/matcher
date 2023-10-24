from typing import Protocol


class AbstractRepository(Protocol):

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def modify(self, *args, **kwargs):
        raise NotImplementedError

    def delete(self, *args, **kwargs):
        raise NotImplementedError

    def get_by_id(self, entry_id: int, *args, **kwargs):
        raise NotImplementedError
