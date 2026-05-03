from fastapi import FastAPI, HTTPException, APIRouter, Depends, status
from pydantic import BaseModel, Field
from database import MultiBaker, insert_data, get_panel_by_id
from database import (
    get_baker,
    get_models_page,
    get_panels_page,
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
    page_size: int = Field(3, ge=1)


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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Модель не найдена"
        )
    return baker


@router_v1.get("/panel")
def get_panel(by_id: int) -> str:
    panel = get_panel_by_id(panel_id=by_id)
    if panel is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Панель не найдена"
        )
    return str(panel)


@router_v1.get("/models", response_model=ModelsResponse)
def get_models(request: RequestPagination = Depends()) -> ModelsResponse:
    page = request.page
    page_size = request.page_size
    return ModelsResponse(
        models=get_models_page(page=page, limit=page_size), page_number=page
    )


@router_v1.get("/panels", response_model=PanelsResponse)
def get_panels(request: RequestPagination = Depends()) -> PanelsResponse:
    page = request.page
    page_size = request.page_size
    return PanelsResponse(
        panels=get_panels_page(page=page, limit=page_size), page_number=page
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
