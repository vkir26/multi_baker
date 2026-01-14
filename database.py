import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import TypedDict

filepath = Path("files/multi_baker.db")


def insert_panels(cursor: sqlite3.Cursor, panels: set[str]) -> dict[str, int]:
    panel_id: dict[str, int] = {}
    for panel in panels:
        cursor.execute(
            """ INSERT INTO panel (panel)
                VALUES (?) """,
            (panel,),
        )
        rowid = cursor.lastrowid
        if rowid is None:
            raise RuntimeError("Не удалось получить id панели")
        panel_id[panel] = rowid
    return panel_id


class MultiBaker(TypedDict):
    model: str
    panels: list[str]


def insert_data(data: list[MultiBaker]) -> None:
    try:
        with sqlite3.connect(filepath) as connect:
            cursor = connect.cursor()
            unique_panels = {panel for baker in data for panel in baker["panels"]}
            panels_id: dict[str, int] = insert_panels(
                cursor=cursor, panels=unique_panels
            )
            for baker in data:
                cursor.execute(
                    """ INSERT INTO multi_baker (model)
                        VALUES (?) """,
                    (baker["model"],),
                )
                model_id = cursor.lastrowid
                for panel in baker["panels"]:
                    panel_id = panels_id[panel]
                    cursor.execute(
                        """ INSERT INTO model_panel (model_id, panel_id)
                            VALUES (?, ?) """,
                        (model_id, panel_id),
                    )
    except sqlite3.Error as e:
        print(f"Ошибка: {e}")


def get_cursor() -> sqlite3.Cursor:
    with sqlite3.connect(filepath) as connect:
        return connect.cursor()


@dataclass(frozen=True, slots=True)
class BakerView:
    id: int
    model: str


def get_bakers() -> list[BakerView]:
    cursor = get_cursor()
    request = cursor.execute(""" SELECT id, model FROM multi_baker """)
    return [BakerView(id=id_model, model=model) for id_model, model in request]


@dataclass(frozen=True, slots=True)
class BakerWithPanels:
    model: str
    panels: list[str]


def get_baker(baker_id: int) -> BakerWithPanels:
    cursor = get_cursor()
    request = cursor.execute(
        """ SELECT model, panel
                                 FROM multi_baker mb
                                          JOIN model_panel mp ON mb.id = mp.model_id
                                          JOIN panel p ON p.id = mp.panel_id
                                 WHERE mb.id = ?; """,
        f"{baker_id}",
    )

    baker = set()
    panels = []
    for model, panel in request:
        baker.add(model)
        panels.append(panel)
    return BakerWithPanels(model="".join(baker), panels=panels)
