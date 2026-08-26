from __future__ import annotations

from typing import ContextManager, Protocol


class UnitOfWork(Protocol):
    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class UnitOfWorkFactory(Protocol):
    def __call__(self) -> ContextManager[UnitOfWork]: ...
