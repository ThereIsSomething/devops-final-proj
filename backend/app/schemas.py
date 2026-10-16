from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EquipmentInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    name: str = Field(min_length=1, max_length=120)
    category: str = Field(min_length=1, max_length=60)
    quantity: int = Field(ge=0, le=1_000_000, strict=True)
    low_stock_threshold: int = Field(ge=0, le=1_000_000, strict=True)
    location: str = Field(min_length=1, max_length=120)


class EquipmentOut(EquipmentInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class Summary(BaseModel):
    records: int
    units: int
    low_stock: int
    categories: list[str]
