from sqlalchemy.orm import Session
from typing import Optional
from models import Passenger
from schemas import PassengerCreate, PassengerUpdate, success_response, error_response
from exceptions import PassengerNotFound, ValidationError, DatabaseError

class PassengerService:
    
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        """Récupérer tous les passagers"""
        try:
            passengers = db.query(Passenger).offset(skip).limit(limit).all()
            total = db.query(Passenger).count()
            
            return success_response(
                data=passengers,
                message=f"{len(passengers)} passagers récupérés",
                count=total,
                metadata={"page": (skip // limit) + 1, "limit": limit}
            )
        except Exception as e:
            raise DatabaseError("récupération des passagers")
    
    @staticmethod
    def get_by_id(db: Session, passenger_id: int):
        """Récupérer un passager par ID"""
        try:
            passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
            if not passenger:
                raise PassengerNotFound(passenger_id)
            
            return success_response(
                data=passenger,
                message="Passager trouvé"
            )
        except PassengerNotFound:
            raise
        except Exception as e:
            raise DatabaseError(f"récupération du passager {passenger_id}")
    
    @staticmethod
    def search_advanced(db: Session, sex=None, min_age=None, max_age=None, pclass=None, embarked=None, survived=None):
        """Recherche avancée"""
        try:
            query = db.query(Passenger)
            
            # Validation simple des paramètres
            if sex and sex not in ['male', 'female']:
                raise ValidationError("Le sexe doit être 'male' ou 'female'")
            
            if embarked and embarked.upper() not in ['C', 'S', 'Q']:
                raise ValidationError("Le port doit être C, S ou Q")
            
            if min_age is not None and max_age is not None and min_age > max_age:
                raise ValidationError("L'âge minimum doit être inférieur à l'âge maximum")
            
            # Appliquer les filtres
            if sex:
                query = query.filter(Passenger.sex == sex)
            if min_age is not None:
                query = query.filter(Passenger.age >= min_age)
            if max_age is not None:
                query = query.filter(Passenger.age <= max_age)
            if pclass:
                query = query.filter(Passenger.pclass == pclass)
            if embarked:
                query = query.filter(Passenger.embarked == embarked.upper())
            if survived is not None:
                query = query.filter(Passenger.survived == survived)
            
            passengers = query.all()
            
            # Calculer des statistiques
            survival_rate = 0
            if passengers:
                survivors = sum(1 for p in passengers if p.survived)
                survival_rate = round((survivors / len(passengers)) * 100, 1)
            
            return success_response(
                data=passengers,
                message=f"{len(passengers)} passagers trouvés",
                metadata={
                    "filters": {
                        "sex": sex, "min_age": min_age, "max_age": max_age,
                        "pclass": pclass, "embarked": embarked, "survived": survived
                    },
                    "survival_rate": survival_rate
                }
            )
        except (ValidationError, PassengerNotFound):
            raise
        except Exception as e:
            raise DatabaseError("recherche des passagers")
    
    @staticmethod
    def create(db: Session, passenger_data: PassengerCreate):
        """Créer un passager"""
        try:
            # Validation métier simple
            if passenger_data.sex not in ['male', 'female']:
                raise ValidationError("Le sexe doit être 'male' ou 'female'")
            
            if passenger_data.embarked and passenger_data.embarked.upper() not in ['C', 'S', 'Q']:
                raise ValidationError("Le port doit être C, S ou Q")
            
            # Normaliser les données
            data_dict = passenger_data.dict()
            if data_dict['embarked']:
                data_dict['embarked'] = data_dict['embarked'].upper()
            data_dict['sex'] = data_dict['sex'].lower()
            
            db_passenger = Passenger(**data_dict)
            db.add(db_passenger)
            db.commit()
            db.refresh(db_passenger)
            
            return success_response(
                data=db_passenger,
                message="Passager créé avec succès"
            )
        except ValidationError:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseError("création du passager")
    
    @staticmethod
    def update(db: Session, passenger_id: int, passenger_data: PassengerUpdate):
        """Mettre à jour un passager"""
        try:
            passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
            if not passenger:
                raise PassengerNotFound(passenger_id)
            
            # Appliquer les modifications
            update_data = passenger_data.dict(exclude_unset=True)
            
            # Validation des champs modifiés
            if 'sex' in update_data and update_data['sex'] not in ['male', 'female']:
                raise ValidationError("Le sexe doit être 'male' ou 'female'")
            
            if 'embarked' in update_data and update_data['embarked'] and update_data['embarked'].upper() not in ['C', 'S', 'Q']:
                raise ValidationError("Le port doit être C, S ou Q")
            
            # Normaliser
            if 'embarked' in update_data and update_data['embarked']:
                update_data['embarked'] = update_data['embarked'].upper()
            if 'sex' in update_data:
                update_data['sex'] = update_data['sex'].lower()
            
            for field, value in update_data.items():
                setattr(passenger, field, value)
            
            db.commit()
            db.refresh(passenger)
            
            return success_response(
                data=passenger,
                message="Passager mis à jour avec succès"
            )
        except (ValidationError, PassengerNotFound):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseError("mise à jour du passager")
    
    @staticmethod
    def delete(db: Session, passenger_id: int):
        """Supprimer un passager"""
        try:
            passenger = db.query(Passenger).filter(Passenger.id == passenger_id).first()
            if not passenger:
                raise PassengerNotFound(passenger_id)
            
            db.delete(passenger)
            db.commit()
            
            return success_response(
                data=None,
                message="Passager supprimé avec succès",
                count=0
            )
        except PassengerNotFound:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseError("suppression du passager")