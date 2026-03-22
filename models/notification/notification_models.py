from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from models.base import Base
from datetime import datetime


class Notification(Base):
	__tablename__ = 'notifications'
	notification_id = Column(Integer, primary_key=True, index=True)
	admin_id = Column(Integer, ForeignKey('admin_users.admin_id'), nullable=False)
	title = Column(String, nullable=False)
	subtitle = Column(String, nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
