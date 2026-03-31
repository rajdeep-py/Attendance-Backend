from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from models.break_time.break_time_models import BreakTime
from models.attendance.attendance_models import Attendance
from models.onboarding.employee_models import EmployeeUser
from db import get_db
from datetime import datetime
import os

router = APIRouter()

UPLOAD_DIR = "uploads/break_time"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper: get active attendance session
def get_active_attendance(db, employee_id):
	return db.query(Attendance).filter(
		Attendance.employee_id == employee_id,
		Attendance.check_in_time != None,
		Attendance.check_out_time == None
	).order_by(Attendance.check_in_time.desc()).first()

# Break check-in
@router.post("/break-time/check-in/{employee_id}")
async def break_check_in(
	employee_id: int,
	photo: UploadFile = File(...),
	db: Session = Depends(get_db)
):
	# Ensure employee exists
	employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id).first()
	if not employee:
		raise HTTPException(status_code=404, detail="Employee not found")
	# Ensure active attendance session
	attendance = get_active_attendance(db, employee_id)
	if not attendance:
		raise HTTPException(status_code=400, detail="No active attendance session for break")
	# Ensure no active break
	active_break = db.query(BreakTime).filter(
		BreakTime.attendance_id == attendance.attendance_id,
		BreakTime.break_in_time != None,
		BreakTime.break_out_time == None
	).first()
	if active_break:
		raise HTTPException(status_code=400, detail="Already on a break")
	# Save selfie
	now = datetime.utcnow()
	date_str = now.date().isoformat()
	dir_path = os.path.join(UPLOAD_DIR, str(employee_id), date_str)
	os.makedirs(dir_path, exist_ok=True)
	ext = os.path.splitext(photo.filename)[1].lower() if photo.filename else ".jpg"
	if ext not in [".jpg", ".jpeg", ".png"]:
		ext = ".jpg"
	photo_path = os.path.join(dir_path, f"break_in_selfie{ext}")
	contents = await photo.read()
	with open(photo_path, "wb") as f:
		f.write(contents)
	# Create break record
	break_time = BreakTime(
		attendance_id=attendance.attendance_id,
		employee_id=employee_id,
		admin_id=employee.admin_id,
		break_in_time=now,
		break_in_photo=photo_path
	)
	db.add(break_time)
	db.commit()
	db.refresh(break_time)
	return {"message": "Break check-in successful", "break_id": break_time.break_id, "break_in_time": str(break_time.break_in_time)}

# Break check-out
@router.post("/break-time/check-out/{employee_id}")
async def break_check_out(
	employee_id: int,
	photo: UploadFile = File(...),
	db: Session = Depends(get_db)
):
	# Ensure employee exists
	employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id).first()
	if not employee:
		raise HTTPException(status_code=404, detail="Employee not found")
	# Ensure active attendance session
	attendance = get_active_attendance(db, employee_id)
	if not attendance:
		raise HTTPException(status_code=400, detail="No active attendance session for break")
	# Find active break
	break_time = db.query(BreakTime).filter(
		BreakTime.attendance_id == attendance.attendance_id,
		BreakTime.break_in_time != None,
		BreakTime.break_out_time == None
	).order_by(BreakTime.break_in_time.desc()).first()
	if not break_time:
		raise HTTPException(status_code=400, detail="No active break to check out from")
	# Save selfie
	now = datetime.utcnow()
	date_str = break_time.break_in_time.date().isoformat() if break_time.break_in_time else now.date().isoformat()
	dir_path = os.path.join(UPLOAD_DIR, str(employee_id), date_str)
	os.makedirs(dir_path, exist_ok=True)
	ext = os.path.splitext(photo.filename)[1].lower() if photo.filename else ".jpg"
	if ext not in [".jpg", ".jpeg", ".png"]:
		ext = ".jpg"
	photo_path = os.path.join(dir_path, f"break_out_selfie{ext}")
	contents = await photo.read()
	with open(photo_path, "wb") as f:
		f.write(contents)
	# Update break record
	break_time.break_out_time = now
	break_time.break_out_photo = photo_path
	db.commit()
	db.refresh(break_time)
	return {"message": "Break check-out successful", "break_id": break_time.break_id, "break_out_time": str(break_time.break_out_time)}

# Admin fetch breaks for employee
@router.get("/break-time/admin/{admin_id}/employee/{employee_id}")
def get_breaks_by_admin_and_employee(admin_id: int, employee_id: int, db: Session = Depends(get_db)):
	return db.query(BreakTime).filter(BreakTime.admin_id == admin_id, BreakTime.employee_id == employee_id).all()

# Employee fetch own breaks
@router.get("/break-time/employee/{employee_id}")
def get_breaks_by_employee(employee_id: int, db: Session = Depends(get_db)):
	return db.query(BreakTime).filter(BreakTime.employee_id == employee_id).all()
