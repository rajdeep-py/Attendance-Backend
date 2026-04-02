from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db import get_db
from models.privacy_policy.privacy_policy_models import PrivacyPolicy


router = APIRouter()


class PrivacyPolicyCreate(BaseModel):
	policy_header: str
	policy_description: str


class PrivacyPolicyUpdate(BaseModel):
	policy_header: str | None = None
	policy_description: str | None = None


@router.post("/create/privacy-policy/")
def create_privacy_policy(data: PrivacyPolicyCreate, db: Session = Depends(get_db)):
	policy = PrivacyPolicy(**data.dict())
	db.add(policy)
	db.commit()
	db.refresh(policy)
	return {"message": "Privacy policy created", "id": policy.id}


@router.get("/get/privacy-policy/")
def get_all_privacy_policies(db: Session = Depends(get_db)):
	return db.query(PrivacyPolicy).all()


@router.put("/update/privacy-policy/{id}")
def update_privacy_policy(id: int, update: PrivacyPolicyUpdate, db: Session = Depends(get_db)):
	policy = db.query(PrivacyPolicy).filter(PrivacyPolicy.id == id).first()
	if not policy:
		raise HTTPException(status_code=404, detail="Privacy policy not found")
	for field, value in update.dict(exclude_unset=True).items():
		setattr(policy, field, value)
	db.commit()
	db.refresh(policy)
	return {"message": "Privacy policy updated", "id": policy.id}


@router.delete("/delete/privacy-policy/{id}")
def delete_privacy_policy(id: int, db: Session = Depends(get_db)):
	policy = db.query(PrivacyPolicy).filter(PrivacyPolicy.id == id).first()
	if not policy:
		raise HTTPException(status_code=404, detail="Privacy policy not found")
	db.delete(policy)
	db.commit()
	return {"message": "Privacy policy deleted"}
