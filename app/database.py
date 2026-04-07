import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import TypedDict, cast
from fastapi import HTTPException

ROOT_DIR = Path(__file__).resolve().parent.parent
filepath = ROOT_DIR / "files" / "multi_baker.db"


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
        raise HTTPException(status_code=503, detail=f"Ошибка: {e}")


def get_cursor() -> sqlite3.Cursor:
    with sqlite3.connect(filepath) as connect:
        return connect.cursor()


@dataclass(frozen=True, slots=True)
class BakerView:
    id: int
    name: str


def get_page_params(page: int | None, limit: int) -> list[int]:
    params = []

    if page is not None:
        offset = (page - 1) * limit
        params.extend([limit, offset])
    return params


def get_data_multibakers(request: str, page: int | None, limit: int) -> list[BakerView]:
    cursor = get_cursor()

    params = get_page_params(page=page, limit=limit)
    if params:
        request += " LIMIT ? OFFSET ?"
    return [
        BakerView(id=name_id, name=name)
        for name_id, name in cursor.execute(request, params)
    ]


def get_bakers(page: int | None, limit: int) -> list[BakerView]:
    request = """ SELECT id, model
                  FROM multi_baker """
    return get_data_multibakers(request=request, page=page, limit=limit)


def get_baking_tins(page: int | None, limit: int) -> list[BakerView]:
    request = """ SELECT id, panel
                  FROM panel """
    return get_data_multibakers(request=request, page=page, limit=limit)


@dataclass(frozen=True, slots=True)
class BakerWithPanels:
    model: str
    panels: list[str]


def get_baker(baker_id: int) -> BakerWithPanels | None:
    cursor = get_cursor()
    request = cursor.execute(
        """ SELECT model, panel
            FROM multi_baker mb
                     JOIN model_panel mp ON mb.id = mp.model_id
                     JOIN panel p ON p.id = mp.panel_id
            WHERE mb.id = ?; """,
        (baker_id,),
    )

    baker = set()
    panels = []
    for model, panel in request:
        baker.add(model)
        panels.append(panel)
    multi_baker = BakerWithPanels(model="".join(baker), panels=panels)
    if len(multi_baker.model) == 0:
        return None
    return BakerWithPanels(model="".join(baker), panels=panels)


def get_baking_dish(panel_id: int) -> str | None:
    cursor = get_cursor()
    request = cursor.execute(
        """ SELECT panel
            FROM panel
            WHERE id = ?; """,
        (panel_id,),
    )
    row = cast(tuple[str] | None, request.fetchone())
    if row:
        return row[0]
    return None
