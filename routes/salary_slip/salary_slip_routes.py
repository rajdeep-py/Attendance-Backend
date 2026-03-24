from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models.salary_slip.salary_slip_models import SalarySlip
from db import get_db
import os
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploads/salary"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Helper to save and compress salary slip PDF
async def save_salary_slip(employee_id: int, slip_file: UploadFile):
	ext = os.path.splitext(slip_file.filename)[1].lower()
	if ext != ".pdf":
		raise HTTPException(status_code=400, detail="Only PDF files are allowed")
	dir_path = os.path.join(UPLOAD_DIR, str(employee_id))
	os.makedirs(dir_path, exist_ok=True)
	file_path = os.path.join(dir_path, "slip.pdf")
	# Remove old slip if exists
	if os.path.exists(file_path):
		os.remove(file_path)
	contents = await slip_file.read()
	with open(file_path, "wb") as f:
		f.write(contents)
	return file_path

# Create salary slip (by admin for employee)
@router.post("/salary_slip/{admin_id}/{employee_id}")
async def create_salary_slip(
	admin_id: int,
	employee_id: int,
	slip_file: UploadFile = File(...),
	db: Session = Depends(get_db)
):
	file_path = await save_salary_slip(employee_id, slip_file)
	slip = SalarySlip(
		admin_id=admin_id,
		employee_id=employee_id,
		salary_slip_url=file_path,
		created_at=datetime.utcnow(),
		updated_at=datetime.utcnow()
	)
	db.add(slip)
	db.commit()
	db.refresh(slip)
	return {"message": "Salary slip created", "slip_id": slip.slip_id, "salary_slip_url": slip.salary_slip_url}

# Get salary slip by slip_id
@router.get("/salary_slip/{slip_id}")
def get_salary_slip(slip_id: int, db: Session = Depends(get_db)):
	slip = db.query(SalarySlip).filter(SalarySlip.slip_id == slip_id).first()
	if not slip:
		raise HTTPException(status_code=404, detail="Salary slip not found")
	return slip

# Get all salary slips by employee_id and admin_id
@router.get("/salary_slip/all/{admin_id}/{employee_id}")
def get_all_salary_slips(admin_id: int, employee_id: int, db: Session = Depends(get_db)):
	slips = db.query(SalarySlip).filter(SalarySlip.admin_id == admin_id, SalarySlip.employee_id == employee_id).all()
	return slips

# Get all salary slips by employee_id
@router.get("/salary_slip/employee/{employee_id}")
def get_salary_slips_by_employee(employee_id: int, db: Session = Depends(get_db)):
	slips = db.query(SalarySlip).filter(SalarySlip.employee_id == employee_id).all()
	return slips

# Update salary slip PDF (by admin for employee)
@router.put("/salary_slip/{admin_id}/{employee_id}/{slip_id}")
async def update_salary_slip(
	admin_id: int,
	employee_id: int,
	slip_id: int,
	slip_file: UploadFile = File(...),
	db: Session = Depends(get_db)
):
	slip = db.query(SalarySlip).filter(
		SalarySlip.slip_id == slip_id,
		SalarySlip.admin_id == admin_id,
		SalarySlip.employee_id == employee_id
	).first()
	if not slip:
		raise HTTPException(status_code=404, detail="Salary slip not found")
	file_path = await save_salary_slip(employee_id, slip_file)
	slip.salary_slip_url = file_path
	slip.updated_at = datetime.utcnow()
	db.commit()
	db.refresh(slip)
	return {"message": "Salary slip updated", "slip_id": slip.slip_id, "salary_slip_url": slip.salary_slip_url}


# Delete salary slip by slip_id
@router.delete("/salary_slip/{slip_id}")
def delete_salary_slip(slip_id: int, db: Session = Depends(get_db)):
	slip = db.query(SalarySlip).filter(SalarySlip.slip_id == slip_id).first()
	if not slip:
		raise HTTPException(status_code=404, detail="Salary slip not found")
	# Remove the PDF file if exists
	if slip.salary_slip_url and os.path.exists(slip.salary_slip_url):
		os.remove(slip.salary_slip_url)
	db.delete(slip)
	db.commit()
	return {"message": "Salary slip deleted"}
