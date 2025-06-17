from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from models import get_db, User
from schemas import UserLogin, UserCreate, success_response
from auth import AuthService, require_admin, get_current_active_user
from exceptions import ValidationError, DatabaseError

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Créer un nouveau compte utilisateur"""
    try:
        return AuthService.create_user(db, user_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la création du compte")

@router.post("/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Se connecter et obtenir un token JWT"""
    try:
        return AuthService.login(db, login_data)
    except ValidationError as e:
        raise HTTPException(status_code=401, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la connexion")

@router.get("/me")
def get_me(current_user: User = Depends(get_current_active_user)):
    """Récupérer les informations de l'utilisateur connecté"""
    return success_response(
        data={
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role,
            "is_active": current_user.is_active
        },
        message="Informations utilisateur récupérées"
    )

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Seuls les admins peuvent voir tous les utilisateurs
):
    """Récupérer tous les utilisateurs (admin seulement)"""
    try:
        return AuthService.get_all_users(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des utilisateurs")

@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """Se déconnecter (invalidation côté client)"""
    return success_response(
        message=f"Déconnexion réussie pour {current_user.email}"
    )