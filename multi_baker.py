import sqlite3
import csv
from pathlib import Path
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DataTables:
    models: set[str]
    panels: list[dict[int, str]]


def get_id(models: set[str], panels_list: list[dict[str, str]]) -> list[dict[int, str]]:
    panels = []
    id_models = {model: num for num, model in enumerate(models, 1)}
    for panel in panels_list:
        for key, value in panel.items():
            panels.append({id_models[key]: value})
    return panels


def write_from_csv(filepath: Path) -> DataTables:
    with open(filepath, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        models = set()
        panels = []
        for i in reader:
            models.add(i["models"])
            panels.append({i["models"]: i["panels"]})
        return DataTables(
            models=models, panels=get_id(models=models, panels_list=panels)
        )


@dataclass(frozen=True, slots=True)
class Request:
    query: str
    data: set[str] | list[dict[int, str]] | None


def build_insert(table_name: str, columns: str) -> str:
    split_columns = ", ".join("?" * len(columns.split(",")))
    return insert.format(table_name, columns, split_columns)


def connect_db(
    filepath: Path, query: str, data: set[str] | list[dict[int, str]] | None = None
) -> None:
    with sqlite3.connect(filepath) as connect:
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


if __name__ == "__main__":
    csv_file = Path("files/multi_baker.csv")
    baker_table = Path("files/multi_baker.db")
    panel_table = Path("files/panels.db")
    data_tables = write_from_csv(csv_file)
    create = """ CREATE TABLE IF NOT EXISTS {}(id INTEGER PRIMARY KEY, {}) """
    insert = """ INSERT INTO {} ({}) VALUES({}) """

    connect_db(
        filepath=baker_table, query=create.format("multi_baker", "models TEXT NOT NULL")
    )
    connect_db(
        filepath=baker_table,
        query=build_insert(table_name="multi_baker", columns="models"),
        data=data_tables.models,
    )

    connect_db(
        filepath=panel_table,
        query=create.format("panels", "model_id INT NOT NULL, panels TEXT NOT NULL"),
    )
    connect_db(
        filepath=panel_table,
        query=build_insert(table_name="panels", columns="model_id, panels"),
        data=data_tables.panels,
    )
