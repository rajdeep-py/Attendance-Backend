from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.help_center.help_center_models import HelpCenter
from db import get_db

router = APIRouter()

class HelpCenterCreate(BaseModel):
	description: str
	phone_no: str
	email: str
	address: str
	website: str = None

class HelpCenterUpdate(BaseModel):
	description: str = None
	phone_no: str = None
	email: str = None
	address: str = None
	website: str = None

# Create help center
@router.post("/help-center/")
def create_help_center(data: HelpCenterCreate, db: Session = Depends(get_db)):
	help_center = HelpCenter(**data.dict())
	db.add(help_center)
	db.commit()
	db.refresh(help_center)
	return {"message": "Help center created", "id": help_center.id}

# Get all help centers
@router.get("/help-center/")
def get_all_help_centers(db: Session = Depends(get_db)):
	return db.query(HelpCenter).all()

# Update help center by id
@router.put("/help-center/{id}")
def update_help_center(id: int, update: HelpCenterUpdate, db: Session = Depends(get_db)):
	help_center = db.query(HelpCenter).filter(HelpCenter.id == id).first()
	if not help_center:
		raise HTTPException(status_code=404, detail="Help center not found")
	for field, value in update.dict(exclude_unset=True).items():
		setattr(help_center, field, value)
	db.commit()
	db.refresh(help_center)
	return {"message": "Help center updated", "id": help_center.id}

# Delete help center by id
@router.delete("/help-center/{id}")
def delete_help_center(id: int, db: Session = Depends(get_db)):
	help_center = db.query(HelpCenter).filter(HelpCenter.id == id).first()
	if not help_center:
		raise HTTPException(status_code=404, detail="Help center not found")
	db.delete(help_center)
	db.commit()
	return {"message": "Help center deleted"}
