from fastapi import FastAPI, HTTPException
from database import get_bakers, get_baker, BakerWithPanels, BakerView

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


@app.get("/models")
def get_models(page: int | None = None) -> list[BakerView]:
    page_size = 3
    total_pages = (len(get_bakers()) + page_size - 1) // page_size
    if page is not None:
        if page > total_pages or page <= 0:
            raise HTTPException(status_code=404)
    return get_bakers(page=page, limit=page_size)
