
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from db import get_db

from models.documentation.documentation_models import Documentation

import os
import shutil


router = APIRouter()

UPLOAD_DIR = "uploads/documentation"
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


async def _save_pdf(doc_id: int, pdf: UploadFile) -> tuple[str, str]:
	ext = os.path.splitext(pdf.filename or "")[1].lower()
	if ext != ".pdf":
		raise HTTPException(status_code=400, detail="Only PDF files are allowed")

	file_name = os.path.basename(pdf.filename) if pdf.filename else "document.pdf"
	if not file_name.lower().endswith(".pdf"):
		file_name = "document.pdf"

	dir_path = os.path.join(UPLOAD_DIR, str(doc_id))
	os.makedirs(dir_path, exist_ok=True)

	# Keep only the latest PDF for this doc
	for existing in os.listdir(dir_path):
		existing_path = os.path.join(dir_path, existing)
		_safe_remove_file(existing_path)

	file_path = os.path.join(dir_path, file_name)
	contents = await pdf.read()
	with open(file_path, "wb") as f:
		f.write(contents)

	return file_path, file_name


@router.post("/documentation/")
async def create_documentation(
	pdf: UploadFile = File(...),
	db: Session = Depends(get_db),
):
	doc = Documentation(file_name=os.path.basename(pdf.filename or "document.pdf"), file_url="")
	db.add(doc)
	try:
		db.flush()  # assign doc.id
		file_path, file_name = await _save_pdf(doc.id, pdf)
		doc.file_name = file_name
		doc.file_url = file_path
		db.commit()
	except HTTPException:
		db.rollback()
		raise
	except Exception:
		db.rollback()
		raise

	db.refresh(doc)
	return doc


@router.get("/documentation/")
def get_all_documentation(db: Session = Depends(get_db)):
	return db.query(Documentation).order_by(Documentation.created_at.desc()).all()


@router.get("/documentation/{id}")
def get_documentation_by_id(id: int, db: Session = Depends(get_db)):
	doc = db.query(Documentation).filter(Documentation.id == id).first()
	if not doc:
		raise HTTPException(status_code=404, detail="Documentation not found")
	return doc


@router.put("/documentation/{id}")
async def update_documentation(
	id: int,
	pdf: UploadFile = File(...),
	db: Session = Depends(get_db),
):
	doc = db.query(Documentation).filter(Documentation.id == id).first()
	if not doc:
		raise HTTPException(status_code=404, detail="Documentation not found")

	try:
		file_path, file_name = await _save_pdf(doc.id, pdf)
		doc.file_name = file_name
		doc.file_url = file_path
		db.commit()
	except HTTPException:
		db.rollback()
		raise
	except Exception:
		db.rollback()
		raise

	db.refresh(doc)
	return {"message": "Documentation updated", "id": doc.id, "file_url": doc.file_url}


@router.delete("/documentation/{id}")
def delete_documentation(id: int, db: Session = Depends(get_db)):
	doc = db.query(Documentation).filter(Documentation.id == id).first()
	if not doc:
		raise HTTPException(status_code=404, detail="Documentation not found")

	file_path = doc.file_url
	dir_path = os.path.join(UPLOAD_DIR, str(doc.id))

	db.delete(doc)
	db.commit()

	_safe_remove_file(file_path)
	_safe_remove_dir(dir_path)

	return {"message": "Documentation deleted"}

