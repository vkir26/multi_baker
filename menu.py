from enum import IntEnum
from typing import assert_never


class Menu(IntEnum):
    BAKER_MODEL = 1
    BAKER_ALL = 2

    def message(self) -> str:
        match self:
            case Menu.BAKER_MODEL:
                return "Указать ID модели"
            case Menu.BAKER_ALL:
                return "Доступные модели"
            case _ as unreachable_case:
                assert_never(unreachable_case)
