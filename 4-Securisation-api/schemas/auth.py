from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    """Données de connexion"""
    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., min_length=4, description="Mot de passe")

class UserCreate(BaseModel):
    """Création d'utilisateur"""
    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., min_length=4, description="Mot de passe")
    role: str = Field("user", description="Rôle: user ou admin")

class UserResponse(BaseModel):
    """Réponse utilisateur (sans mot de passe)"""
    id: int
    email: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """Données contenues dans le token"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None