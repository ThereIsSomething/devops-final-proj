import logging

from fastapi import Depends, FastAPI, HTTPException, Query, Response, status
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import Equipment
from .schemas import EquipmentInput, EquipmentOut, Summary

logger = logging.getLogger("labshelf")
app = FastAPI(title="LabShelf API", version=settings.app_version)
Instrumentator(excluded_handlers=["/metrics", "/health", "/ready"]).instrument(app).expose(app)


@app.get("/health")
def health():
    return {"status": "UP", "version": settings.app_version}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1 FROM equipment LIMIT 1"))
    except SQLAlchemyError:
        logger.warning("Database readiness check failed")
        raise HTTPException(status_code=503, detail="Database unavailable") from None
    return {"status": "READY"}


@app.get("/api/summary", response_model=Summary)
def summary(db: Session = Depends(get_db)):
    records, units = db.execute(
        select(func.count(Equipment.id), func.coalesce(func.sum(Equipment.quantity), 0))
    ).one()
    low_stock = db.scalar(
        select(func.count(Equipment.id)).where(
            Equipment.quantity <= Equipment.low_stock_threshold
        )
    )
    categories = list(db.scalars(select(Equipment.category).distinct().order_by(Equipment.category)))
    return Summary(records=records, units=units, low_stock=low_stock, categories=categories)


@app.get("/api/equipment", response_model=list[EquipmentOut])
def list_equipment(
    q: str = Query(default="", max_length=120),
    category: str = Query(default="", max_length=60),
    low_stock: bool = False,
    db: Session = Depends(get_db),
):
    query = select(Equipment)
    if q.strip():
        query = query.where(or_(
            Equipment.name.icontains(q.strip(), autoescape=True),
            Equipment.location.icontains(q.strip(), autoescape=True),
        ))
    if category:
        query = query.where(Equipment.category == category)
    if low_stock:
        query = query.where(Equipment.quantity <= Equipment.low_stock_threshold)
    return list(db.scalars(query.order_by(Equipment.id.desc())))


def find_equipment(db: Session, equipment_id: int) -> Equipment:
    equipment = db.get(Equipment, equipment_id)
    if equipment is None:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return equipment


@app.get("/api/equipment/{equipment_id}", response_model=EquipmentOut)
def get_equipment(equipment_id: int, db: Session = Depends(get_db)):
    return find_equipment(db, equipment_id)


@app.post("/api/equipment", response_model=EquipmentOut, status_code=status.HTTP_201_CREATED)
def create_equipment(payload: EquipmentInput, db: Session = Depends(get_db)):
    equipment = Equipment(**payload.model_dump())
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    logger.info("Created equipment id=%s", equipment.id)
    return equipment


@app.put("/api/equipment/{equipment_id}", response_model=EquipmentOut)
def update_equipment(equipment_id: int, payload: EquipmentInput, db: Session = Depends(get_db)):
    equipment = find_equipment(db, equipment_id)
    for field, value in payload.model_dump().items():
        setattr(equipment, field, value)
    db.commit()
    db.refresh(equipment)
    logger.info("Updated equipment id=%s", equipment.id)
    return equipment


@app.delete("/api/equipment/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment(equipment_id: int, db: Session = Depends(get_db)):
    equipment = find_equipment(db, equipment_id)
    db.delete(equipment)
    db.commit()
    logger.info("Deleted equipment id=%s", equipment_id)
    return Response(status_code=204)
