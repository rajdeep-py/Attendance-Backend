from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from models.base import Base
from datetime import datetime

class SalarySlip(Base):
	__tablename__ = 'salary_slips'
	slip_id = Column(Integer, primary_key=True, index=True)
	admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
	employee_id = Column(Integer, ForeignKey('employee_users.employee_id'), nullable=False)
	salary_slip_url = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
