from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import Passenger
from schemas import PassengerCreate, PassengerUpdate
from typing import List, Optional

def get_passenger(db: Session, passenger_id: int) -> Optional[Passenger]:
    """Récupérer un passager par son ID"""
    return db.query(Passenger).filter(Passenger.id == passenger_id).first()

def get_passengers(db: Session, skip: int = 0, limit: int = 100) -> List[Passenger]:
    """Récupérer plusieurs passagers avec pagination"""
    return db.query(Passenger).offset(skip).limit(limit).all()

def get_passengers_by_class(db: Session, pclass: int) -> List[Passenger]:
    """Récupérer les passagers par classe"""
    return db.query(Passenger).filter(Passenger.pclass == pclass).all()

def get_survivors(db: Session) -> List[Passenger]:
    """Récupérer uniquement les survivants"""
    return db.query(Passenger).filter(Passenger.survived == True).all()

def create_passenger(db: Session, passenger: PassengerCreate) -> Passenger:
    """Créer un nouveau passager"""
    try:
        passenger_data = passenger.dict()
        db_passenger = Passenger(**passenger_data)
        db.add(db_passenger)
        db.commit()
        db.refresh(db_passenger)
        return db_passenger
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"Erreur d'intégrité : {str(e)}")
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erreur lors de la création : {str(e)}")

def update_passenger(db: Session, passenger_id: int, passenger_update: PassengerUpdate) -> Optional[Passenger]:
    """Mettre à jour un passager"""
    try:
        db_passenger = get_passenger(db, passenger_id)
        if db_passenger:
            update_data = passenger_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_passenger, field, value)
            db.commit()
            db.refresh(db_passenger)
        return db_passenger
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erreur lors de la mise à jour : {str(e)}")

def delete_passenger(db: Session, passenger_id: int) -> bool:
    """Supprimer un passager"""
    try:
        db_passenger = get_passenger(db, passenger_id)
        if db_passenger:
            db.delete(db_passenger)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise ValueError(f"Erreur lors de la suppression : {str(e)}")