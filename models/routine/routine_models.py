from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, JSON
from models.base import Base
from datetime import datetime

class Routine(Base):
	__tablename__ = 'routines'
	routine_id = Column(Integer, primary_key=True, index=True)
	date = Column(Date, nullable=False, index=True)
	admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False, index=True)
	employee_id = Column(Integer, ForeignKey('employee_users.employee_id'), nullable=False, index=True)
	tasks = Column(JSON, nullable=False)  # List of tasks: [{task_id, task_name, task_description, status}]
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
