from sqlalchemy import Column, Integer, String
from models.base import Base

class HelpCenter(Base):
	__tablename__ = 'help_center'
	id = Column(Integer, primary_key=True, index=True)
	description = Column(String, nullable=False)
	phone_no = Column(String, nullable=False)
	email = Column(String, nullable=False)
	address = Column(String, nullable=False)
	website = Column(String, nullable=True)
