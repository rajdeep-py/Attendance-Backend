from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Enum
from models.base import Base
from datetime import datetime
import enum

class LeaveStatusEnum(enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class LeaveRequest(Base):
    __tablename__ = 'leave_requests'
    leave_id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employee_users.employee_id'), nullable=False)
    date = Column(Date, nullable=False)
    reason = Column(String, nullable=False)
    status = Column(Enum(LeaveStatusEnum), default=LeaveStatusEnum.pending, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
