import csv
from pathlib import Path
from dataclasses import dataclass, astuple


def read_file(filepath: Path) -> list[str]:
    with open(filepath, "r", encoding="UTF-8") as f:
        return [recording.strip() for recording in f]


@dataclass(frozen=True, slots=True)
class DataFields:
    id: int
    models: str
    panels: str


def write_db(filepath: Path, data: list[tuple[str]]) -> None:
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(DataFields.__annotations__)
        for recording in data:
            writer.writerow([*recording])


def compile_data(filepath: Path, data: list[str]) -> None:
    multi_baker = []
    id_model = 1
    for i in data:
        model, panels = i.split(" - ")
        for panel in panels.split(", "):
            multi_baker.append(
                astuple(DataFields(id=id_model, models=model, panels=panel))
            )
            id_model += 1
    write_db(filepath=filepath, data=multi_baker)


if __name__ == "__main__":
    file = Path("files/text.txt")
    storage_file = Path("files/multi_baker.csv")
    compile_data(filepath=storage_file, data=read_file(file))
