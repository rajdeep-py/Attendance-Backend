from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from db import get_db
from models.documentation.documentation_models import Documentation


router = APIRouter()


class DocumentationCreate(BaseModel):
	doc_header: str
	doc_description: str


class DocumentationUpdate(BaseModel):
	doc_header: str | None = None
	doc_description: str | None = None


@router.post("/create/documentation/")
def create_documentation(data: DocumentationCreate, db: Session = Depends(get_db)):
	doc = Documentation(**data.dict())
	db.add(doc)
	db.commit()
	db.refresh(doc)
	return {"message": "Documentation created", "id": doc.id}


@router.get("/get/documentation/")
def get_all_documentation(db: Session = Depends(get_db)):
	return db.query(Documentation).all()


@router.put("/update/documentation/{id}")
def update_documentation(id: int, update: DocumentationUpdate, db: Session = Depends(get_db)):
	doc = db.query(Documentation).filter(Documentation.id == id).first()
	if not doc:
		raise HTTPException(status_code=404, detail="Documentation not found")
	for field, value in update.dict(exclude_unset=True).items():
		setattr(doc, field, value)
	db.commit()
	db.refresh(doc)
	return {"message": "Documentation updated", "id": doc.id}


@router.delete("/delete/documentation/{id}")
def delete_documentation(id: int, db: Session = Depends(get_db)):
	doc = db.query(Documentation).filter(Documentation.id == id).first()
	if not doc:
		raise HTTPException(status_code=404, detail="Documentation not found")
	db.delete(doc)
	db.commit()
	return {"message": "Documentation deleted"}

