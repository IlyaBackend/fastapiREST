from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class EssenceBase(BaseModel):
    """Базовая схема сущностей."""

    name: str = Field(..., max_length=255)
    quantity: int = Field(..., ge=0)
    is_done: bool = Field(False)

    model_config = ConfigDict(extra='forbid')


class EssenceCreate(EssenceBase):
    """Схема для создания новой записи."""


class EssenceReplace(EssenceBase):
    """Схема для полного замещения/обновления PUT."""


class EssenceUpdate(BaseModel):
    """Схема для частичного обновления сущности."""

    name: Optional[str] = Field(None, max_length=255)
    quantity: Optional[int] = Field(None, ge=0)
    is_done: Optional[bool] = None

    model_config = ConfigDict(extra='forbid')


class EssenceOut(EssenceBase):
    """Схема для показа сущностей."""

    id: int

    model_config = ConfigDict(from_attributes=True)
