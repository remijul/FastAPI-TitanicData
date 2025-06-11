# Atelier 3 : Structure et organisation

## 🎯 Objectifs

- Organiser le code en architecture en couches
- Gérer proprement les erreurs et exceptions
- Valider efficacement les données d'entrée
- Standardiser les réponses de l'API

## 📚 Concepts théoriques

### Architecture en couches

L'organisation du code en couches améliore la lisibilité, la maintenance et la testabilité :

```txt
📱 Routes (API Layer)     → Gestion des endpoints HTTP
🔧 Services (Logic Layer) → Logique métier et traitements
💾 Models (Data Layer)    → Accès aux données et persistance
```

### Avantages de cette approche

- Séparation des responsabilités : Chaque couche a un rôle précis
- Réutilisabilité : Les services peuvent être utilisés par plusieurs routes
- Testabilité : Chaque couche peut être testée indépendamment
- Maintenance : Modifications isolées par couche

### Gestion des erreurs simplifiée

Exceptions personnalisées claires et informatives :

```python
# Exception spécifique et simple
raise PassengerNotFound("Passager avec ID 123 introuvable")
```

### Réponses standardisées

Structure cohérente pour toutes les réponses API :

```python
{
    "success": true,
    "message": "Opération réussie",
    "data": [...],
    "count": 10
}
```

## 🚀 Mise en pratique

### Structure du projet

```txt
atelier3/
├── api/
│   ├── __init__.py
│   └── routes.py        # Endpoints HTTP
├── services/
│   ├── __init__.py
│   └── passenger_service.py  # Logique métier
├── models/
│   ├── __init__.py
│   ├── database.py      # Configuration DB
│   └── passenger.py     # Modèle SQLAlchemy
├── schemas/
│   ├── __init__.py
│   ├── passenger.py     # Modèles Pydantic
│   └── response.py      # Réponses standardisées
├── exceptions/
│   ├── __init__.py
│   └── custom_exceptions.py  # Exceptions personnalisées
├── main.py              # Application principale
├── init_data.py         # Initialisation
└── test_api.py          # Tests
```

### 1. Exceptions simples : `exceptions/custom_exceptions.py`

#### Objectif : Définir des erreurs métier spécifiques et parlantes

#### Pourquoi nécessaire :

- Clarté : PassengerNotFound est plus parlant que Exception
- Gestion ciblée : Traiter différemment chaque type d'erreur
- Maintenance : Centralise les messages d'erreur
- Debugging : Plus facile d'identifier la source du problème

```python
class PassengerNotFound(Exception):
    """Passager non trouvé"""
    def __init__(self, passenger_id: int):
        self.message = f"Passager avec ID {passenger_id} introuvable"
        super().__init__(self.message)

class ValidationError(Exception):
    """Erreur de validation des données"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DatabaseError(Exception):
    """Erreur de base de données"""
    def __init__(self, operation: str):
        self.message = f"Erreur lors de l'opération: {operation}"
        super().__init__(self.message)
```

### 2. Fichier `exceptions/__init__.py`

#### Objectif : Exposer les exceptions personnalisées

#### Pourquoi nécessaire :

- Import clean : `from exceptions import PassengerNotFound`
- Évite d'exposer les détails d'implémentation

```python
from .custom_exceptions import PassengerNotFound, ValidationError, DatabaseError

__all__ = ["PassengerNotFound", "ValidationError", "DatabaseError"]
```

### 3. Réponses standardisées : `schemas/response.py`

#### Objectif : Standardiser et valider le format de toutes les réponses API

#### Pourquoi nécessaire :

- Cohérence : Toutes les réponses ont la même structure
- Maintenance : Un seul endroit pour modifier le format des réponses
- Documentation : Les clients savent à quoi s'attendre
- Debugging : Plus facile de tracer les erreurs

```python
from pydantic import BaseModel
from typing import Any, Optional, Dict, List

class StandardResponse(BaseModel):
    """Réponse API standardisée"""
    success: bool
    message: str
    data: Optional[List[Any]] = None
    count: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

def success_response(data: Any = None, message: str = "Opération réussie", count: int = None, metadata: Dict = None):
    """Créer une réponse de succès"""
    if data is not None and not isinstance(data, list):
        data = [data]
    
    return StandardResponse(
        success=True,
        message=message,
        data=data,
        count=count or (len(data) if data else 0),
        metadata=metadata or {}
    ).dict()

def error_response(message: str, data: Any = None):
    """Créer une réponse d'erreur"""
    return StandardResponse(
        success=False,
        message=message,
        data=data,
        count=0
    ).dict()
```

### 4. Fichier `schemas/__init__.py`

#### Objectif : Point d'entrée unique pour tous les schémas

#### Pourquoi nécessaire :

- Import simplifié : from schemas import PassengerCreate, success_response
- Cache la complexité interne du package schemas

```python
from .response import StandardResponse, success_response, error_response
from .passenger import PassengerCreate, PassengerUpdate, PassengerResponse

__all__ = [
    "StandardResponse", "success_response", "error_response",
    "PassengerCreate", "PassengerUpdate", "PassengerResponse"
]
```

### 5. Configuration base de données : `models/database.py`

#### Objectif : Configuration centralisée de la base de données

#### Pourquoi nécessaire :

- Centralise la connexion PostgreSQL pour éviter la duplication
- Fournit la factory `get_db()` pour l'injection de dépendances FastAPI
- Définit la base SQLAlchemy pour tous les modèles
- Permet de tester la connexion facilement

```python
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration encodage
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

DATABASE_URL = "postgresql://titanic_user:titanic_password@localhost:5432/titanic_db"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1
    except Exception:
        return False
```

### 6. Modèle Passenger : `models/passenger.py`

#### Objectif : Définir la structure de la table `passengers` en base

#### Pourquoi nécessaire :

- Sépare la définition du modèle de données de la logique métier
- Utilise l'ORM SQLAlchemy pour mapper Python ↔ SQL
- Centralise la structure de la table (un seul endroit à modifier)
- Permet l'auto-génération des tables

```python
from sqlalchemy import Column, Integer, String, Float, Boolean
from .database import Base

class Passenger(Base):
    __tablename__ = "passengers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    sex = Column(String, nullable=False)
    age = Column(Float, nullable=True)
    survived = Column(Boolean, nullable=False)
    pclass = Column(Integer, nullable=False)
    fare = Column(Float, nullable=True)
    embarked = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<Passenger(id={self.id}, name='{self.name}')>"
```

### 7. Fichier `models/__init__.py`

#### Objectif : Exposer l'API publique du package `models`

#### Pourquoi nécessaire :

- Simplifie les imports : `from models import Passenger`
- Cache les détails internes (seuls les éléments utiles sont exposés)
- Facilite la refactorisation (on peut déplacer du code sans casser les imports)

```python
from .database import get_db, engine, Base, test_connection
from .passenger import Passenger

__all__ = ["get_db", "engine", "Base", "test_connection", "Passenger"]
```

### 8. Schémas Pydantic : `schemas/passenger.py`

#### Objectif : Valider et sérialiser les données d'entrée/sortie

#### Pourquoi nécessaire :

- Validation automatique : Pydantic vérifie les types et contraintes
- Documentation auto : FastAPI génère la doc depuis les schémas
- Sécurité : Empêche l'injection de données malveillantes
- Séparation : Les modèles API ≠ modèles base de données

```python
from pydantic import BaseModel, Field
from typing import Optional

class PassengerBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nom du passager")
    sex: str = Field(..., description="Sexe: male ou female")
    age: Optional[float] = Field(None, ge=0, le=120, description="Âge")
    survived: bool = Field(..., description="A survécu")
    pclass: int = Field(..., ge=1, le=3, description="Classe")
    fare: Optional[float] = Field(None, ge=0, description="Prix du billet")
    embarked: Optional[str] = Field(None, description="Port: C, S, Q")

class PassengerCreate(PassengerBase):
    pass

class PassengerUpdate(BaseModel):
    name: Optional[str] = None
    sex: Optional[str] = None
    age: Optional[float] = None
    survived: Optional[bool] = None
    pclass: Optional[int] = None
    fare: Optional[float] = None
    embarked: Optional[str] = None

class PassengerResponse(PassengerBase):
    id: int
    
    class Config:
        from_attributes = True
```

### 9. Service métier : `services/passenger_service.py`

#### Objectif : Centraliser TOUTE la logique métier des passagers

#### Pourquoi nécessaire :

- Séparation des responsabilités : API = HTTP, Service = logique métier
- Réutilisabilité : Les méthodes peuvent être appelées depuis plusieurs endpoints
- Testabilité : Plus facile de tester la logique isolément
- Maintenance : Logique métier centralisée en un seul endroit

#### Responsabilités :

- Validation des règles métier
- Orchestration des appels à la base
- Calcul des statistiques
- Formatage des réponses

```python
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
```

### 10. Fichier `services/__init__.py`

#### Objectif : Point d'accès au service principal

#### Pourquoi nécessaire :

- Import direct : `from services import PassengerService`
- Peut exposer plusieurs services si le projet grandit

```python
from .passenger_service import PassengerService

__all__ = ["PassengerService"]
```

### 11. Routes API : `api/routes.py`

#### Objectif : Définir les endpoints HTTP et gérer les requêtes/réponses

#### Pourquoi nécessaire :

- Séparation claire : Routes = HTTP uniquement, pas de logique métier
- Gestion d'erreurs : Convertit les exceptions métier en codes HTTP
- Validation HTTP : Paramètres de requête, headers, etc.
- Documentation : FastAPI génère la doc depuis les routes

#### Responsabilités :

- Définir les URLs et méthodes HTTP
- Validation des paramètres HTTP
- Injection des dépendances (db, auth, etc.)
- Conversion exceptions → codes HTTP

```python
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
```

### 12. Fichier `api/__init__.py`

#### Objectif : Exposer le routeur principal

#### Pourquoi nécessaire :

- Import simple dans `main.py` : `from api import router`
- Peut combiner plusieurs routeurs si nécessaire

```python
from .routes import router

__all__ = ["router"]
```

### 13. Application principale : `main.py`

#### Objectif : Point d'entrée de l'application, assemblage de tous les composants

#### Pourquoi nécessaire :

- Orchestration : Combine tous les modules ensemble
- Configuration globale : CORS, middleware, titre de l'API
- Séparation : Garde la logique dans les autres couches
- Lisibilité : Vision claire de la structure de l'app

```python
from fastapi import FastAPI

from models import engine, Base, test_connection
from api import router

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Titanic - Architecture en couches",
    description="API pédagogique avec structure modulaire",
    version="3.0.0"
)

# Inclure les routes
app.include_router(router)

@app.get("/")
def welcome():
    return {
        "message": "API Titanic v3.0 - Architecture en couches ! 🚢📚",
        "features": [
            "Structure modulaire",
            "Gestion d'erreurs personnalisées", 
            "Validation des données",
            "Réponses standardisées"
        ]
    }

@app.get("/health")
def health_check():
    """Vérification de santé"""
    db_status = "ok" if test_connection() else "error"
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "version": "3.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 14. Initialisation : `init_data.py`

```python
import sys
import os

if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from models import SessionLocal, engine, Base, Passenger, test_connection

def init_data():
    print("🚢 Initialisation des données Titanic")
    print("=" * 40)
    
    print("🔍 Test de connexion...")
    if not test_connection():
        print("❌ Impossible de se connecter à la base")
        return False

    try:
        print("🏗️  Création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées")
    except Exception as e:
        print(f"❌ Erreur tables : {e}")
        return False

    passengers_data = [
        {"name": "Braund, Mr. Owen Harris", "sex": "male", "age": 22.0, "survived": False, "pclass": 3, "fare": 7.25, "embarked": "S"},
        {"name": "Cumings, Mrs. John Bradley", "sex": "female", "age": 38.0, "survived": True, "pclass": 1, "fare": 71.28, "embarked": "C"},
        {"name": "Heikkinen, Miss. Laina", "sex": "female", "age": 26.0, "survived": True, "pclass": 3, "fare": 7.92, "embarked": "S"},
        {"name": "Futrelle, Mrs. Jacques Heath", "sex": "female", "age": 35.0, "survived": True, "pclass": 1, "fare": 53.10, "embarked": "S"},
        {"name": "Allen, Mr. William Henry", "sex": "male", "age": 35.0, "survived": False, "pclass": 3, "fare": 8.05, "embarked": "S"},
        {"name": "Moran, Mr. James", "sex": "male", "age": None, "survived": False, "pclass": 3, "fare": 8.46, "embarked": "Q"},
        {"name": "McCarthy, Mr. Timothy J", "sex": "male", "age": 54.0, "survived": False, "pclass": 1, "fare": 51.86, "embarked": "S"},
        {"name": "Palsson, Master. Gosta Leonard", "sex": "male", "age": 2.0, "survived": False, "pclass": 3, "fare": 21.08, "embarked": "S"},
        {"name": "Johnson, Mrs. Oscar W", "sex": "female", "age": 27.0, "survived": True, "pclass": 3, "fare": 11.13, "embarked": "S"},
        {"name": "Nasser, Mrs. Nicholas", "sex": "female", "age": 14.0, "survived": True, "pclass": 2, "fare": 30.07, "embarked": "C"}
    ]

    db = SessionLocal()
    try:
        existing_count = db.query(Passenger).count()
        if existing_count > 0:
            print(f"ℹ️  Base contient déjà {existing_count} passagers")
            return True
        
        print("📊 Insertion des données...")
        for data in passengers_data:
            passenger = Passenger(**data)
            db.add(passenger)
        
        db.commit()
        final_count = db.query(Passenger).count()
        print(f"✅ {final_count} passagers ajoutés !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur insertion : {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = init_data()
    if success:
        print("\n🎉 Prêt ! Lancez: python main.py")
    else:
        print("\n💥 Échec de l'initialisation")
15. Tests : test_api.py
pythonimport requests

BASE_URL = "http://localhost:8000/api/v1"

def test_structured_api():
    print("🧪 Test de l'API structurée\n")
    
    # 1. Health check
    print("1️⃣ Test health check")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Santé API: {health['status']}")
            print(f"✅ Base de données: {health['database']}")
        else:
            print(f"❌ Erreur health: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 2. Pagination
    print("2️⃣ Test pagination")
    try:
        response = requests.get(f"{BASE_URL}/passengers?skip=0&limit=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès: {data['success']}")
            print(f"✅ Message: {data['message']}")
            print(f"✅ Total: {data['count']} passagers")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 3. Recherche
    print("3️⃣ Test recherche avancée")
    try:
        response = requests.get(f"{BASE_URL}/passengers/search/advanced?sex=female&survived=true")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            if 'metadata' in data and 'survival_rate' in data['metadata']:
                print(f"✅ Taux de survie: {data['metadata']['survival_rate']}%")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 4. Gestion d'erreur
    print("4️⃣ Test gestion d'erreur")
    try:
        response = requests.get(f"{BASE_URL}/passengers/999")
        print(f"Status: {response.status_code}")
        if response.status_code == 404:
            error = response.json()
            print(f"✅ Erreur capturée: {error['detail']}")
        else:
            print(f"❌ Status inattendu: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 5. CRUD complet
    print("5️⃣ Test CRUD complet")
    try:
        # Création
        new_passenger = {
            "name": "Test, Mr. Structure",
            "sex": "male",
            "age": 30,
            "survived": True,
            "pclass": 2,
            "fare": 25.0,
            "embarked": "S"
        }
        response = requests.post(f"{BASE_URL}/passengers", json=new_passenger)
        print(f"Création - Status: {response.status_code}")
        
        if response.status_code == 200:
            created = response.json()
            passenger_id = created['data'][0]['id']
            print(f"✅ Passager créé avec ID: {passenger_id}")
            
            # Mise à jour
            update_data = {"age": 31, "fare": 30.0}
            update_response = requests.put(f"{BASE_URL}/passengers/{passenger_id}", json=update_data)
            print(f"Mise à jour - Status: {update_response.status_code}")
            if update_response.status_code == 200:
                print("✅ Mise à jour réussie")
            
            # Suppression
            delete_response = requests.delete(f"{BASE_URL}/passengers/{passenger_id}")
            print(f"Suppression - Status: {delete_response.status_code}")
            if delete_response.status_code == 200:
                print("✅ CRUD complet réussi")
        else:
            print(f"❌ Erreur création: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_structured_api()
```

## 🚀 Instructions de démarrage

### 1.Créer la structure :

```bash
mkdir -p atelier3/{api,services,models,schemas,exceptions}
touch atelier3/{api,services,models,schemas,exceptions}/__init__.py
```

### 2.Initialiser :

```bash
cd atelier3
python init_data.py
```

### 3.Lancer l'API :

```bash
python main.py
```

### 4.Tester :

```
bash
python test_api.py
```

### 5.Documentation :

- `http://localhost:8000/docs`

## 💡 Points clés à retenir

- Architecture claire : Chaque dossier a sa responsabilité
- Exceptions simples : Messages d'erreur informatifs
- Validation robuste : Contrôles métier + Pydantic
- Réponses cohérentes : Structure uniforme
- Séparation des couches : Models, Services, API isolés
- Facilité de maintenance : Code organisé et modulaire

------

## 🎯 Exercice Pratique

### Énoncé
Créez un nouvel endpoint `/api/v1/passengers/statistics` qui retourne des **statistiques détaillées** sur les passagers avec la possibilité de grouper par différents critères.

**Spécifications :**

- URL : /api/v1/passengers/statistics
- Paramètre optionnel : group_by ("class", "sex", "port", "age_group")
- Retour : Statistiques groupées avec métadonnées complètes
- Structure de réponse standardisée

**Format attendu :**

```json
{
  "success": true,
  "message": "Statistiques calculées avec succès",
  "data": [
    {
      "category": "1",
      "count": 3,
      "survival_rate": 100.0,
      "average_age": 42.0,
      "average_fare": 87.5
    }
  ],
  "count": 3,
  "metadata": {
    "group_by": "class",
    "total_passengers": 10,
    "overall_survival_rate": 60.0
  }
}
