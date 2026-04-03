from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.onboarding.employee_models import EmployeeUser
from models.attendance.attendance_models import Attendance
from models.break_time.break_time_models import BreakTime
from models.current_location.current_location_models import CurrentLocation
from models.leaves.leave_request_models import LeaveRequest
from models.salary_slip.salary_slip_models import SalarySlip
from db import get_db
import os
import shutil
from PIL import Image
from sqlalchemy.exc import IntegrityError
from fastapi import status
from typing import Optional
import secrets

router = APIRouter()

UPLOAD_DIR = "uploads/profile_photo"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _safe_remove_file(file_path: str | None) -> None:
    if not file_path:
        return
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except Exception:
        pass


def _safe_remove_dir(dir_path: str | None) -> None:
    if not dir_path:
        return
    try:
        shutil.rmtree(dir_path, ignore_errors=True)
    except Exception:
        pass


# Employee login model
class EmployeeLogin(BaseModel):
    phone_no: str
    password: str

class EmployeeCreate(BaseModel):
    admin_id: int
    full_name: str
    phone_no: str
    email: str
    address: str
    designation: str
    password: str
    bank_account_no: Optional[str] = None
    bank_name: Optional[str] = None
    branch_name: Optional[str] = None
    ifsc_code: Optional[str] = None

class EmployeeUpdate(BaseModel):
    full_name: str = None
    phone_no: str = None
    email: str = None
    address: str = None
    designation: str = None
    password: str = None
    bank_account_no: str = None
    bank_name: str = None
    branch_name: str = None
    ifsc_code: str = None


class EmployeeDeleteVerify(BaseModel):
    password: str

# Helper to save and compress profile photo
async def save_profile_photo(employee_id: int, full_name: str, file: UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".jpg", ".jpeg", ".png"]:
        raise HTTPException(status_code=400, detail="Invalid image format")
    dir_path = os.path.join(UPLOAD_DIR, str(employee_id))
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, f"{full_name}{ext}")
    # Remove old files
    for f in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, f))
    # Save and compress
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    img = Image.open(file_path)
    img = img.convert("RGB")
    img.save(file_path, optimize=True, quality=70)
    return file_path

# Create employee
@router.post("/login/employees/")
def login_employee(login: EmployeeLogin, db: Session = Depends(get_db)):
    employee = db.query(EmployeeUser).filter(EmployeeUser.phone_no == login.phone_no).first()
    if not employee or employee.password != login.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"message": "Login successful", "employee_id": employee.employee_id, "admin_id": employee.admin_id, "full_name": employee.full_name}


# Create employee
@router.post("/create/employees/")
async def create_employee(
    admin_id: int = Form(...),
    full_name: str = Form(...),
    phone_no: str = Form(...),
    email: str = Form(...),
    address: str = Form(...),
    designation: str = Form(...),
    password: str = Form(...),
    bank_account_no: Optional[str] = Form(None),
    bank_name: Optional[str] = Form(None),
    branch_name: Optional[str] = Form(None),
    ifsc_code: Optional[str] = Form(None),
    profile_photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    employee = EmployeeUser(
        admin_id=admin_id,
        full_name=full_name,
        phone_no=phone_no,
        email=email,
        address=address,
        designation=designation,
        password=password,
        bank_account_no=bank_account_no,
        bank_name=bank_name,
        branch_name=branch_name,
        ifsc_code=ifsc_code
    )
    db.add(employee)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() or "unique violation" in str(e).lower():
            raise HTTPException(status_code=400, detail="Phone number already registered")
        raise
    db.refresh(employee)
    if profile_photo:
        file_path = await save_profile_photo(employee.employee_id, full_name, profile_photo)
        employee.profile_photo = file_path
        db.commit()
        db.refresh(employee)
    return {"message": "Employee created", "employee_id": employee.employee_id}

# Get all employees by admin_id
@router.get("/get-all/employees/admin/{admin_id}")
def get_employees_by_admin(admin_id: int, db: Session = Depends(get_db)):
    return db.query(EmployeeUser).filter(EmployeeUser.admin_id == admin_id).all()

# Get employee by employee_id
@router.get("/get-by/employees/{employee_id}")
def get_employee_by_id(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# Update employee by employee_id (self-update)
@router.put("/update/employees/{employee_id}")
async def update_employee_by_id(
    employee_id: int,
    full_name: str = Form(None),
    phone_no: str = Form(None),
    email: str = Form(None),
    address: str = Form(None),
    designation: str = Form(None),
    password: str = Form(None),
    bank_account_no: str = Form(None),
    bank_name: str = Form(None),
    branch_name: str = Form(None),
    ifsc_code: str = Form(None),
    profile_photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    # Update fields
    for field, value in locals().items():
        if field in EmployeeUpdate.__annotations__ and value is not None:
            setattr(employee, field, value)
    # Handle profile photo
    if profile_photo:
        file_path = await save_profile_photo(employee.employee_id, employee.full_name, profile_photo)
        employee.profile_photo = file_path
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e).lower() or "unique violation" in str(e).lower():
            raise HTTPException(status_code=400, detail="Phone number already registered")
        raise
    db.refresh(employee)
    # Return the updated employee profile as dict
    return employee

# Update employee by admin_id and employee_id
@router.put("/update-by/employees/{employee_id}/admin/{admin_id}")
async def update_employee_by_admin(
    employee_id: int,
    admin_id: int,
    full_name: str = Form(None),
    phone_no: str = Form(None),
    email: str = Form(None),
    address: str = Form(None),
    designation: str = Form(None),
    password: str = Form(None),
    bank_account_no: str = Form(None),
    bank_name: str = Form(None),
    branch_name: str = Form(None),
    ifsc_code: str = Form(None),
    profile_photo: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id, EmployeeUser.admin_id == admin_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in locals().items():
        if field in EmployeeUpdate.__annotations__ and value is not None:
            setattr(employee, field, value)
    if profile_photo:
        file_path = await save_profile_photo(employee.employee_id, employee.full_name, profile_photo)
        employee.profile_photo = file_path
    db.commit()
    db.refresh(employee)
    return {"message": "Employee updated", "employee_id": employee.employee_id}

# Delete employee by admin_id and employee_id
@router.delete("/delete/employees/{employee_id}/admin/{admin_id}")
def delete_employee(
    employee_id: int,
    admin_id: int,
    verify: EmployeeDeleteVerify,
    db: Session = Depends(get_db),
):
    employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id, EmployeeUser.admin_id == admin_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Verify password before deleting
    stored_password = employee.password or ""
    if not secrets.compare_digest(stored_password, verify.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    cleanup_files: list[str] = []
    cleanup_dirs: list[str] = [
        os.path.join("uploads/profile_photo", str(employee.employee_id)),
        os.path.join("uploads/salary", str(employee.employee_id)),
        os.path.join("uploads/attendance", str(employee.employee_id)),
        os.path.join("uploads/break_time", str(employee.employee_id)),
    ]

    if employee.profile_photo:
        cleanup_files.append(employee.profile_photo)

    salary_slips = db.query(SalarySlip).filter(SalarySlip.employee_id == employee_id, SalarySlip.admin_id == admin_id).all()
    for slip in salary_slips:
        if slip.salary_slip_url:
            cleanup_files.append(slip.salary_slip_url)

    attendance_rows = db.query(Attendance).filter(Attendance.employee_id == employee_id, Attendance.admin_id == admin_id).all()
    for row in attendance_rows:
        if row.check_in_photo:
            cleanup_files.append(row.check_in_photo)
        if row.check_out_photo:
            cleanup_files.append(row.check_out_photo)

    break_rows = db.query(BreakTime).filter(BreakTime.employee_id == employee_id, BreakTime.admin_id == admin_id).all()
    for row in break_rows:
        if row.break_in_photo:
            cleanup_files.append(row.break_in_photo)
        if row.break_out_photo:
            cleanup_files.append(row.break_out_photo)

    try:
        # Delete dependent rows first to avoid FK constraint errors
        db.query(BreakTime).filter(BreakTime.employee_id == employee_id, BreakTime.admin_id == admin_id).delete(synchronize_session=False)
        db.query(Attendance).filter(Attendance.employee_id == employee_id, Attendance.admin_id == admin_id).delete(synchronize_session=False)
        db.query(SalarySlip).filter(SalarySlip.employee_id == employee_id, SalarySlip.admin_id == admin_id).delete(synchronize_session=False)
        db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee_id, LeaveRequest.admin_id == admin_id).delete(synchronize_session=False)
        db.query(CurrentLocation).filter(CurrentLocation.employee_id == employee_id, CurrentLocation.admin_id == admin_id).delete(synchronize_session=False)

        db.delete(employee)
        db.commit()
    except Exception:
        db.rollback()
        raise

    # Remove uploaded files/directories (best-effort)
    for file_path in set(cleanup_files):
        _safe_remove_file(file_path)
    for dir_path in cleanup_dirs:
        _safe_remove_dir(dir_path)

    return {"message": "Employee and related data deleted"}
