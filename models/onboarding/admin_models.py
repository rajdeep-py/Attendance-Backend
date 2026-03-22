# from sqlalchemy and datetime imports
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class AdminUser(Base):
	__tablename__ = 'admin_users'
	admin_id = Column(Integer, primary_key=True, index=True)
	email = Column(String, unique=True, nullable=False, index=True)
	password = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
