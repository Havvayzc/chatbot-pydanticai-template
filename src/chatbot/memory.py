"""
Extension point: Conversational memory (chat history).

This module provides a default in-process store that persists messages to a
SQLite file. The agent uses this history so it can refer to earlier messages
in the conversation.

To use a different backend (e.g. Redis, PostgreSQL, or an in-memory-only
store for tests), replace the implementation of ChatMemory or the methods
get_messages / add_messages so they read/write from your store. The API
expected by the FastAPI app is: get_messages() -> list[ModelMessage],
add_messages(messages: bytes) -> None.
"""

from __future__ import annotations

import asyncio
import sqlite3
from collections.abc import AsyncIterator, Callable
from concurrent.futures.thread import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Any, ParamSpec, TypeVar

from pydantic_ai import ModelMessage, ModelMessagesTypeAdapter

P = ParamSpec("P")
R = TypeVar("R")

# Default path for the SQLite DB (one file per app instance; you can change this).
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / ".chat_messages.sqlite"


@dataclass
class ChatMemory:
    """
    Simple persistent chat history using SQLite.

    We run SQLite in a thread pool because it's synchronous; this keeps the
    async FastAPI handlers non-blocking.
    """

    con: sqlite3.Connection
    _loop: asyncio.AbstractEventLoop
    _executor: ThreadPoolExecutor

    @classmethod
    @asynccontextmanager
    async def connect(cls, file: Path = DEFAULT_DB_PATH) -> AsyncIterator[ChatMemory]:
        """Create a connection to the message store. Use as async context manager."""
        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=1)
        con = await loop.run_in_executor(executor, cls._connect, file)
        store = cls(con, loop, executor)
        try:
            yield store
        finally:
            await store._asyncify(con.close)

    @staticmethod
    def _connect(file: Path) -> sqlite3.Connection:
        con = sqlite3.connect(str(file))
        cur = con.cursor()
        # One row per "batch" of messages (one user + one model reply). We append
        # new batches so we can replay the full conversation in order.
        cur.execute(
            "CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, message_list TEXT NOT NULL)"
        )
        con.commit()
        return con

    async def add_messages(self, messages: bytes) -> None:
        """Append a batch of messages (JSON bytes from result.new_messages_json())."""
        await self._asyncify(
            self._execute,
            "INSERT INTO messages (message_list) VALUES (?);",
            messages,
            commit=True,
        )

    async def get_messages(self) -> list[ModelMessage]:
        """Load full conversation history as a list of ModelMessage."""
        cur = await self._asyncify(
            self._execute,
            "SELECT message_list FROM messages ORDER BY id",
        )
        rows = await self._asyncify(cur.fetchall)
        out: list[ModelMessage] = []
        for row in rows:
            out.extend(ModelMessagesTypeAdapter.validate_json(row[0]))
        return out

    def _execute(
        self, sql: str, *args: Any, commit: bool = False
    ) -> sqlite3.Cursor:
        cur = self.con.cursor()
        cur.execute(sql, args)
        if commit:
            self.con.commit()
        return cur

    async def _asyncify(
        self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
    ) -> R:
        return await self._loop.run_in_executor(
            self._executor,
            partial(func, *args, **kwargs),
        )
