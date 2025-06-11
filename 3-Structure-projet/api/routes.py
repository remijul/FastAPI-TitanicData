from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from models import get_db
from services import PassengerService
from schemas import PassengerCreate, PassengerUpdate, error_response
from exceptions import PassengerNotFound, ValidationError, DatabaseError

router = APIRouter(prefix="/api/v1", tags=["passengers"])

@router.get("/passengers")
def get_passengers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Récupérer tous les passagers"""
    try:
        return PassengerService.get_all(db, skip, limit)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur interne")

@router.get("/passengers/{passenger_id}")
def get_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Récupérer un passager par ID"""
    try:
        return PassengerService.get_by_id(db, passenger_id)
    except PassengerNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur interne")

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
    """Recherche avancée de passagers"""
    try:
        return PassengerService.search_advanced(
            db, sex, min_age, max_age, pclass, embarked, survived
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur interne")

@router.post("/passengers")
def create_passenger(passenger: PassengerCreate, db: Session = Depends(get_db)):
    """Créer un nouveau passager"""
    try:
        return PassengerService.create(db, passenger)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur interne")

@router.put("/passengers/{passenger_id}")
def update_passenger(
    passenger_id: int, 
    passenger: PassengerUpdate, 
    db: Session = Depends(get_db)
):
    """Mettre à jour un passager"""
    try:
        return PassengerService.update(db, passenger_id, passenger)
    except PassengerNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur interne")

@router.delete("/passengers/{passenger_id}")
def delete_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Supprimer un passager"""
    try:
        return PassengerService.delete(db, passenger_id)
    except PassengerNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur interne")