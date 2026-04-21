import csv
import click
from pathlib import Path
from app.database import (
    insert_data,
    get_bakers,
    get_baker,
    get_baking_dish,
    get_baking_tins,
    MultiBaker,
)


def read_from_csv(filepath: Path) -> list[MultiBaker]:
    with open(filepath, "r", newline="") as file_csv:
        reader = csv.DictReader(file_csv, delimiter=";")
        models: dict[str, list[str]] = {}
        for i in reader:
            model = i["model"]
            if model not in models:
                models[model] = []
            models[model].append(i["panel"])
        multi_bakers: list[MultiBaker] = [
            MultiBaker(model=model, panels=panels) for model, panels in models.items()
        ]
        return multi_bakers


@click.group()
def multi_baker() -> None:
    """Сервис мультипекарей."""
    pass


@multi_baker.command()
@click.option("--file", help="Парсинг файла и запись данных в БД")
def file_parse(file: str) -> None:
    csv_file = Path(file)
    if csv_file.is_file():
        for baker in read_from_csv(filepath=Path(file)):
            insert_data(baker=baker)
    else:
        click.echo("Файл не найден")


@multi_baker.command()
@click.option("--by_id", help="Поиск модели по ID.", type=int)
def get_model(by_id: int) -> None:
    baker = get_baker(baker_id=by_id)
    if baker:
        click.echo(baker)
    else:
        click.echo("Не найдено")


@multi_baker.command()
@click.option("--by_id", help="Поиск панели по ID.", type=int)
def get_panel(by_id: int) -> None:
    panel = get_baking_dish(panel_id=by_id)
    if panel:
        click.echo(panel)
    else:
        click.echo("Не найдено")


@multi_baker.command()
@click.option("--page", help="Номер страницы.", type=int)
def get_models(page: int) -> None:
    baker_models = get_bakers(page=page, limit=3)
    if baker_models:
        click.echo("Список моделей:")
        for baker in baker_models:
            click.echo(baker)
    else:
        click.echo("Не найдено")


@multi_baker.command()
@click.option("--page", help="Номер страницы.", type=int)
def get_panels(page: int) -> None:
    panels = get_baking_tins(page=page, limit=3)
    if panels:
        click.echo("Список панелей:")
        for panel in panels:
            click.echo(panel)
    else:
        click.echo("Не найдено")


@multi_baker.command()
@click.option("--model", help="Добавить модель.", type=str)
@click.option("--panel", help="Добавить панель.", type=str, multiple=True)
def add_model(model: str, panel: str) -> None:
    baker = MultiBaker(model=model, panels=list(panel))
    insert_data(baker=baker)
    click.echo(f"Модель: {model} - успешно добавлена")


def main() -> None:
    multi_baker()


if __name__ == "__main__":
    main()
