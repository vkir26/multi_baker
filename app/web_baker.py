from fastapi import FastAPI, HTTPException, APIRouter, Depends
from pydantic import BaseModel, Field
from database import MultiBaker, insert_data, get_baking_dish
from database import (
    get_bakers,
    get_baker,
    get_baking_tins,
    BakerWithPanels,
    BakerView,
)

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Добро пожаловать в сервис Мультипекарей"}


router_v1 = APIRouter(prefix="/v1")


class RequestPagination(BaseModel):
    page: int | None = Field(None, ge=1)


class ModelsResponse(BaseModel):
    models: list[BakerView]
    page_number: int | None


class PanelsResponse(BaseModel):
    panels: list[BakerView]
    page_number: int | None


@router_v1.get("/model")
def get_model(by_id: int) -> BakerWithPanels:
    baker = get_baker(baker_id=by_id)
    if baker is None:
        raise HTTPException(status_code=400, detail="Модель не найдена")
    return baker


@router_v1.get("/panel")
def get_panel(by_id: int) -> str:
    panel = get_baking_dish(panel_id=by_id)
    if panel is None:
        raise HTTPException(status_code=400, detail="Панель не найдена")
    return str(panel)


@router_v1.get("/models", response_model=ModelsResponse)
def get_models(request: RequestPagination = Depends()) -> ModelsResponse:
    page = request.page
    page_size = 3
    return ModelsResponse(
        models=get_bakers(page=page, limit=page_size), page_number=page
    )


@router_v1.get("/panels", response_model=PanelsResponse)
def get_panels(request: RequestPagination = Depends()) -> PanelsResponse:
    page = request.page
    page_size = 3
    return PanelsResponse(
        panels=get_baking_tins(page=page, limit=page_size), page_number=page
    )


class AddModel(BaseModel):
    name: str
    panels: list[str] = Field(default_factory=list)


class AddModelResponse(BaseModel):
    name: str
    status: str


@router_v1.post("/model/add")
def add_model(request: AddModel) -> AddModelResponse:
    baker = MultiBaker(model=request.name, panels=request.panels)
    insert_data(baker=baker)
    return AddModelResponse(name=request.name, status="успешно добавлена")


app.include_router(router_v1)
