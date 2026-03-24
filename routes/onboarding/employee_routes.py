from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.onboarding.employee_models import EmployeeUser
from db import get_db
import os
from PIL import Image
from sqlalchemy.exc import IntegrityError
from fastapi import status
from pydantic import BaseModel

router = APIRouter()

UPLOAD_DIR = "uploads/profile_photo"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
    bank_account_no: str
    bank_name: str
    branch_name: str
    ifsc_code: str

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
    bank_account_no: str = Form(...),
    bank_name: str = Form(...),
    branch_name: str = Form(...),
    ifsc_code: str = Form(...),
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
    return {"message": "Employee updated", "employee_id": employee.employee_id}

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
def delete_employee(employee_id: int, admin_id: int, db: Session = Depends(get_db)):
    employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id, EmployeeUser.admin_id == admin_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    # Remove profile photo directory
    dir_path = os.path.join(UPLOAD_DIR, str(employee.employee_id))
    if os.path.exists(dir_path):
        for f in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, f))
        os.rmdir(dir_path)
    db.delete(employee)
    db.commit()
    return {"message": "Employee deleted"}
