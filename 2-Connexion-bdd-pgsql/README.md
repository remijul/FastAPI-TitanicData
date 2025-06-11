# Atelier 2 : Connexion base de données avec PostgreSQL

## 🎯 Objectifs

- Configurer une base de données PostgreSQL
- Intégrer SQLAlchemy avec FastAPI
- Implémenter les opérations CRUD de base
- Séparer les modèles de données et de validation

## 📚 Concepts théoriques

**Pourquoi une base de données ?**

Les données en dur ne conviennent que pour les tests. En production, nous avons besoin de :

- **Persistance** : Les données survivent aux redémarrages
- **Concurrence** : Plusieurs utilisateurs simultanés
- **Intégrité** : Contraintes et validations
- **Performance** : Indexation et optimisation

**SQLAlchemy : L'ORM Python**

Un ORM (Object-Relational Mapping) traduit les objets Python en requêtes SQL :

```python
# Au lieu d'écrire du SQL brut
"SELECT * FROM passengers WHERE age > 30"

# On écrit du Python
session.query(Passenger).filter(Passenger.age > 30)
```

**Architecture en couches**

```txt
API (FastAPI) → Modèles Pydantic → ORM (SQLAlchemy) → Base de données (PostgreSQL)
```

**Séparation des modèles**

- Modèle SQLAlchemy : Structure de la table en base
- Modèle Pydantic : Validation des données API
- Schémas : Formats d'entrée/sortie différents

## 🚀 Mise en pratique

### Installation

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv
```

### Configuration PostgreSQL

1. **Fichier .env*

```txt
DATABASE_URL=postgresql://titanic_user:titanic_password@localhost:5432/titanic_db
```

2. **Script de création de la base : create_db.sql**

```sql
-- Connexion en tant qu'administrateur PostgreSQL
CREATE DATABASE titanic_db;
CREATE USER titanic_user WITH PASSWORD 'titanic_password';
GRANT ALL PRIVILEGES ON DATABASE titanic_db TO titanic_user;

-- Se connecter à la base titanic_db
\c titanic_db;

-- Donner les permissions sur le schéma public
GRANT ALL ON SCHEMA public TO titanic_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO titanic_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO titanic_user;
```

### Structure du projet

```txt
atelier2/
├── .env
├── database.py      # Configuration base de données
├── models.py        # Modèles SQLAlchemy
├── schemas.py       # Modèles Pydantic
├── crud.py          # Opérations CRUD
├── main.py          # Application FastAPI
├── init_data.py     # Initialisation des données
└── test_crud.py     # Tests
```

### Script de configuration : database.py

```python
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration encodage pour Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# URL de connexion PostgreSQL
DATABASE_URL = "postgresql://titanic_user:titanic_password@localhost:5432/titanic_db"

print(f"🔗 Connexion à la base : postgresql://titanic_user:***@localhost:5432/titanic_db")

# Moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    echo=False  # True pour voir les requêtes SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Tester la connexion à la base de données"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_user"))
            row = result.fetchone()
            print(f"✅ Connexion réussie ! Base: {row[0]}, Utilisateur: {row[1]}")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        print("💡 Vérifications :")
        print("   - PostgreSQL est-il démarré ?")
        print("   - La base 'titanic_db' existe-t-elle ?")
        print("   - L'utilisateur 'titanic_user' existe-t-il ?")
        return False

if __name__ == "__main__":
    test_connection()
```

### Modèles SQLAlchemy : models.py

```python
from sqlalchemy import Column, Integer, String, Float, Boolean
from database import Base

class Passenger(Base):
    __tablename__ = "passengers"
    
    # Clé primaire avec auto-incrémentation
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

### Schémas Pydantic : schemas.py

```python
from pydantic import BaseModel, Field
from typing import Optional

class PassengerBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nom du passager")
    sex: str = Field(..., pattern="^(male|female)$", description="Sexe du passager")
    age: Optional[float] = Field(None, ge=0, le=120, description="Âge du passager")
    survived: bool = Field(..., description="Le passager a-t-il survécu ?")
    pclass: int = Field(..., ge=1, le=3, description="Classe du passager (1, 2 ou 3)")
    fare: Optional[float] = Field(None, ge=0, description="Prix du billet")
    embarked: Optional[str] = Field(None, pattern="^[CSQ]$", description="Port d'embarquement")

class PassengerCreate(PassengerBase):
    pass

class PassengerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    sex: Optional[str] = Field(None, pattern="^(male|female)$")
    age: Optional[float] = Field(None, ge=0, le=120)
    survived: Optional[bool] = None
    pclass: Optional[int] = Field(None, ge=1, le=3)
    fare: Optional[float] = Field(None, ge=0)
    embarked: Optional[str] = Field(None, pattern="^[CSQ]$")

class PassengerResponse(PassengerBase):
    id: int
    
    class Config:
        from_attributes = True
```

### Opérations CRUD : crud.py

```python
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
```

### Application principale : main.py

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db, engine
from models import Base
import crud
import schemas

# Créer les tables au démarrage
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Titanic - Base de données",
    description="API avec persistance PostgreSQL",
    version="2.0.0"
)

@app.get("/")
def welcome():
    """Page d'accueil de l'API"""
    return {"message": "API Titanic v2.0 avec PostgreSQL ! 🚢💾"}

@app.get("/passengers", response_model=List[schemas.PassengerResponse])
def read_passengers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Récupérer tous les passagers avec pagination"""
    passengers = crud.get_passengers(db, skip=skip, limit=limit)
    return passengers

@app.get("/passengers/{passenger_id}", response_model=schemas.PassengerResponse)
def read_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Récupérer un passager par son ID"""
    passenger = crud.get_passenger(db, passenger_id=passenger_id)
    if passenger is None:
        raise HTTPException(status_code=404, detail="Passager non trouvé")
    return passenger

@app.get("/passengers/class/{pclass}", response_model=List[schemas.PassengerResponse])
def read_passengers_by_class(pclass: int, db: Session = Depends(get_db)):
    """Récupérer les passagers par classe"""
    if pclass not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="La classe doit être 1, 2 ou 3")
    passengers = crud.get_passengers_by_class(db, pclass=pclass)
    return passengers

@app.get("/passengers/search/survivors", response_model=List[schemas.PassengerResponse])
def read_survivors(db: Session = Depends(get_db)):
    """Récupérer uniquement les survivants"""
    survivors = crud.get_survivors(db)
    return survivors

@app.post("/passengers", response_model=schemas.PassengerResponse)
def create_passenger(passenger: schemas.PassengerCreate, db: Session = Depends(get_db)):
    """Créer un nouveau passager"""
    try:
        return crud.create_passenger(db=db, passenger=passenger)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/passengers/{passenger_id}", response_model=schemas.PassengerResponse)
def update_passenger(passenger_id: int, passenger: schemas.PassengerUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un passager"""
    try:
        db_passenger = crud.update_passenger(db, passenger_id, passenger)
        if db_passenger is None:
            raise HTTPException(status_code=404, detail="Passager non trouvé")
        return db_passenger
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/passengers/{passenger_id}")
def delete_passenger(passenger_id: int, db: Session = Depends(get_db)):
    """Supprimer un passager"""
    try:
        success = crud.delete_passenger(db, passenger_id)
        if not success:
            raise HTTPException(status_code=404, detail="Passager non trouvé")
        return {"message": "Passager supprimé avec succès"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Initialisation des données : init_data.py

```python
import sys
import os

# Configuration encodage
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from database import SessionLocal, test_connection
from models import Passenger

def init_data():
    """Initialiser la base avec les données Titanic"""
    
    print("🔍 Test de connexion...")
    if not test_connection():
        print("❌ Impossible de se connecter à la base")
        return False

    # Données Titanic (sans ID - auto-généré)
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
        # Vérifier si des données existent
        existing_count = db.query(Passenger).count()
        if existing_count > 0:
            print(f"ℹ️  La base contient déjà {existing_count} passagers")
            return True
        
        print("📊 Insertion des données...")
        for passenger_data in passengers_data:
            passenger = Passenger(**passenger_data)
            db.add(passenger)
        
        db.commit()
        
        # Vérification
        final_count = db.query(Passenger).count()
        print(f"✅ {final_count} passagers insérés avec succès !")
        
        # Afficher quelques exemples
        first_passengers = db.query(Passenger).limit(3).all()
        for p in first_passengers:
            print(f"   ID {p.id}: {p.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion : {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚢 Initialisation des données Titanic")
    print("=" * 40)
    success = init_data()
    if success:
        print("\n🎉 Prêt à utiliser l'API !")
        print("💡 Lancez: python main.py")
    else:
        print("\n💥 Échec de l'initialisation")
```

### Script de test : test_api.py

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Test de l'API Titanic avec PostgreSQL\n")
    
    # Test 1: Page d'accueil
    print("1️⃣ Test de la page d'accueil")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Réponse: {response.json()['message']}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()
    
    # Test 2: Tous les passagers
    print("2️⃣ Test récupération de tous les passagers")
    try:
        response = requests.get(f"{BASE_URL}/passengers")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            passengers = response.json()
            print(f"Nombre de passagers: {len(passengers)}")
            if passengers:
                print(f"Premier passager: {passengers[0]['name']}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()
    
    # Test 3: Un passager spécifique
    print("3️⃣ Test récupération du passager ID 1")
    try:
        response = requests.get(f"{BASE_URL}/passengers/1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            passenger = response.json()
            print(f"Passager: {passenger['name']}")
            print(f"Survécu: {passenger['survived']}")
        elif response.status_code == 404:
            print("Passager non trouvé")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()
    
    # Test 4: Survivants
    print("4️⃣ Test récupération des survivants")
    try:
        response = requests.get(f"{BASE_URL}/passengers/search/survivors")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            survivors = response.json()
            print(f"Nombre de survivants: {len(survivors)}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()
    
    # Test 5: Passagers par classe
    print("5️⃣ Test passagers de 1ère classe")
    try:
        response = requests.get(f"{BASE_URL}/passengers/class/1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            first_class = response.json()
            print(f"Passagers 1ère classe: {len(first_class)}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    print()
    
    # Test 6: Création d'un passager (optionnel)
    print("6️⃣ Test création d'un nouveau passager")
    try:
        new_passenger = {
            "name": "Test, Mr. API",
            "sex": "male",
            "age": 30,
            "survived": True,
            "pclass": 2,
            "fare": 25.50,
            "embarked": "S"
        }
        response = requests.post(f"{BASE_URL}/passengers", json=new_passenger)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            created = response.json()
            print(f"Passager créé avec ID: {created['id']}")
            
            # Test suppression
            print("   🗑️  Suppression du passager test...")
            delete_response = requests.delete(f"{BASE_URL}/passengers/{created['id']}")
            if delete_response.status_code == 200:
                print("   ✅ Passager supprimé")
        else:
            print(f"Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_api()
```

## 🚀 Lancement

1. **Configurer PostgreSQL :**

```bash
# Créer la base (adaptez selon votre installation)
psql -U postgres -f create_db.sql
```

2. **Tester la connexion :**

```bash
python database.py
```

3. **Initialiser les données :**

```bash
python init_data.py
```

4. **Démarrer l'API :**

```bash
python main.py
```

5. **Tester :**

- Sur un autre terminal :

```bash
python test_crud.py
```

6. **Documentation automatique :**

- Ouvrez `http://localhost:8000/docs`

## 💡 Points clés à retenir

- Séparation des responsabilités : Base, ORM, API, Validation
- Sessions de base de données : Toujours fermer les connexions
- Injection de dépendances : Depends(get_db) pour les sessions
- Validation automatique : Pydantic valide les données d'entrée/sortie

## 🎯 Exercice Pratique

### Énoncé

Créez un nouvel endpoint GET pour **rechercher les passagers par âge et sexe.**

**Spécifications :**

- URL : `/passengers/search/demographics`
- Paramètres de requête :

  - `min_age` (optionnel) : Âge minimum
  - `sex` (optionnel) : "male" ou "female"
  - `max_age` (optionnel) : Âge maximum

- Retour : Liste des passagers + statistiques
- Exemple : `/passengers/search/demographics?sex=female&min_age=20&max_age=40`

**Format de réponse attendu :**

```json
{
  "filters": {
    "sex": "female",
    "min_age": 20,
    "max_age": 40
  },
  "count": 3,
  "survival_rate": 66.7,
  "passengers": [...]
}
```
