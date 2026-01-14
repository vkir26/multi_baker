import csv
import sqlite3
import click
from pathlib import Path
from database import insert_data, get_bakers, get_baker, MultiBaker


def read_from_csv(filepath: Path) -> list[MultiBaker]:
    with open(filepath, "r", newline="") as file_csv:
        reader = csv.DictReader(file_csv, delimiter=";")
        models: dict[str, list[str]] = {}
        for i in reader:
            model = i["models"]
            if model not in models:
                models[model] = []
            models[model].append(i["panels"])
        multi_bakers: list[MultiBaker] = [
            {"model": model, "panels": panels} for model, panels in models.items()
        ]
        return multi_bakers


def fill_database(data: list[MultiBaker]) -> None:
    try:
        insert_data(data=data)
    except sqlite3.OperationalError as e:
        print(f"Ошибка: {e}")


@click.group()
def multi_baker() -> None:
    """Сервис мультипекарей."""
    pass


@multi_baker.command()
@click.option("--file", help="Парсинг файла и запись данных в БД")
def file_parse(file: str) -> None:
    csv_file = Path(file)
    if csv_file.is_file():
        data = read_from_csv(filepath=Path(file))
        fill_database(data=data)
    else:
        click.echo("Файл не найден")


@multi_baker.command()
@click.option("--by_id", help="Поиск модели по ID.", type=int)
def get_model(by_id: int) -> None:
    baker = get_baker(baker_id=by_id)
    if baker.model:
        click.echo(baker)
    else:
        click.echo("Не найдено")


@multi_baker.command()
def get_models() -> None:
    baker_models = get_bakers()
    if baker_models:
        click.echo("Список доступных моделей:")
        for baker in baker_models:
            click.echo(baker)
    else:
        click.echo("Не найдено")


def main() -> None:
    multi_baker()


if __name__ == "__main__":
    main()
