from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime, date
from db import get_db

from models.current_location.current_location_models import CurrentLocation
from models.onboarding.employee_models import EmployeeUser

router = APIRouter()

class LocationPayload(BaseModel):
    latitude: float
    longitude: float
    timestamp: str = None

@router.post("/current-location/employee/{employee_id}")
def update_current_location(employee_id: int, payload: LocationPayload, db: Session = Depends(get_db)):
    employee = db.query(EmployeeUser).filter(EmployeeUser.employee_id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    today = date.today()
    record = db.query(CurrentLocation).filter(
        CurrentLocation.employee_id == employee_id,
        CurrentLocation.date == today
    ).first()

    now_str = payload.timestamp if payload.timestamp else datetime.utcnow().isoformat()
    new_coord = {
        "lat": payload.latitude,
        "lng": payload.longitude,
        "timestamp": now_str
    }

    if record:
        # Append to existing json list
        # SQLAlchemy JSON columns sometimes require explicit reassignment for change detection
        current_coords = record.coordinates if record.coordinates is not None else []
        
        # Ensure it's a list since JSON could hypothetically store a dict
        if not isinstance(current_coords, list):
            current_coords = [current_coords]
            
        updated_coords = list(current_coords)
        updated_coords.append(new_coord)
        record.coordinates = updated_coords
    else:
        # Create new daily record
        record = CurrentLocation(
            admin_id=employee.admin_id,
            employee_id=employee_id,
            date=today,
            coordinates=[new_coord]
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return {"message": "Location successfully tracked", "location_id": record.location_id, "date": str(record.date)}

@router.get("/current-location/admin/{admin_id}/employee/{employee_id}")
def get_employee_location(admin_id: int, employee_id: int, target_date: date = None, db: Session = Depends(get_db)):
    query = db.query(CurrentLocation).filter(
        CurrentLocation.admin_id == admin_id,
        CurrentLocation.employee_id == employee_id
    )
    if target_date:
        query = query.filter(CurrentLocation.date == target_date)
    
    records = query.order_by(CurrentLocation.date.desc()).all()
    return records
