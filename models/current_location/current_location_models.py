from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, JSON
from models.base import Base
from datetime import datetime

class CurrentLocation(Base):
    __tablename__ = 'current_location'
    location_id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
    employee_id = Column(Integer, ForeignKey('employee_users.employee_id'), nullable=False)
    date = Column(Date, nullable=False, index=True)
    coordinates = Column(JSON, nullable=False, default=list) # stores an array of {"lat": x, "lng": y, "timestamp": "..."}
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
