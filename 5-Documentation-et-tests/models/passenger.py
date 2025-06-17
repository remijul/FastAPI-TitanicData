from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base

class Passenger(Base):
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    sex = Column(String, nullable=False)
    age = Column(Float, nullable=True)
    survived = Column(Boolean, nullable=False)
    pclass = Column(Integer, nullable=False)
    fare = Column(Float, nullable=True)
    embarked = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Passenger(id={self.id}, name='{self.name}')>"