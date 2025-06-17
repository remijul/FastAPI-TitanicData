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