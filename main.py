import csv
import sqlite3
import click
from pathlib import Path
from database import insert_data, get_bakers, get_baker


def read_from_csv(filepath: Path) -> dict[str, list[str]]:
    with open(filepath, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        models: dict[str, list[str]] = {}
        for i in reader:
            model = i["models"]
            if model not in models:
                models[model] = []
            models[model].append(i["panels"])
        return models


def fill_database() -> None:
    try:
        insert_data(data=data)
    except sqlite3.OperationalError as e:
        print(f"Ошибка: {e}")


@click.group()
def multi_baker() -> None:
    """Сервис мультипекарей."""
    pass


@multi_baker.command()
@click.option("--parse", is_flag=True, help="Заполнить базу данных из CSV.")
def file_parse(parse: bool) -> None:
    fill_database()


@multi_baker.command()
@click.option("--by_id", help="Поиск модели по ID.", type=int)
def get_model(by_id: int) -> None:
    click.echo(get_baker(by_id))


@multi_baker.command()
@click.option("--all_models", is_flag=True, help="Все доступные модели.")
def get_models(all_models: bool) -> None:
    click.echo("Список доступных моделей:")
    for baker in get_bakers():
        click.echo(baker)


def main() -> None:
    multi_baker()


if __name__ == "__main__":
    csv_file = Path("files/multi_baker.csv")
    data = read_from_csv(csv_file)
    main()
