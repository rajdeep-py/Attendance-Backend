from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from models.base import Base


class TermsConditions(Base):
	__tablename__ = "terms_conditions"

	id = Column(Integer, primary_key=True, index=True)
	term_headline = Column(String, nullable=False)
	term_description = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
