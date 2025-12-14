import sqlite3
from pathlib import Path
from dataclasses import dataclass
from sqlite3 import Cursor

filepath_db = Path("files/multi_baker.db")


def build_insert(table_name: str, columns: str) -> str:
    insert = """ INSERT INTO {} ({}) \
                 VALUES ({}) """
    split_columns = ", ".join("?" * len(columns.split(",")))
    return insert.format(table_name, columns, split_columns)


@dataclass(frozen=True, slots=True)
class Request:
    query: str
    data: set[str] | list[dict[int, str]] | None


def connect_db(
    table_name: str, columns: str, data: set[str] | list[dict[int, str]] | None = None
) -> None:
    query = build_insert(table_name=table_name, columns=columns)
    try:
        with sqlite3.connect(filepath_db) as connect:
            request = Request(query=query, data=data)
            execute_request(cursor=connect.cursor(), request=request)
    except sqlite3.Error as e:
        print(f"Ошибка: {e}")


def execute_request(cursor: sqlite3.Cursor, request: Request) -> None:
    if request.data:
        for data in request.data:
            if isinstance(data, dict):
                cursor.execute(request.query, tuple(*data.items()))
            else:
                cursor.execute(request.query, (data,))


def data_request(fields: str, table: str) -> Cursor:
    select = """ SELECT {}
                 FROM {} """
    with sqlite3.connect(filepath_db) as connect:
        cursor = connect.cursor()
        return cursor.execute(select.format(fields, table))


@dataclass(frozen=True, slots=True)
class BakerView:
    id: int
    model: str


def get_bakers() -> list[BakerView]:
    request = data_request(fields="id, model", table="multi_baker")
    return [BakerView(id=id_model, model=model) for id_model, model in request]


@dataclass(frozen=True, slots=True)
class BakerWithPanels:
    model: str | None
    panels: list[str]


def get_baker(baker_id: int) -> BakerWithPanels:
    request = data_request(
        fields="mb.id, model, panel",
        table="multi_baker mb JOIN panel p ON p.model_id = mb.id",
    )
    baker = None
    panels = []
    for model_id, model, panel in request:
        if model_id == baker_id:
            if baker is None:
                baker = model
            panels.append(panel)
    return BakerWithPanels(model=baker, panels=panels)
