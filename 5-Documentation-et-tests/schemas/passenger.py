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

class PassengerCreate(BaseModel):
    """
    Schéma pour créer un nouveau passager
    """
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Nom complet du passager",
        example="Nouveau, Mr. Passager"
    )
    sex: str = Field(
        ...,
        description="Sexe du passager",
        example="male"
    )
    age: Optional[float] = Field(
        None,
        ge=0,
        le=120,
        description="Âge du passager en années",
        example=30
    )
    survived: bool = Field(
        ...,
        description="Le passager a-t-il survécu au naufrage ?",
        example=True
    )
    pclass: int = Field(
        ...,
        ge=1,
        le=3,
        description="Classe du billet (1=Première, 2=Seconde, 3=Troisième)",
        example=2
    )
    fare: Optional[float] = Field(
        None,
        ge=0,
        description="Prix du billet en livres sterling",
        example=25.0
    )
    embarked: Optional[str] = Field(
        None,
        description="Port d'embarquement (C=Cherbourg, S=Southampton, Q=Queenstown)",
        example="S"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Nouveau, Mr. Passager",
                "sex": "male",
                "age": 30,
                "survived": True,
                "pclass": 2,
                "fare": 25.0,
                "embarked": "S"
            }
        }

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
    
class StatisticsGroup(BaseModel):
    """
    Groupe de statistiques pour les passagers
    """
    category: str = Field(..., description="Catégorie du groupe", example="1")
    count: int = Field(..., description="Nombre de passagers dans ce groupe", example=3)
    survival_rate: float = Field(..., description="Taux de survie en pourcentage", example=66.7)
    average_age: Optional[float] = Field(None, description="Âge moyen du groupe", example=42.5)
    average_fare: Optional[float] = Field(None, description="Prix moyen des billets", example=87.2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "1",
                "count": 3,
                "survival_rate": 100.0,
                "average_age": 42.0,
                "average_fare": 87.5
            }
        }   