from sqlalchemy import Column, Integer, DateTime, Float, String, ForeignKey, Enum
from models.base import Base
from datetime import datetime
import enum

class AttendanceStatusEnum(enum.Enum):
    present = "present"
    absent = "absent"

class Attendance(Base):
    __tablename__ = 'attendance'
    attendance_id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employee_users.employee_id'), nullable=False)
    date = Column(DateTime, nullable=False)
    check_in_time = Column(DateTime, nullable=True)
    check_out_time = Column(DateTime, nullable=True)
    check_in_photo = Column(String, nullable=True)
    check_out_photo = Column(String, nullable=True)
    check_in_latitude = Column(Float, nullable=True)
    check_in_longitude = Column(Float, nullable=True)
    check_out_latitude = Column(Float, nullable=True)
    check_out_longitude = Column(Float, nullable=True)
    status = Column(Enum(AttendanceStatusEnum), default=AttendanceStatusEnum.present, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
