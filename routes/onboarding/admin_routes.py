
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from models.onboarding.admin_models import AdminUser
from db import get_db


router = APIRouter()

class AdminCreate(BaseModel):
	email: str
	password: str

class AdminLogin(BaseModel):
	email: str
	password: str


# Admin registration endpoint
@router.post("/admin/register")
def register_admin(admin: AdminCreate, db: Session = Depends(get_db)):
	print("Register admin endpoint called.")
	existing = db.query(AdminUser).filter(AdminUser.email == admin.email).first()
	if existing:
		raise HTTPException(status_code=400, detail="Email already registered")
	new_admin = AdminUser(email=admin.email, password=admin.password)
	db.add(new_admin)
	db.commit()
	db.refresh(new_admin)
	return {
		"message": "Admin registered successfully",
		"admin_id": new_admin.admin_id,
		"email": new_admin.email
	}


# Admin login endpoint
@router.post("/admin/login")
def login_admin(admin: AdminLogin, db: Session = Depends(get_db)):
	print("Login admin endpoint called.")
	user = db.query(AdminUser).filter(AdminUser.email == admin.email).first()
	if not user or user.password != admin.password:
		raise HTTPException(status_code=401, detail="Invalid credentials")
	return {
		"message": "Login successful",
		"admin_id": user.admin_id,
		"email": user.email
	}

# Admin logout endpoint (placeholder, as actual session management is not implemented)
@router.post("/admin/logout")
def logout_admin():
	print("Logout admin endpoint called.")
	return {"message": "Logout successful"}
