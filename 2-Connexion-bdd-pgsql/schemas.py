from pydantic import BaseModel, Field
from typing import Optional

class PassengerBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nom du passager")
    sex: str = Field(..., pattern="^(male|female)$", description="Sexe du passager")
    age: Optional[float] = Field(None, ge=0, le=120, description="Âge du passager")
    survived: bool = Field(..., description="Le passager a-t-il survécu ?")
    pclass: int = Field(..., ge=1, le=3, description="Classe du passager (1, 2 ou 3)")
    fare: Optional[float] = Field(None, ge=0, description="Prix du billet")
    embarked: Optional[str] = Field(None, pattern="^[CSQ]$", description="Port d'embarquement")

class PassengerCreate(PassengerBase):
    pass

class PassengerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    sex: Optional[str] = Field(None, pattern="^(male|female)$")
    age: Optional[float] = Field(None, ge=0, le=120)
    survived: Optional[bool] = None
    pclass: Optional[int] = Field(None, ge=1, le=3)
    fare: Optional[float] = Field(None, ge=0)
    embarked: Optional[str] = Field(None, pattern="^[CSQ]$")

class PassengerResponse(PassengerBase):
    id: int
    
    class Config:
        from_attributes = True