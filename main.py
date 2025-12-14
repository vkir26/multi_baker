import sqlite3
import click
from pathlib import Path
from enum import StrEnum
from multi_baker import read_from_csv
from database import (
    connect_db,
    get_bakers,
    get_baker
)


class Command(StrEnum):
    PARSE = "parse",
    BY_ID = "by_id",
    MODELS = "models"


def fill_database() -> None:
    connect_db(table_name="multi_baker",
               columns="model",
               data=data_tables.models)
    connect_db(table_name="panel",
               columns="model_id, panel",
               data=data_tables.panels)


@click.command()
@click.option(f'--{Command.PARSE}', is_flag=True, help='Заполнить базу данных из CSV.')
@click.option(f'--{Command.BY_ID}', help='Поиск модели по ID.', type=int)
@click.option(f'--{Command.MODELS}', is_flag=True, help='Все доступные модели.')
def main(**kwargs) -> None:
    """Сервис мультипекарей."""
    for command, value in kwargs.items():
        if value is not None and value != False:
            match command:
                case Command.PARSE:
                    fill_database()
                case Command.BY_ID:
                    click.echo(get_baker(value))
                case Command.MODELS:
                    click.echo("Список доступных моделей:")
                    for baker in get_bakers():
                        click.echo(baker)


if __name__ == '__main__':
    csv_file = Path("files/multi_baker.csv")
    data_tables = read_from_csv(csv_file)
    try:
        main()
    except sqlite3.OperationalError as e:
        print(f"Ошибка: {e}")
