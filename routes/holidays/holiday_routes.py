from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict
from models.holidays.holiday_models import Holiday
from db import get_db
from datetime import date

router = APIRouter()

class Occasion(BaseModel):
    title: str
    remarks: Optional[str] = None

class HolidayCreate(BaseModel):
    admin_id: int
    occasion: Occasion
    date: date

class HolidayUpdate(BaseModel):
    occasion: Optional[Occasion] = None
    date: Optional[date] = None

# Create holiday
@router.post("/holidays/post")
def create_holiday(data: HolidayCreate, db: Session = Depends(get_db)):
    holiday = Holiday(
        admin_id=data.admin_id,
        occasion=data.occasion.dict(),
        date=data.date
    )
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday
    return {"message": "Holiday created", "holiday_id": holiday.holiday_id}

# Get holiday by admin_id and holiday_id
@router.get("/get-holidays/{holiday_id}/admin/{admin_id}")
def get_holiday_by_admin_and_id(holiday_id: int, admin_id: int, db: Session = Depends(get_db)):
    holiday = db.query(Holiday).filter(Holiday.holiday_id == holiday_id, Holiday.admin_id == admin_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    return holiday

# Get all holidays by admin_id
@router.get("/get-holidays/admin/{admin_id}")
def get_holidays_by_admin(admin_id: int, db: Session = Depends(get_db)):
    return db.query(Holiday).filter(Holiday.admin_id == admin_id).all()

# Get all holidays
@router.get("/get-holidays/")
def get_all_holidays(db: Session = Depends(get_db)):
    return db.query(Holiday).all()

# Update holiday by admin_id and holiday_id
@router.put("/update-holidays/{holiday_id}/admin/{admin_id}")
def update_holiday(holiday_id: int, admin_id: int, update: HolidayUpdate, db: Session = Depends(get_db)):
    holiday = db.query(Holiday).filter(Holiday.holiday_id == holiday_id, Holiday.admin_id == admin_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    if update.occasion is not None:
        holiday.occasion = update.occasion.dict()
    if update.date is not None:
        holiday.date = update.date
    db.commit()
    db.refresh(holiday)
    return {"message": "Holiday updated", "holiday_id": holiday.holiday_id}

# Delete holiday by admin_id and holiday_id
@router.delete("/delete-holidays/{holiday_id}/admin/{admin_id}")
def delete_holiday(holiday_id: int, admin_id: int, db: Session = Depends(get_db)):
    holiday = db.query(Holiday).filter(Holiday.holiday_id == holiday_id, Holiday.admin_id == admin_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db.delete(holiday)
    db.commit()
    return {"message": "Holiday deleted"}
