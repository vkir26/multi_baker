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


def read_from_csv(filepath: Path) -> DataTables:
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


if __name__ == "__main__":
    csv_file = Path("files/multi_baker.csv")
    data_tables = read_from_csv(csv_file)

    connect_db(table_name="multi_baker", columns="model", data=data_tables.models)
    connect_db(table_name="panel", columns="model_id, panel", data=data_tables.panels)

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
