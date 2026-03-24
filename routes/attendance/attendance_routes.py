from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.attendance.attendance_models import Attendance, AttendanceStatusEnum
from models.location_matrix.location_matrix_models import LocationMatrix
from db import get_db
from datetime import datetime
import os
from typing import Optional

router = APIRouter()

UPLOAD_DIR = "uploads/attendance"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper to check if location is within allowed radius (in meters)
def is_within_radius(lat1, lon1, lat2, lon2, radius=10):
    from math import radians, cos, sin, asin, sqrt
    # Haversine formula
    R = 6371000  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    distance = R * c
    return distance <= radius

# Employee check-in
@router.post("/attendance/check-in/{employee_id}")
async def check_in(
    employee_id: int,
    latitude: float = File(...),
    longitude: float = File(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Get employee's admin_id
    from models.onboarding.employee_models import EmployeeUser
    employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    admin_id = employee.admin_id
    # Get allowed locations for admin
    allowed_locations = db.query(LocationMatrix).filter(LocationMatrix.admin_id == admin_id).all()
    if not allowed_locations:
        raise HTTPException(status_code=400, detail="No allowed locations set by admin")
    # Check if current location is within any allowed location (100m radius)
    valid = any(is_within_radius(latitude, longitude, loc.latitude, loc.longitude) for loc in allowed_locations)
    if not valid:
        raise HTTPException(status_code=403, detail="Current location not allowed for check-in")
    # Save photo
    now = datetime.utcnow()
    date_str = now.date().isoformat()
    dir_path = os.path.join(UPLOAD_DIR, str(employee_id), date_str)
    os.makedirs(dir_path, exist_ok=True)
    ext = os.path.splitext(photo.filename)[1].lower() if photo.filename else ".jpg"
    if ext not in [".jpg", ".jpeg", ".png"]:
        ext = ".jpg"
    photo_path = os.path.join(dir_path, f"check_in_selfie{ext}")
    contents = await photo.read()
    with open(photo_path, "wb") as f:
        f.write(contents)
    # Create attendance record
    attendance = Attendance(
        admin_id=admin_id,
        employee_id=employee_id,
        date=now.date(),
        check_in_time=now,
        check_in_photo=photo_path,
        check_in_latitude=latitude,
        check_in_longitude=longitude,
        status=AttendanceStatusEnum.present
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return {"message": "Check-in successful", "attendance_id": attendance.attendance_id, "status": attendance.status.value, "date": str(attendance.date)}

# Employee check-out
@router.post("/attendance/check-out/{employee_id}")
async def check_out(
    employee_id: int,
    latitude: float = File(...),
    longitude: float = File(...),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Get latest attendance record for employee (not checked out)
    attendance = db.query(Attendance).filter(Attendance.employee_id == employee_id, Attendance.check_out_time == None).order_by(Attendance.check_in_time.desc()).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="No active check-in found")
    # Get employee's admin_id
    from models.onboarding.employee_models import EmployeeUser
    employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    admin_id = employee.admin_id
    # Get allowed locations for admin
    allowed_locations = db.query(LocationMatrix).filter(LocationMatrix.admin_id == admin_id).all()
    if not allowed_locations:
        raise HTTPException(status_code=400, detail="No allowed locations set by admin")
    # Check if current location is within any allowed location (100m radius)
    valid = any(is_within_radius(latitude, longitude, loc.latitude, loc.longitude) for loc in allowed_locations)
    if not valid:
        raise HTTPException(status_code=403, detail="Current location not allowed for check-out")
    # Save photo
    now = datetime.utcnow()
    date_str = attendance.date.isoformat() if hasattr(attendance, 'date') and attendance.date else now.date().isoformat()
    dir_path = os.path.join(UPLOAD_DIR, str(employee_id), date_str)
    os.makedirs(dir_path, exist_ok=True)
    ext = os.path.splitext(photo.filename)[1].lower() if photo.filename else ".jpg"
    if ext not in [".jpg", ".jpeg", ".png"]:
        ext = ".jpg"
    photo_path = os.path.join(dir_path, f"check_out_selfie{ext}")
    contents = await photo.read()
    with open(photo_path, "wb") as f:
        f.write(contents)
    # Update attendance record
    attendance.check_out_time = datetime.utcnow()
    attendance.check_out_photo = photo_path
    attendance.check_out_latitude = latitude
    attendance.check_out_longitude = longitude
    db.commit()
    db.refresh(attendance)
    return {"message": "Check-out successful", "attendance_id": attendance.attendance_id, "status": attendance.status.value, "date": str(attendance.date)}

# Admin fetch attendance for their employees
@router.get("/attendance/admin/{admin_id}/employee/{employee_id}")
def get_attendance_by_admin_and_employee(admin_id: int, employee_id: int, db: Session = Depends(get_db)):
    return db.query(Attendance).filter(Attendance.admin_id == admin_id, Attendance.employee_id == employee_id).all()

# Get all attendance records by employee_id
@router.get("/attendance/employee/{employee_id}")
def get_attendance_by_employee(employee_id: int, db: Session = Depends(get_db)):
    return db.query(Attendance).filter(Attendance.employee_id == employee_id).all()

# Update attendance status by admin
class AttendanceStatusUpdate(BaseModel):
    status: str  # present or absent

@router.put("/attendance/{attendance_id}/admin/{admin_id}/status")
def update_attendance_status(attendance_id: int, admin_id: int, update: AttendanceStatusUpdate, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.attendance_id == attendance_id, Attendance.admin_id == admin_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    if update.status not in [e.value for e in AttendanceStatusEnum]:
        raise HTTPException(status_code=400, detail="Invalid status value")
    attendance.status = AttendanceStatusEnum(update.status)
    db.commit()
    db.refresh(attendance)
    return {"message": "Attendance status updated", "attendance_id": attendance.attendance_id, "status": attendance.status.value}
