from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from models.base import Base
from datetime import datetime

class BreakTime(Base):
	__tablename__ = 'break_time'
	break_id = Column(Integer, primary_key=True, index=True)
	attendance_id = Column(Integer, ForeignKey('attendance.attendance_id'), nullable=False)
	employee_id = Column(Integer, ForeignKey('employee_users.employee_id'), nullable=False)
	admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
	break_in_time = Column(DateTime, nullable=True)
	break_out_time = Column(DateTime, nullable=True)
	break_in_photo = Column(String, nullable=True)
	break_out_photo = Column(String, nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
