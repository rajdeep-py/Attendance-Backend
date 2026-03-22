from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from models.base import Base
from datetime import datetime

class LocationMatrix(Base):
	__tablename__ = 'location_matrix'
	location_matrix_id = Column(Integer, primary_key=True, index=True)
	admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
	longitude = Column(Float, nullable=False)
	latitude = Column(Float, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
