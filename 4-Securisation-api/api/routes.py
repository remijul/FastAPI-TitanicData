from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from models import get_db, User
from services import PassengerService
from schemas import PassengerCreate, PassengerUpdate, error_response
from exceptions import PassengerNotFound, ValidationError, DatabaseError
from auth import get_current_active_user, require_admin, require_user_or_admin

router = APIRouter(prefix="/api/v1", tags=["passengers"])

# ENDPOINTS PUBLICS (pas d'authentification requise)

@router.get("/passengers")
def get_passengers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Récupérer tous les passagers (accès public)"""
    try:
        return PassengerService.get_all(db, skip, limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

@router.get("/passengers/{passenger_id}")
def get_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Récupérer un passager par ID (accès public)"""
    try:
        return PassengerService.get_by_id(db, passenger_id)
    except PassengerNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

@router.get("/passengers/search/advanced")
def search_passengers(
    sex: Optional[str] = None,
    min_age: Optional[float] = None,
    max_age: Optional[float] = None,
    pclass: Optional[int] = None,
    embarked: Optional[str] = None,
    survived: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Recherche avancée (accès public)"""
    try:
        return PassengerService.search_advanced(
            db, sex, min_age, max_age, pclass, embarked, survived
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

@router.get("/passengers/statistics")
def get_statistics(
    group_by: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Statistiques (accès public)"""
    try:
        return PassengerService.get_statistics(db, group_by)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

# ENDPOINTS PROTÉGÉS (authentification requise)

@router.post("/passengers")
def create_passenger(
    passenger: PassengerCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_or_admin)  # 🔒 Authentification requise
):
    """Créer un nouveau passager (utilisateurs connectés seulement)"""
    try:
        return PassengerService.create(db, passenger)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

@router.put("/passengers/{passenger_id}")
def update_passenger(
    passenger_id: int, 
    passenger: PassengerUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # 🔒 Admins seulement
):
    """Mettre à jour un passager (admins seulement)"""
    try:
        return PassengerService.update(db, passenger_id, passenger)
    except PassengerNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)

@router.delete("/passengers/{passenger_id}")
def delete_passenger(
    passenger_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # 🔒 Admins seulement
):
    """Supprimer un passager (admins seulement)"""
    try:
        return PassengerService.delete(db, passenger_id)
    except PassengerNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)