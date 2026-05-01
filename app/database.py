import sqlite3
from http import HTTPStatus
from pathlib import Path
from dataclasses import dataclass
from typing import cast

ROOT_DIR = Path(__file__).resolve().parent.parent
filepath = ROOT_DIR / "files" / "multi_baker.db"


def insert_panels(cursor: sqlite3.Cursor, panels: set[str]) -> dict[str, int]:
    panel_id: dict[str, int] = {}
    for panel in panels:
        try:
            cursor.execute(
                """ INSERT INTO panel (panel)
                    VALUES (?) """,
                (panel,),
            )
            rowid = cursor.lastrowid
            if rowid:
                panel_id[panel] = rowid

        except sqlite3.IntegrityError:
            cursor.execute(
                """ SELECT id
                               FROM panel
                               WHERE panel = ? """,
                (panel,),
            )
            row = cursor.fetchone()
            if row:
                panel_id[panel] = row[0]
    return panel_id


@dataclass(frozen=True, slots=True)
class MultiBaker:
    model: str
    panels: list[str]


def insert_models(cursor: sqlite3.Cursor, model: str) -> int | None:
    cursor.execute(
        """ INSERT INTO multi_baker (model)
            VALUES (?) """,
        (model,),
    )
    model_id = cursor.lastrowid
    return model_id


def insert_data(baker: MultiBaker) -> None:
    try:
        with sqlite3.connect(filepath) as connect:
            cursor = connect.cursor()

            model_id = insert_models(cursor=cursor, model=baker.model)
            unique_panels = {panel for panel in baker.panels}
            panels_id: dict[str, int] = insert_panels(
                cursor=cursor, panels=unique_panels
            )
            for panel in unique_panels:
                panel_id = panels_id[panel]
                cursor.execute(
                    """ INSERT INTO model_panel (model_id, panel_id)
                        VALUES (?, ?) """,
                    (model_id, panel_id),
                )
    except sqlite3.Error as e:
        raise sqlite3.Error(f"{HTTPStatus.SERVICE_UNAVAILABLE.phrase}. {e}")


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
    with sqlite3.connect(filepath) as connect:
        cursor = connect.cursor()

    params = get_page_params(page=page, limit=limit)
    if params:
        request += " LIMIT ? OFFSET ?"
    return [
        BakerView(id=name_id, name=name)
        for name_id, name in cursor.execute(request, params)
    ]


def get_models_page(page: int | None, limit: int) -> list[BakerView]:
    request = """ SELECT id, model
                  FROM multi_baker """
    return get_data_multibakers(request=request, page=page, limit=limit)


def get_panels_page(page: int | None, limit: int) -> list[BakerView]:
    request = """ SELECT id, panel
                  FROM panel """
    return get_data_multibakers(request=request, page=page, limit=limit)


@dataclass(frozen=True, slots=True)
class BakerWithPanels:
    model: str
    panels: list[str]


def get_baker(baker_id: int) -> BakerWithPanels | None:
    with sqlite3.connect(filepath) as connect:
        cursor = connect.cursor()

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


def get_panel_by_id(panel_id: int) -> str | None:
    with sqlite3.connect(filepath) as connect:
        cursor = connect.cursor()

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
