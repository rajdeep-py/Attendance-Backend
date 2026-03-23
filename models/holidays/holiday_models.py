from sqlalchemy import Column, Integer, DateTime, ForeignKey, JSON, Date
from models.base import Base
from datetime import datetime

class Holiday(Base):
	__tablename__ = 'holidays'
	holiday_id = Column(Integer, primary_key=True, index=True)
	admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
	occasion = Column(JSON, nullable=False)  # expects {"title": ..., "remarks": ...}
	date = Column(Date, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
