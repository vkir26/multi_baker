import sqlite3
import csv
from pathlib import Path
from dataclasses import dataclass


def read_csv(filepath: Path) -> list[dict[str, str]]:
    with open(filepath, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        return list(reader)


@dataclass(frozen=True, slots=True)
class Request:
    query: str
    data: list[dict[str, str]] | None


def connect_db(query: str, data: list[dict[str, str]] | None = None) -> None:
    with sqlite3.connect(db_file) as connect:
        request = Request(query=query, data=data)
        execute_request(cursor=connect.cursor(), request=request)


def execute_request(cursor: sqlite3.Cursor, request: Request) -> None:
    if request.data:
        for data in request.data:
            cursor.execute(request.query, tuple(data.values()))
    else:
        cursor.execute(request.query)


if __name__ == "__main__":
    create_baker = """ CREATE TABLE IF NOT EXISTS multi_baker(id INTEGER PRIMARY KEY, models TEXT NOT NULL, panels TEXT NOT NULL) """
    insert_baker = """ INSERT INTO multi_baker (id, models, panels) VALUES(?, ?, ?) """
    csv_file = Path("files/multi_baker.csv")
    db_file = Path("files/multi_baker.db")
    connect_db(query=create_baker)
    connect_db(query=insert_baker, data=read_csv(csv_file))
