import sqlite3
from pathlib import Path
from dataclasses import dataclass
from sqlite3 import Cursor

filepath_db = Path("files/multi_baker.db")


def insert_data(data: dict[str, list[str]]) -> None:
    try:
        with sqlite3.connect(filepath_db) as connect:
            cursor = connect.cursor()
            for model, panels in data.items():
                cursor.execute(
                    """ INSERT INTO multi_baker (model)
                                   VALUES (?) """,
                    (model,),
                )
                model_id = cursor.lastrowid
                for panel in panels:
                    cursor.execute(
                        """ INSERT INTO panel (model_id, panel)
                                       VALUES (?, ?) """,
                        (model_id, panel),
                    )
    except sqlite3.Error as e:
        print(f"Ошибка: {e}")


def data_request(query: str) -> Cursor:
    with sqlite3.connect(filepath_db) as connect:
        cursor = connect.cursor()
        return cursor.execute(query)


@dataclass(frozen=True, slots=True)
class BakerView:
    id: int
    model: str


def get_bakers() -> list[BakerView]:
    request = data_request(
        query=""" SELECT id, model
                                     FROM multi_baker """
    )
    return [BakerView(id=id_model, model=model) for id_model, model in request]


@dataclass(frozen=True, slots=True)
class BakerWithPanels:
    model: str | None
    panels: list[str]


def get_baker(baker_id: int) -> BakerWithPanels:
    request = data_request(
        query=f""" SELECT mb.id, model, panel FROM multi_baker mb JOIN panel p ON p.model_id = mb.id WHERE mb.id = {baker_id}"""
    )
    baker = None
    panels = []
    for model_id, model, panel in request:
        if baker is None:
            baker = model
        panels.append(panel)
    return BakerWithPanels(model=baker, panels=panels)
