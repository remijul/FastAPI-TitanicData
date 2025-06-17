# Atelier 5 : Documentation et bonnes pratiques

## 🎯 Objectifs

- Créer une documentation API complète et professionnelle
- Enrichir les métadonnées des endpoints (tags, descriptions, exemples)
- Implémenter des tests automatisés avec TestClient
- Adopter les bonnes pratiques de développement API

## 📚 Concepts théoriques

### Pourquoi documenter son API ?

Une bonne documentation est essentielle pour :

- **Faciliter l'adoption** : Les développeurs comprennent rapidement comment utiliser votre API
- **Réduire le support** : Moins de questions grâce à des exemples clairs
- **Professionnaliser** : Une API bien documentée inspire confiance
- **Maintenance** : Plus facile de maintenir du code bien documenté

### OpenAPI/Swagger : Le standard

**OpenAPI** (anciennement Swagger) est le standard pour documenter les APIs REST :

- **Génération automatique** : FastAPI génère la doc depuis votre code
- **Interface interactive** : Testez directement depuis la documentation
- **Standardisé** : Format reconnu par tous les outils

### Tests automatisés avec TestClient

Les **tests automatisés** garantissent la qualité :

- **Détection des régressions** : Évite de casser ce qui marchait
- **Confiance** : Déploiement serein
- **Documentation vivante** : Les tests montrent comment utiliser l'API

```python
# Test simple avec TestClient
from fastapi.testclient import TestClient
client = TestClient(app)

def test_get_passengers():
    response = client.get("/api/v1/passengers")
    assert response.status_code == 200
```

### Structure d'un test avec authentification JWT

```python
def test_protected_endpoint():
    # 1. Se connecter pour obtenir un token
    login_response = client.post("/api/v1/auth/login", json={
        "email": "user@test.com",
        "password": "password"
    })
    token = login_response.json()["data"]["access_token"]
    
    # 2. Utiliser le token dans les headers
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/passengers", json=data, headers=headers)
    
    # 3. Vérifier le résultat
    assert response.status_code == 200
```

## 🚀 Mise en pratique

### Structure du projet (ajouts à l'Atelier 4)

```txt
atelier5/
├── [Structure Atelier 4]
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Configuration pytest
│   ├── test_auth.py          # Tests authentification
│   ├── test_passengers.py    # Tests endpoints passagers
│   └── test_documentation.py # Tests de la documentation
├── docs/
│   ├── examples.py           # Exemples pour la doc
│   └── descriptions.py       # Descriptions détaillées
└── requirements-dev.txt      # Dépendances de développement
```

### Installation des dépendances de test

```bash
pip install pytest pytest-asyncio httpx
```

### 1. Configuration des tests : `tests/conftest.py`

```python
import pytest
import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ✅ Correction de l'import - ajouter le répertoire parent au path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ✅ Maintenant on peut importer main
import main
from models import get_db, Base
from auth import JWTHandler

# Base de données SQLite en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override de la dépendance de base de données
main.app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Créer la base de test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Client de test FastAPI"""
    return TestClient(main.app)

@pytest.fixture
def test_user_data():
    """Données d'utilisateur de test"""
    return {
        "email": "test@example.com",
        "password": "testpass123",
        "role": "user"
    }

@pytest.fixture
def test_admin_data():
    """Données d'admin de test"""
    return {
        "email": "admin@example.com",
        "password": "adminpass123",
        "role": "admin"
    }

@pytest.fixture
def test_passenger_data():
    """Données de passager de test"""
    return {
        "name": "Test, Mr. Passenger",
        "sex": "male",
        "age": 30,
        "survived": True,
        "pclass": 2,
        "fare": 25.0,
        "embarked": "S"
    }

def get_auth_headers(client: TestClient, email: str, password: str) -> dict:
    """Utility pour obtenir les headers d'authentification"""
    # D'abord créer l'utilisateur si nécessaire
    register_response = client.post("/api/v1/auth/register", json={
        "email": email,
        "password": password,
        "role": "admin" if "admin" in email else "user"
    })
    
    # Se connecter (même si register échoue, login peut réussir)
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    
    if response.status_code == 200:
        token_data = response.json()["data"]
        if isinstance(token_data, list):
            token = token_data[0]["access_token"]
        else:
            token = token_data["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        raise Exception(f"Login failed: {response.text}")
```

### 2. Tests d'authentification : `tests/test_auth.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_user_registration(client: TestClient, test_user_data):
    """Test d'inscription utilisateur"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Utilisateur créé" in data["message"]
    assert data["data"]["email"] == test_user_data["email"]
    assert data["data"]["role"] == test_user_data["role"]

def test_user_login_success(client: TestClient, test_user_data):
    """Test de connexion réussie"""
    # Créer l'utilisateur d'abord
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Tenter la connexion
    login_data = {
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user"]["email"] == test_user_data["email"]

def test_user_login_invalid_credentials(client: TestClient):
    """Test de connexion avec credentials invalides"""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_duplicate_user_registration(client: TestClient, test_user_data):
    """Test d'inscription avec email déjà existant"""
    # Créer l'utilisateur une première fois
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Tenter de créer le même utilisateur
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 400
    assert "existe déjà" in response.json()["detail"]

def test_get_current_user_profile(client: TestClient, test_user_data):
    """Test de récupération du profil utilisateur"""
    from tests.conftest import get_auth_headers
    
    headers = get_auth_headers(client, test_user_data["email"], test_user_data["password"])
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["email"] == test_user_data["email"]

def test_access_without_token(client: TestClient):
    """Test d'accès à un endpoint protégé sans token"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401

def test_access_with_invalid_token(client: TestClient):
    """Test d'accès avec token invalide"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 401
```

### 3. Tests des endpoints passagers : `tests/test_passengers.py`

```python
import pytest
from fastapi.testclient import TestClient

def test_get_passengers_public(client: TestClient):
    """Test de récupération des passagers (endpoint public)"""
    response = client.get("/api/v1/passengers")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)

def test_get_passenger_by_id_public(client: TestClient):
    """Test de récupération d'un passager par ID (endpoint public)"""
    # D'abord récupérer la liste pour avoir un ID valide
    passengers_response = client.get("/api/v1/passengers?limit=1")
    passengers = passengers_response.json()["data"]
    
    if passengers:
        passenger_id = passengers[0]["id"]
        response = client.get(f"/api/v1/passengers/{passenger_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"][0]["id"] == passenger_id

def test_get_nonexistent_passenger(client: TestClient):
    """Test de récupération d'un passager inexistant"""
    response = client.get("/api/v1/passengers/99999")
    
    assert response.status_code == 404
    assert "non trouvé" in response.json()["detail"]

def test_search_passengers_public(client: TestClient):
    """Test de recherche de passagers (endpoint public)"""
    response = client.get("/api/v1/passengers/search/advanced?sex=female&survived=true")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)

def test_get_statistics_public(client: TestClient):
    """Test des statistiques (endpoint public)"""
    response = client.get("/api/v1/passengers/statistics")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_create_passenger_requires_auth(client: TestClient, test_passenger_data):
    """Test que la création de passager nécessite une authentification"""
    response = client.post("/api/v1/passengers", json=test_passenger_data)
    
    assert response.status_code == 401

def test_create_passenger_with_auth(client: TestClient, test_user_data, test_passenger_data):
    """Test de création de passager avec authentification"""
    from tests.conftest import get_auth_headers
    
    headers = get_auth_headers(client, test_user_data["email"], test_user_data["password"])
    response = client.post("/api/v1/passengers", json=test_passenger_data, headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"][0]["name"] == test_passenger_data["name"]

def test_update_passenger_requires_admin(client: TestClient, test_user_data, test_passenger_data):
    """Test que la modification nécessite les droits admin"""
    from tests.conftest import get_auth_headers
    
    # Créer un passager avec un user normal
    user_headers = get_auth_headers(client, test_user_data["email"], test_user_data["password"])
    create_response = client.post("/api/v1/passengers", json=test_passenger_data, headers=user_headers)
    passenger_id = create_response.json()["data"][0]["id"]
    
    # Essayer de modifier avec un user normal (doit échouer)
    update_data = {"age": 35}
    response = client.put(f"/api/v1/passengers/{passenger_id}", json=update_data, headers=user_headers)
    
    assert response.status_code == 403

def test_update_passenger_with_admin(client: TestClient, test_admin_data, test_passenger_data):
    """Test de modification avec droits admin"""
    from tests.conftest import get_auth_headers
    
    # Créer un passager avec admin
    admin_headers = get_auth_headers(client, test_admin_data["email"], test_admin_data["password"])
    create_response = client.post("/api/v1/passengers", json=test_passenger_data, headers=admin_headers)
    passenger_id = create_response.json()["data"][0]["id"]
    
    # Modifier le passager
    update_data = {"age": 35}
    response = client.put(f"/api/v1/passengers/{passenger_id}", json=update_data, headers=admin_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["data"][0]["age"] == 35

def test_delete_passenger_requires_admin(client: TestClient, test_admin_data, test_passenger_data):
    """Test de suppression avec droits admin"""
    from tests.conftest import get_auth_headers
    
    # Créer un passager
    admin_headers = get_auth_headers(client, test_admin_data["email"], test_admin_data["password"])
    create_response = client.post("/api/v1/passengers", json=test_passenger_data, headers=admin_headers)
    passenger_id = create_response.json()["data"][0]["id"]
    
    # Supprimer le passager
    response = client.delete(f"/api/v1/passengers/{passenger_id}", headers=admin_headers)
    
    assert response.status_code == 200
    assert "supprimé" in response.json()["message"]
```

### 4. Exemples pour la documentation : `docs/examples.py`

```python
"""Exemples pour enrichir la documentation OpenAPI"""

# Exemples de réponses pour les schémas
passenger_example = {
    "id": 1,
    "name": "Braund, Mr. Owen Harris",
    "sex": "male",
    "age": 22.0,
    "survived": False,
    "pclass": 3,
    "fare": 7.25,
    "embarked": "S"
}

passenger_create_example = {
    "name": "Nouveau, Mr. Passager",
    "sex": "male",
    "age": 30,
    "survived": True,
    "pclass": 2,
    "fare": 25.0,
    "embarked": "S"
}

passenger_update_example = {
    "age": 31,
    "fare": 26.50
}

user_login_example = {
    "email": "user@titanic.com",
    "password": "user123"
}

user_register_example = {
    "email": "nouveau@titanic.com",
    "password": "motdepasse123",
    "role": "user"
}

token_response_example = {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "email": "user@titanic.com",
        "role": "user",
        "is_active": True
    }
}

success_response_example = {
    "success": True,
    "message": "Opération réussie",
    "data": [passenger_example],
    "count": 1
}

error_response_example = {
    "success": False,
    "message": "Passager non trouvé",
    "data": None,
    "count": 0
}
```

### 5. Documentation enrichie : mise à jour de `main.py`

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from models import engine, Base, test_connection
from api.routes import router as passenger_router
from api.auth_routes import router as auth_router

# Créer les tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Titanic - Documentation Complète",
    description="""
## 🚢 API de gestion des passagers du Titanic

Cette API permet de gérer les données des passagers du célèbre navire Titanic avec :

* **Authentification JWT** sécurisée
* **Gestion des rôles** (utilisateur/administrateur)
* **CRUD complet** sur les données des passagers
* **Recherche avancée** et statistiques
* **Documentation interactive** complète

### 🔐 Authentification

L'API utilise des tokens JWT pour sécuriser certains endpoints :

1. **Créer un compte** ou **se connecter** via `/auth/register` ou `/auth/login`
2. **Utiliser le token** dans le header `Authorization: Bearer <token>`
3. **Accéder aux endpoints protégés** selon votre rôle

### 👥 Rôles utilisateur

- **👤 USER** : Peut consulter et créer des passagers
- **👑 ADMIN** : Peut tout faire (CRUD complet)
- **🌍 PUBLIC** : Peut consulter les données (sans modification)

### 📊 Données

L'API contient les données historiques des passagers du Titanic avec :
- Informations personnelles (nom, âge, sexe)
- Détails du voyage (classe, port d'embarquement, prix du billet)
- Information de survie

### 🧪 Comptes de test

Pour tester l'API, vous pouvez utiliser :
- **Admin** : `admin@titanic.com` / `admin123`
- **User** : `user@titanic.com` / `user123`
    """,
    version="5.0.0",
    contact={
        "name": "Équipe de développement",
        "email": "dev@titanic-api.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Serveur de développement"
        }
    ]
)

# Inclure les routes avec des tags organisés
app.include_router(
    auth_router,
    tags=["🔐 Authentification"],
)
app.include_router(
    passenger_router,
    tags=["🚢 Passagers"],
)

@app.get("/", tags=["📋 Informations"])
def welcome():
    """
    ## Page d'accueil de l'API
    
    Retourne les informations générales sur l'API et ses fonctionnalités.
    """
    return {
        "message": "API Titanic v5.0 - Documentation complète ! 🚢📚",
        "features": [
            "Authentification JWT sécurisée",
            "Gestion des rôles utilisateur",
            "CRUD complet des passagers",
            "Recherche et statistiques avancées",
            "Documentation interactive OpenAPI",
            "Tests automatisés"
        ],
        "endpoints": {
            "public": [
                "GET /passengers - Liste des passagers",
                "GET /passengers/{id} - Détails d'un passager",
                "GET /passengers/search/advanced - Recherche avancée",
                "GET /passengers/statistics - Statistiques"
            ],
            "authenticated": [
                "POST /passengers - Créer un passager (user+)"
            ],
            "admin_only": [
                "PUT /passengers/{id} - Modifier un passager",
                "DELETE /passengers/{id} - Supprimer un passager"
            ]
        },
        "documentation": "http://localhost:8000/docs"
    }

@app.get("/health", tags=["📋 Informations"])
def health_check():
    """
    ## Vérification de santé de l'API
    
    Endpoint pour vérifier que l'API et la base de données fonctionnent correctement.
    Utile pour le monitoring et les health checks.
    """
    db_status = "ok" if test_connection() else "error"
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "version": "5.0.0",
        "security": "JWT enabled",
        "features": {
            "authentication": True,
            "authorization": True,
            "documentation": True,
            "tests": True
        }
    }

def custom_openapi():
    """Personnalisation de la documentation OpenAPI"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="API Titanic - Documentation Complète",
        version="5.0.0",
        description=app.description,
        routes=app.routes,
    )
    
    # Ajouter des informations de sécurité
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Token JWT obtenu via /auth/login"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 6. Amélioration des routes avec exemples : `api/routes.py (extraits)`

Un exemple ici pour 2 routes, vous pouvez transposer cette logique pour d'autres routes.

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from models import get_db, User
from services import PassengerService
from schemas import PassengerCreate, PassengerUpdate, error_response
from exceptions import PassengerNotFound, ValidationError, DatabaseError
from auth import get_current_active_user, require_admin, require_user_or_admin

router = APIRouter(prefix="/api/v1", tags=["🚢 Passagers"])

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
    `
    GET /passengers?skip=0&limit=10
    `
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
    `json
    {
        "name": "Nouveau, Mr. Passager",
        "sex": "male",
        "age": 30,
        "survived": true,
        "pclass": 2,
        "fare": 25.0,
        "embarked": "S"
    }
    `
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

# ... vous pouvez procéder de même pour les autres endpoints similaires
```

### 7. Mise à jour des schémas avec exemples : `schemas/passenger.py (extraits)`

Un exemple ici pour 1 schéma, vous pouvez transposer cette logique pour d'autres schémas.

```python
from pydantic import BaseModel, Field
from typing import Optional

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
```

### 8. Script de test complet : `run_tests.py`

```python
"""
Script pour exécuter tous les tests avec rapport détaillé
"""
import subprocess
import sys
import os

def run_tests():
    """Exécuter tous les tests avec pytest"""
    print("🧪 Exécution des tests automatisés")
    print("=" * 50)
    
    # Commandes pytest avec options détaillées
    test_commands = [
        # Tests de base avec verbose
        ["pytest", "tests/", "-v", "--tb=short"],
        
        # Tests avec coverage si disponible
        ["pytest", "tests/", "--cov=.", "--cov-report=term-missing", "-v"],
        
        # Tests spécifiques par module
        ["pytest", "tests/test_auth.py", "-v"],
        ["pytest", "tests/test_passengers.py", "-v"],
    ]
    
    for i, cmd in enumerate(test_commands):
        print(f"\n{'='*20} Commande {i+1}/{len(test_commands)} {'='*20}")
        print(f"Exécution: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                print("✅ Tests réussis")
                print(result.stdout)
            else:
                print("❌ Tests échoués")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
            # Arrêter après le premier test réussi pour éviter la redondance
            if result.returncode == 0:
                break
                
        except FileNotFoundError:
            print(f"⚠️  Commande non trouvée: {cmd[0]}")
            continue
        except Exception as e:
            print(f"❌ Erreur: {e}")
            continue
    
    print(f"\n🎉 Tests terminés")

if __name__ == "__main__":
    run_tests()
```

### 9. Requirements de développement : `requirements-dev.txt`

```txt
# Dépendances de production
fastapi
uvicorn
sqlalchemy
psycopg2-binary
pydantic[email]
python-jose[cryptography]
passlib[bcrypt]
python-multipart
requests

# Dépendances de développement et test
pytest
pytest-asyncio
httpx
pytest-cov
black
flake8
mypy
```

## 🚀 Instructions de démarrage

### 1. Installer les dépendances de test :

```bash
pip install -r requirements-dev.txt
```

### 2. Lancer l'API :

```bash
python main.py
```

### 3. Explorer la documentation enrichie :

- Ouvrez `http://localhost:8000/docs`
- Explorez les nouveaux tags, descriptions et exemples
- Testez l'authentification avec le bouton "Authorize"

### 4. Exécuter les tests :

```bash
pytest tests/ -v
```

Les résultats de test pourraient ressembler à ceci :

```bash
(venv) PS C:\FastAPI-TitanicData\5-Documentation-et-tests> pytest tests/ -v
====================================================================================== test session starts ======================================================================================
platform win32 -- Python 3.12.7, pytest-8.4.0, pluggy-1.6.0 -- C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests
plugins: anyio-4.9.0, asyncio-1.0.0, cov-6.2.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 17 items                                                                                                                                                                               

tests/test_auth.py::test_user_registration PASSED                                                                                                                                          [  5%]
tests/test_auth.py::test_user_login_success PASSED                                                                                                                                         [ 11%]
tests/test_auth.py::test_user_login_invalid_credentials PASSED                                                                                                                             [ 17%]
tests/test_auth.py::test_duplicate_user_registration PASSED                                                                                                                                [ 23%]
tests/test_auth.py::test_get_current_user_profile PASSED                                                                                                                                   [ 29%]
tests/test_auth.py::test_access_without_token PASSED                                                                                                                                       [ 35%]
tests/test_auth.py::test_access_with_invalid_token PASSED                                                                                                                                  [ 41%]
tests/test_passengers.py::test_get_passengers_public PASSED                                                                                                                                [ 47%]
tests/test_passengers.py::test_get_passenger_by_id_public PASSED                                                                                                                           [ 52%]
tests/test_passengers.py::test_get_nonexistent_passenger PASSED                                                                                                                            [ 58%]
tests/test_passengers.py::test_search_passengers_public PASSED                                                                                                                             [ 64%] 
tests/test_passengers.py::test_get_statistics_public FAILED                                                                                                                                [ 70%]
tests/test_passengers.py::test_create_passenger_requires_auth PASSED                                                                                                                       [ 76%] 
tests/test_passengers.py::test_create_passenger_with_auth PASSED                                                                                                                           [ 82%]
tests/test_passengers.py::test_update_passenger_requires_admin PASSED                                                                                                                      [ 88%]
tests/test_passengers.py::test_update_passenger_with_admin PASSED                                                                                                                          [ 94%]
tests/test_passengers.py::test_delete_passenger_requires_admin PASSED                                                                                                                      [100%]

=========================================================================================== FAILURES ============================================================================================ 
__________________________________________________________________________________ test_get_statistics_public ___________________________________________________________________________________ 

client = <starlette.testclient.TestClient object at 0x000001C900D2FE30>

    def test_get_statistics_public(client: TestClient):
        """Test des statistiques (endpoint public)"""
        # ✅ Correction : ajouter les paramètres nécessaires si requis
        response = client.get("/api/v1/passengers/statistics")

        # Si 422, essayer avec un paramètre
        if response.status_code == 422:
            response = client.get("/api/v1/passengers/statistics?group_by=class")

>       assert response.status_code == 200
E       assert 422 == 200
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests\test_passengers.py:59: AssertionError
======================================================================================= warnings summary ======================================================================================== 
models\database.py:15
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\models\database.py:15: MovedIn20Warning: The ``declarative_base()`` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
    Base = declarative_base()

..\venv\Lib\site-packages\pydantic\fields.py:1089: 12 warnings
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\venv\Lib\site-packages\pydantic\fields.py:1089: PydanticDeprecatedSince20: Using extra keyword arguments on `Field` is deprecated and will be removed. Use `json_schema_extra` instead. (Extra keys: 'example'). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warn(

..\venv\Lib\site-packages\pydantic\_internal\_config.py:323
..\venv\Lib\site-packages\pydantic\_internal\_config.py:323
..\venv\Lib\site-packages\pydantic\_internal\_config.py:323
..\venv\Lib\site-packages\pydantic\_internal\_config.py:323
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\venv\Lib\site-packages\pydantic\_internal\_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

api\routes.py:35
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\api\routes.py:35: DeprecationWarning: `example` has been deprecated, please use `examples` instead
    skip: int = Query(0, ge=0, description="Nombre d'éléments à ignorer", example=0),

api\routes.py:36
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\api\routes.py:36: DeprecationWarning: `example` has been deprecated, please use `examples` instead
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'éléments à retourner", example=10),

tests/test_auth.py::test_user_registration
tests/test_passengers.py::test_update_passenger_with_admin
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\auth\auth_service.py:37: PydanticDeprecatedSince20: The `from_orm` method is deprecated; set `model_config['from_attributes']=True` and use `model_validate` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    data=UserResponse.from_orm(db_user),

tests/test_auth.py: 4 warnings
tests/test_passengers.py: 14 warnings
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\schemas\response.py:23: PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    ).dict()

tests/test_auth.py::test_user_login_success
tests/test_auth.py::test_get_current_user_profile
tests/test_passengers.py::test_create_passenger_with_auth
tests/test_passengers.py::test_update_passenger_requires_admin
tests/test_passengers.py::test_update_passenger_with_admin
tests/test_passengers.py::test_delete_passenger_requires_admin
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\auth\jwt_handler.py:30: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

tests/test_auth.py::test_user_login_success
tests/test_auth.py::test_get_current_user_profile
tests/test_passengers.py::test_create_passenger_with_auth
tests/test_passengers.py::test_update_passenger_requires_admin
tests/test_passengers.py::test_update_passenger_with_admin
tests/test_passengers.py::test_delete_passenger_requires_admin
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\auth\jwt_handler.py:37: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    "iat": datetime.utcnow()

tests/test_auth.py::test_user_login_success
tests/test_auth.py::test_get_current_user_profile
tests/test_passengers.py::test_create_passenger_with_auth
tests/test_passengers.py::test_update_passenger_requires_admin
tests/test_passengers.py::test_update_passenger_with_admin
tests/test_passengers.py::test_delete_passenger_requires_admin
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\auth\auth_service.py:67: PydanticDeprecatedSince20: The `from_orm` method is deprecated; set `model_config['from_attributes']=True` and use `model_validate` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
    user=UserResponse.from_orm(user)

tests/test_auth.py::test_get_current_user_profile
tests/test_passengers.py::test_create_passenger_with_auth
tests/test_passengers.py::test_update_passenger_requires_admin
tests/test_passengers.py::test_update_passenger_requires_admin
tests/test_passengers.py::test_update_passenger_with_admin
tests/test_passengers.py::test_update_passenger_with_admin
tests/test_passengers.py::test_delete_passenger_requires_admin
tests/test_passengers.py::test_delete_passenger_requires_admin
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\auth\jwt_handler.py:51: DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).
    if exp and datetime.utcnow() > datetime.fromtimestamp(exp):

tests/test_passengers.py::test_create_passenger_with_auth
tests/test_passengers.py::test_update_passenger_requires_admin
tests/test_passengers.py::test_update_passenger_with_admin
tests/test_passengers.py::test_delete_passenger_requires_admin
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\services\passenger_service.py:108: PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/   
    data_dict = passenger_data.dict()

tests/test_passengers.py::test_update_passenger_with_admin
  C:\Users\RémiJulien\OneDrive\Documents\DcidConsulting\3.Projet\2025_FastAPI-TitanicData\FastAPI-TitanicData\5-Documentation-et-tests\services\passenger_service.py:137: PydanticDeprecatedSince20: The `dict` method is deprecated; use `model_dump` instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/   
    update_data = passenger_data.dict(exclude_unset=True)

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
==================================================================================== short test summary info ==================================================================================== 
FAILED tests/test_passengers.py::test_get_statistics_public - assert 422 == 200
=========================================================================== 1 failed, 16 passed, 70 warnings in 2.36s ===========================================================================

```

### 5. Ou utiliser le script de test :

```bash
python run_tests.py
```

### 6. Générer un rapport de couverture :

```bash
pytest tests/ --cov=. --cov-report=html
```

- Le rapport `html` est automatiquement créé : `Coverage HTML written to dir htmlcov`.
- Vous pouvez analyser le rapport de couverture avec : `start htmlcov/index.html`.

## 💡 Points clés à retenir

### Documentation OpenAPI/Swagger

- **Génération automatique** depuis le code Python
- **Interface interactive** pour tester directement
- **Métadonnées riches** : descriptions, exemples, tags
- **Standard industriel** reconnu par tous les outils

### Tests automatisés

- **TestClient** : Simule des requêtes HTTP sans serveur
- **Fixtures pytest** : Données de test réutilisables
- **Base de test** : SQLite en mémoire pour l'isolation
- **Authentication testing** : Gestion des tokens JWT dans les tests

### Bonnes pratiques

- **Séparation** : Tests séparés du code applicatif
- **Isolation** : Chaque test est indépendant
- **Lisibilité** : Noms de tests explicites
- **Couverture** : Tester tous les cas (succès + erreurs)

------

## 🎯 Exercice Pratique

### Énoncé

Créez une **nouvelle fonctionnalité complète** pour l'API avec sa documentation et ses tests :

**Fonctionnalité** : Endpoint `/api/v1/passengers/favorites` pour gérer une liste de "passagers favoris" par utilisateur.

**Spécifications :**

- `POST /favorites/{passenger_id}` : Ajouter un passager aux favoris (auth requise)
- `GET /favorites` : Récupérer ses favoris (auth requise)
- `DELETE /favorites/{passenger_id}` : Retirer des favoris (auth requise)

**Tâches :**

1. Créer le modèle `Favorite` (relation User ↔ Passenger)
2. Ajouter les schémas Pydantic appropriés
3. Implémenter le service métier
4. Créer les routes avec documentation complète
5. Écrire les tests automatisés
