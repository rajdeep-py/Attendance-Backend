from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from models.base import Base


class PrivacyPolicy(Base):
	__tablename__ = "privacy_policy"

	id = Column(Integer, primary_key=True, index=True)
	policy_header = Column(String, nullable=False)
	policy_description = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
