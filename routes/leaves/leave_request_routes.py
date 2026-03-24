from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models.leaves.leave_request_models import LeaveRequest, LeaveStatusEnum
from db import get_db
from datetime import date

router = APIRouter()

class LeaveRequestCreate(BaseModel):
    admin_id: int
    employee_id: int
    date: date
    reason: str

class LeaveRequestUpdate(BaseModel):
    date: date = None
    reason: str = None
    status: LeaveStatusEnum = None

# Create leave request by employee
@router.post("/create/leave_requests/")
def create_leave_request(leave: LeaveRequestCreate, db: Session = Depends(get_db)):
    leave_req = LeaveRequest(
        admin_id=leave.admin_id,
        employee_id=leave.employee_id,
        date=leave.date,
        reason=leave.reason
    )
    db.add(leave_req)
    db.commit()
    db.refresh(leave_req)
    return {"message": "Leave request created", "leave_id": leave_req.leave_id}

# Get all leave requests by employee_id
@router.get("/get-all/leave_requests/employee/{employee_id}")
def get_leave_requests_by_employee(employee_id: int, db: Session = Depends(get_db)):
    return db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee_id).all()

# Get all leave requests by admin_id
@router.get("/get-all/leave_requests/admin/{admin_id}")
def get_leave_requests_by_admin(admin_id: int, db: Session = Depends(get_db)):
    return db.query(LeaveRequest).filter(LeaveRequest.admin_id == admin_id).all()

# Get all leave requests by admin_id and employee_id
@router.get("/get-all/leave_requests/admin/{admin_id}/employee/{employee_id}")
def get_leave_requests_by_admin_and_employee(admin_id: int, employee_id: int, db: Session = Depends(get_db)):
    return db.query(LeaveRequest).filter(LeaveRequest.admin_id == admin_id, LeaveRequest.employee_id == employee_id).all()

# Update leave request by leave_id
@router.put("/update/leave_requests/{leave_id}")
def update_leave_request(leave_id: int, update: LeaveRequestUpdate, db: Session = Depends(get_db)):
    leave_req = db.query(LeaveRequest).filter(LeaveRequest.leave_id == leave_id).first()
    if not leave_req:
        raise HTTPException(status_code=404, detail="Leave request not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(leave_req, field, value)
    db.commit()
    db.refresh(leave_req)
    return {"message": "Leave request updated", "leave_id": leave_req.leave_id}

# Delete leave request by leave_id
@router.delete("/delete/leave_requests/{leave_id}")
def delete_leave_request(leave_id: int, db: Session = Depends(get_db)):
    leave_req = db.query(LeaveRequest).filter(LeaveRequest.leave_id == leave_id).first()
    if not leave_req:
        raise HTTPException(status_code=404, detail="Leave request not found")
    db.delete(leave_req)
    db.commit()
    return {"message": "Leave request deleted"}
