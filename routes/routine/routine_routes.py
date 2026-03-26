
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from models.routine.routine_models import Routine
from db import get_db

router = APIRouter()

# Pydantic models for request/response
class TaskModel(BaseModel):
	task_id: int
	task_name: str
	task_description: Optional[str] = None
	status: str

class RoutineCreate(BaseModel):
	date: date
	admin_id: int
	employee_id: int
	tasks: List[TaskModel]

class RoutineUpdate(BaseModel):
	date: Optional[date] = None
	tasks: Optional[List[TaskModel]] = None

# Admin: Create routine
@router.post('/admin/routine/', status_code=201)
def create_routine(routine: RoutineCreate, db: Session = Depends(get_db)):
	db_routine = Routine(
		date=routine.date,
		admin_id=routine.admin_id,
		employee_id=routine.employee_id,
		tasks=[task.dict() for task in routine.tasks]
	)
	db.add(db_routine)
	db.commit()
	db.refresh(db_routine)
	return db_routine

# Admin: Update routine
@router.put('/admin/routine/{routine_id}')
def update_routine(routine_id: int, routine: RoutineUpdate, db: Session = Depends(get_db)):
	db_routine = db.query(Routine).filter(Routine.routine_id == routine_id).first()
	if not db_routine:
		raise HTTPException(status_code=404, detail='Routine not found')
	if routine.date:
		db_routine.date = routine.date
	if routine.tasks:
		db_routine.tasks = [task.dict() for task in routine.tasks]
	db.commit()
	db.refresh(db_routine)
	return db_routine

# Admin: Fetch all routines for their employees (optionally by date)
@router.get('/admin/routines/', response_model=List[dict])
def fetch_routines(admin_id: int, date_query: Optional[date] = None, db: Session = Depends(get_db)):
	query = db.query(Routine).filter(Routine.admin_id == admin_id)
	if date_query:
		query = query.filter(Routine.date == date_query)
	routines = query.all()
	return [
		{
			'routine_id': r.routine_id,
			'date': r.date,
			'admin_id': r.admin_id,
			'employee_id': r.employee_id,
			'tasks': r.tasks,
			'created_at': r.created_at,
			'updated_at': r.updated_at
		} for r in routines
	]

# Admin: Delete routine
@router.delete('/admin/routine/{routine_id}')
def delete_routine(routine_id: int, db: Session = Depends(get_db)):
	db_routine = db.query(Routine).filter(Routine.routine_id == routine_id).first()
	if not db_routine:
		raise HTTPException(status_code=404, detail='Routine not found')
	db.delete(db_routine)
	db.commit()
	return {'detail': 'Routine deleted'}

# Employee: Fetch their own routines (optionally by date)
@router.get('/employee/routines/', response_model=List[dict])
def fetch_employee_routines(employee_id: int, date_query: Optional[date] = None, db: Session = Depends(get_db)):
	query = db.query(Routine).filter(Routine.employee_id == employee_id)
	if date_query:
		query = query.filter(Routine.date == date_query)
	routines = query.all()
	return [
		{
			'routine_id': r.routine_id,
			'date': r.date,
			'admin_id': r.admin_id,
			'employee_id': r.employee_id,
			'tasks': r.tasks,
			'created_at': r.created_at,
			'updated_at': r.updated_at
		} for r in routines
	]

# Employee: Update their own routine tasks (mark done/not done)
class TaskStatusUpdate(BaseModel):
	task_id: int
	status: str  # e.g., 'done', 'not done', 'in progress'

@router.put('/employee/routine/{routine_id}/update-task-status')
def update_task_status_employee(routine_id: int, update: TaskStatusUpdate, db: Session = Depends(get_db)):
	db_routine = db.query(Routine).filter(Routine.routine_id == routine_id).first()
	if not db_routine:
		raise HTTPException(status_code=404, detail='Routine not found')
	tasks = db_routine.tasks or []
	found = False
	for task in tasks:
		if task.get('task_id') == update.task_id:
			task['status'] = update.status
			found = True
			break
	if not found:
		raise HTTPException(status_code=404, detail='Task not found in routine')
	db_routine.tasks = tasks
	db.commit()
	db.refresh(db_routine)
	return db_routine