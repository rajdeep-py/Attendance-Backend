from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from models.base import Base


class Documentation(Base):
	__tablename__ = "documentation"

	id = Column(Integer, primary_key=True, index=True)
	doc_header = Column(String, nullable=False)
	doc_description = Column(String, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

