from database import connect_db, get_bakers, get_baker
import csv
from pathlib import Path
from dataclasses import dataclass
from menu import Menu


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


def build_insert(table_name: str, columns: str) -> str:
    split_columns = ", ".join("?" * len(columns.split(",")))
    return insert.format(table_name, columns, split_columns)


if __name__ == "__main__":
    csv_file = Path("files/multi_baker.csv")
    data_tables = write_from_csv(csv_file)
    create = """ CREATE TABLE IF NOT EXISTS {} (id INTEGER PRIMARY KEY, {}) """
    insert = """ INSERT INTO {} ({}) VALUES ({}) """

    connect_db(query=create.format("multi_baker", "models TEXT NOT NULL UNIQUE"))
    connect_db(
        query=build_insert(table_name="multi_baker", columns="models"),
        data=data_tables.models,
    )
    connect_db(
        query=create.format(
            "panels",
            "model_id INT NOT NULL, panels TEXT NOT NULL, "
            "FOREIGN KEY (model_id) REFERENCES multi_baker(id)",
        )
    )
    connect_db(
        query=build_insert(table_name="panels", columns="model_id, panels"),
        data=data_tables.panels,
    )

    while True:
        print("Выберете меню:")
        for menu in Menu:
            print(f"{menu}. {menu.message()}")
        try:
            select_menu = int(input("Ввод: "))
            match Menu(select_menu):
                case Menu.BAKER_MODEL:
                    select_model = int(input("Укажите ID модели: "))
                    multi_baker = get_baker(select_model)
                    if multi_baker.model is not None:
                        print(multi_baker)
                case Menu.BAKER_ALL:
                    for baker in get_bakers():
                        print(baker)
        except ValueError:
            print("Не найдено")
