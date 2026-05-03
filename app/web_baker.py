from fastapi import FastAPI, HTTPException, Form, Request, APIRouter, Depends
from pydantic import BaseModel, Field
from starlette.templating import _TemplateResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from database import MultiBaker, insert_data, get_baking_dish
from typing import Annotated
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
    panels: str


class AddModelResponse(BaseModel):
    name: str
    status: str


@router_v1.get("/model/add", response_class=HTMLResponse)
def create_model(request: Request) -> _TemplateResponse:
    templates = Jinja2Templates(directory="templates")
    return templates.TemplateResponse(name="create_model.html", request=request)


@router_v1.post("/model/add")
def insert_model(request: Annotated[AddModel, Form(max_length=15)]) -> AddModelResponse:
    data = [MultiBaker(model=request.name, panels=request.panels.split(","))]
    insert_data(data=data)
    return AddModelResponse(name=request.name, status="успешно добавлена")


app.include_router(router_v1)
