from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import date, time
from models.break_time.break_time_models import BreakTime, BreakStatusEnum
from db import get_db

router = APIRouter()

# Pydantic Schemas
class BreakTimeCreate(BaseModel):
	admin_id: int
	employee_id: int
	date: date
	start_time: time
	end_time: time

class BreakTimeUpdate(BaseModel):
	date: Optional[date] = None
	start_time: Optional[time] = None
	end_time: Optional[time] = None
	status: Optional[BreakStatusEnum] = None

# Assign break time (Admin assigns to employee)
@router.post("/break-time/assign", response_model=dict)
def assign_break_time(break_data: BreakTimeCreate, db: Session = Depends(get_db)):
	break_time = BreakTime(**break_data.dict())
	db.add(break_time)
	db.commit()
	db.refresh(break_time)
	return {"message": "Break time assigned", "break_id": break_time.break_id}

# Get all break times for an admin (all employees)
@router.get("/break-time/admin/{admin_id}", response_model=List[dict])
def get_break_times_by_admin(admin_id: int, db: Session = Depends(get_db)):
	breaks = db.query(BreakTime).filter(BreakTime.admin_id == admin_id).all()
	return [
		{
			"break_id": b.break_id,
			"employee_id": b.employee_id,
			"date": b.date,
			"start_time": b.start_time,
			"end_time": b.end_time,
			"status": b.status,
			"created_at": b.created_at,
			"updated_at": b.updated_at
		} for b in breaks
	]

# Get all break times for an employee (by employee_id)
@router.get("/break-time/employee/{employee_id}", response_model=List[dict])
def get_break_times_by_employee(employee_id: int, db: Session = Depends(get_db)):
	breaks = db.query(BreakTime).filter(BreakTime.employee_id == employee_id).all()
	return [
		{
			"break_id": b.break_id,
			"admin_id": b.admin_id,
			"date": b.date,
			"start_time": b.start_time,
			"end_time": b.end_time,
			"status": b.status,
			"created_at": b.created_at,
			"updated_at": b.updated_at
		} for b in breaks
	]

# Update break time (admin or employee can update status or times)
@router.put("/break-time/{break_id}", response_model=dict)
def update_break_time(break_id: int, update_data: BreakTimeUpdate, db: Session = Depends(get_db)):
	break_time = db.query(BreakTime).filter(BreakTime.break_id == break_id).first()
	if not break_time:
		raise HTTPException(status_code=404, detail="Break time not found")
	for field, value in update_data.dict(exclude_unset=True).items():
		setattr(break_time, field, value)
	db.commit()
	db.refresh(break_time)
	return {"message": "Break time updated", "break_id": break_time.break_id}

# Delete break time (admin only)
@router.delete("/break-time/{break_id}/admin/{admin_id}", response_model=dict)
def delete_break_time(break_id: int, admin_id: int, db: Session = Depends(get_db)):
	break_time = db.query(BreakTime).filter(BreakTime.break_id == break_id, BreakTime.admin_id == admin_id).first()
	if not break_time:
		raise HTTPException(status_code=404, detail="Break time not found or unauthorized")
	db.delete(break_time)
	db.commit()
	return {"message": "Break time deleted"}
