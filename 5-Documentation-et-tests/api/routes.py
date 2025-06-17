from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from models import get_db, User
from services import PassengerService
from schemas import PassengerCreate, PassengerUpdate, error_response
from exceptions import PassengerNotFound, ValidationError, DatabaseError
from auth import get_current_active_user, require_admin, require_user_or_admin

router = APIRouter(prefix="/api/v1", tags=["🚢 Passagers"])

# ENDPOINTS PUBLICS (pas d'authentification requise)

@router.get(
    "/passengers",
    summary="📋 Liste des passagers",
    description="""
    Récupère la liste des passagers du Titanic avec pagination.
    
    **Endpoint public** - Aucune authentification requise.
    
    ### Paramètres de pagination
    - `skip` : Nombre d'éléments à ignorer (défaut: 0)
    - `limit` : Nombre maximum d'éléments à retourner (défaut: 100, max: 1000)
    
    ### Exemple d'utilisation
    ```
    GET /passengers?skip=0&limit=10
    ```
    """,
    response_description="Liste paginée des passagers avec métadonnées"
)
def get_passengers(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer", example=0),
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'éléments à retourner", example=10),
    db: Session = Depends(get_db)
):
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

@router.post(
    "/passengers",
    summary="➕ Créer un passager",
    description="""
    Crée un nouveau passager dans la base de données.
    
    **Authentification requise** - Token JWT nécessaire (rôle USER ou ADMIN).
    
    ### Règles de validation
    - Le nom doit contenir au moins 2 caractères
    - Le sexe doit être 'male' ou 'female'
    - L'âge doit être entre 0 et 120 ans
    - La classe doit être 1, 2 ou 3
    - Le port d'embarquement doit être C, S ou Q
    
    ### Exemple de données
    ```json
    {
        "name": "Nouveau, Mr. Passager",
        "sex": "male",
        "age": 30,
        "survived": true,
        "pclass": 2,
        "fare": 25.0,
        "embarked": "S"
    }
    ```
    """,
    response_description="Passager créé avec succès"
)
def create_passenger(
    passenger: PassengerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_user_or_admin)
):
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