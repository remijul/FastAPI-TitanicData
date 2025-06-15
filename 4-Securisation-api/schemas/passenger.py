from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class PassengerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nom du passager")
    sex: str = Field(..., description="Sexe du passager")
    age: Optional[float] = Field(None, ge=0, le=120, description="Âge du passager")
    survived: bool = Field(..., description="Le passager a-t-il survécu ?")
    pclass: int = Field(..., ge=1, le=3, description="Classe du passager")
    fare: Optional[float] = Field(None, ge=0, description="Prix du billet")
    embarked: Optional[str] = Field(None, description="Port d'embarquement")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Le nom ne peut pas être vide')
        return v.strip()

    @field_validator('sex')
    @classmethod
    def validate_sex(cls, v):
        if v.lower() not in ['male', 'female']:
            raise ValueError('Le sexe doit être "male" ou "female"')
        return v.lower()

    @field_validator('embarked')
    @classmethod
    def validate_embarked(cls, v):
        if v is not None and v.upper() not in ['C', 'S', 'Q']:
            raise ValueError('Le port d\'embarquement doit être C, S ou Q')
        return v.upper() if v else None

class PassengerCreate(PassengerBase):
    pass

class PassengerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    sex: Optional[str] = None
    age: Optional[float] = Field(None, ge=0, le=120)
    survived: Optional[bool] = None
    pclass: Optional[int] = Field(None, ge=1, le=3)
    fare: Optional[float] = Field(None, ge=0)
    embarked: Optional[str] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Le nom ne peut pas être vide')
        return v.strip() if v else None

    @field_validator('sex')
    @classmethod
    def validate_sex(cls, v):
        if v is not None and v.lower() not in ['male', 'female']:
            raise ValueError('Le sexe doit être "male" ou "female"')
        return v.lower() if v else None

    @field_validator('embarked')
    @classmethod
    def validate_embarked(cls, v):
        if v is not None and v.upper() not in ['C', 'S', 'Q']:
            raise ValueError('Le port d\'embarquement doit être C, S ou Q')
        return v.upper() if v else None

class PassengerResponse(PassengerBase):
    id: int
    
    class Config:
        from_attributes = True

# Schéma simplifié pour les filtres de recherche
class PassengerSearchFilters(BaseModel):
    sex: Optional[str] = None
    min_age: Optional[float] = None
    max_age: Optional[float] = None
    pclass: Optional[int] = None
    embarked: Optional[str] = None
    survived: Optional[bool] = None
    
# StatisticsGroup
class StatisticsGroup(BaseModel):
    """Groupe de statistiques"""
    category: str
    count: int
    survival_rate: float
    average_age: Optional[float] = None
    average_fare: Optional[float] = None