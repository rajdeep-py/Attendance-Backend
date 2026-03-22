from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.location_matrix.location_matrix_models import LocationMatrix
from db import get_db

router = APIRouter()

class LocationMatrixCreate(BaseModel):
	admin_id: int
	longitude: float
	latitude: float

class LocationMatrixUpdate(BaseModel):
	longitude: float = None
	latitude: float = None

# Create location matrix by admin_id
@router.post("/location-matrix/")
def create_location_matrix(data: LocationMatrixCreate, db: Session = Depends(get_db)):
	loc = LocationMatrix(**data.dict())
	db.add(loc)
	db.commit()
	db.refresh(loc)
	return {"message": "Location matrix created", "location_matrix_id": loc.location_matrix_id}

# Get all location matrices
@router.get("/location-matrix/")
def get_all_location_matrices(db: Session = Depends(get_db)):
	return db.query(LocationMatrix).all()

# Get location matrices by admin_id
@router.get("/location-matrix/admin/{admin_id}")
def get_location_matrices_by_admin(admin_id: int, db: Session = Depends(get_db)):
	return db.query(LocationMatrix).filter(LocationMatrix.admin_id == admin_id).all()

# Update location matrix by admin_id and location_matrix_id
@router.put("/location-matrix/{location_matrix_id}/admin/{admin_id}")
def update_location_matrix(location_matrix_id: int, admin_id: int, update: LocationMatrixUpdate, db: Session = Depends(get_db)):
	loc = db.query(LocationMatrix).filter(LocationMatrix.location_matrix_id == location_matrix_id, LocationMatrix.admin_id == admin_id).first()
	if not loc:
		raise HTTPException(status_code=404, detail="Location matrix not found")
	if update.longitude is not None:
		loc.longitude = update.longitude
	if update.latitude is not None:
		loc.latitude = update.latitude
	db.commit()
	db.refresh(loc)
	return {"message": "Location matrix updated", "location_matrix_id": loc.location_matrix_id}

# Delete location matrix by admin_id and location_matrix_id
@router.delete("/location-matrix/{location_matrix_id}/admin/{admin_id}")
def delete_location_matrix(location_matrix_id: int, admin_id: int, db: Session = Depends(get_db)):
	loc = db.query(LocationMatrix).filter(LocationMatrix.location_matrix_id == location_matrix_id, LocationMatrix.admin_id == admin_id).first()
	if not loc:
		raise HTTPException(status_code=404, detail="Location matrix not found")
	db.delete(loc)
	db.commit()
	return {"message": "Location matrix deleted"}
