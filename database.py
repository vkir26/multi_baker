import sqlite3
from pathlib import Path
from dataclasses import dataclass

filepath_db = Path("files/multi_baker.db")


@dataclass(frozen=True, slots=True)
class Request:
    query: str
    data: set[str] | list[dict[int, str]] | None


def connect_db(query: str, data: set[str] | list[dict[int, str]] | None = None) -> None:
    with sqlite3.connect(filepath_db) as connect:
        request = Request(query=query, data=data)
        execute_request(cursor=connect.cursor(), request=request)


def execute_request(cursor: sqlite3.Cursor, request: Request) -> None:
    if request.data:
        for data in request.data:
            if isinstance(data, dict):
                cursor.execute(request.query, tuple(*data.items()))
            else:
                cursor.execute(request.query, (data,))
    else:
        cursor.execute(request.query)
