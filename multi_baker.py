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
