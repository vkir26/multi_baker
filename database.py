import sqlite3
from pathlib import Path
from dataclasses import dataclass
from sqlite3 import Cursor

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


def data_request(fields: str, table: str) -> Cursor:
    select = """ SELECT {} FROM {} """
    with sqlite3.connect(filepath_db) as connect:
        cursor = connect.cursor()
        return cursor.execute(select.format(fields, table))


@dataclass(frozen=True, slots=True)
class BakerView:
    id: int
    model: str


def get_bakers() -> list[BakerView]:
    request = data_request(fields="id, models", table="multi_baker")
    return [BakerView(id=id_model, model=model) for id_model, model in request]


@dataclass(frozen=True, slots=True)
class BakerWithPanels:
    model: str | None
    panels: list[str]


def get_baker(baker_id: int) -> BakerWithPanels:
    request = data_request(
        fields="mb.id, models, panels",
        table="multi_baker mb JOIN panels p ON p.model_id = mb.id",
    )
    baker = None
    panels = []
    for model_id, model, panel in request:
        if model_id == baker_id:
            if baker is None:
                baker = model
            panels.append(panel)
    return BakerWithPanels(model=baker, panels=panels)
