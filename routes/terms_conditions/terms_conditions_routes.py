from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db import get_db
from models.terms_conditions.terms_conditions_models import TermsConditions


router = APIRouter()


class TermsConditionsCreate(BaseModel):
	term_headline: str
	term_description: str


class TermsConditionsUpdate(BaseModel):
	term_headline: str | None = None
	term_description: str | None = None


@router.post("/create/terms-conditions/")
def create_terms_conditions(data: TermsConditionsCreate, db: Session = Depends(get_db)):
	terms = TermsConditions(**data.dict())
	db.add(terms)
	db.commit()
	db.refresh(terms)
	return {"message": "Terms & conditions created", "id": terms.id}


@router.get("/get/terms-conditions/")
def get_all_terms_conditions(db: Session = Depends(get_db)):
	return db.query(TermsConditions).all()


@router.put("/update/terms-conditions/{id}")
def update_terms_conditions(id: int, update: TermsConditionsUpdate, db: Session = Depends(get_db)):
	terms = db.query(TermsConditions).filter(TermsConditions.id == id).first()
	if not terms:
		raise HTTPException(status_code=404, detail="Terms & conditions not found")
	for field, value in update.dict(exclude_unset=True).items():
		setattr(terms, field, value)
	db.commit()
	db.refresh(terms)
	return {"message": "Terms & conditions updated", "id": terms.id}


@router.delete("/delete/terms-conditions/{id}")
def delete_terms_conditions(id: int, db: Session = Depends(get_db)):
	terms = db.query(TermsConditions).filter(TermsConditions.id == id).first()
	if not terms:
		raise HTTPException(status_code=404, detail="Terms & conditions not found")
	db.delete(terms)
	db.commit()
	return {"message": "Terms & conditions deleted"}
