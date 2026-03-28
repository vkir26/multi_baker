from fastapi import FastAPI, HTTPException
from database import (
    get_bakers,
    get_baker,
    get_baking_tins,
    get_baking_dish,
    BakerWithPanels,
    BakerView,
)

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Добро пожаловать в сервис Мультипекарей"}


@app.get("/model")
def get_model(by_id: int) -> BakerWithPanels:
    baker = get_baker(baker_id=by_id)
    if len(baker.model) == 0:
        raise HTTPException(status_code=400, detail="Модель не найдена")
    return baker


@app.get("/panel")
def get_panel(by_id: int) -> str:
    panel = get_baking_dish(panel_id=by_id)
    if panel is None:
        raise HTTPException(status_code=400, detail="Панель не найдена")
    return panel


def check_pages(page: int | None, page_size: int, number_records: int) -> bool:
    if page is not None:
        total_pages = (number_records + page_size - 1) // page_size
        return page > total_pages or page <= 0
    return False


@app.get("/models")
def get_models(page: int | None = None) -> list[BakerView]:
    page_size = 3
    total_bakers = len(get_bakers())
    if check_pages(page=page, page_size=page_size, number_records=total_bakers):
        raise HTTPException(status_code=404)
    return get_bakers(page=page, limit=page_size)


@app.get("/panels")
def get_panels(page: int | None = None) -> list[BakerView]:
    page_size = 3
    total_panels = len(get_baking_tins())
    if check_pages(page=page, page_size=page_size, number_records=total_panels):
        raise HTTPException(status_code=404)
    return get_baking_tins(page=page, limit=page_size)
