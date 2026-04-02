from sqlalchemy import Column, Integer, String, ForeignKey
from models.base import Base

class EmployeeUser(Base):
	__tablename__ = 'employee_users'
	employee_id = Column(Integer, primary_key=True, index=True)
	admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
	full_name = Column(String, nullable=False)
	phone_no = Column(String, unique=True, nullable=False, index=True)
	email = Column(String, nullable=False)
	address = Column(String, nullable=False)
	designation = Column(String, nullable=False)
	password = Column(String, nullable=False)
	profile_photo = Column(String, nullable=True)
	bank_account_no = Column(String, nullable=True)
	bank_name = Column(String, nullable=True)
	branch_name = Column(String, nullable=True)
	ifsc_code = Column(String, nullable=True)
