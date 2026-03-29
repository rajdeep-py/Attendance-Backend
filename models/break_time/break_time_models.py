from sqlalchemy import Column, Integer, String, Date, Time, Enum, ForeignKey, DateTime
from models.base import Base
from datetime import datetime
import enum

class BreakStatusEnum(str, enum.Enum):
	completed = "completed"
	pending = "pending"

class BreakTime(Base):
	__tablename__ = 'break_times'
	break_id = Column(Integer, primary_key=True, index=True)
	admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
	employee_id = Column(Integer, ForeignKey('employee_users.employee_id'), nullable=False)
	date = Column(Date, nullable=False)
	start_time = Column(Time, nullable=False)
	end_time = Column(Time, nullable=False)
	status = Column(Enum(BreakStatusEnum), default=BreakStatusEnum.pending, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
