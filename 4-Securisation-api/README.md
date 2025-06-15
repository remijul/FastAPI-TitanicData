## Atelier 4 : Sécurisation de l'API

## 🎯 Objectifs

- Comprendre l'authentification JWT (JSON Web Token)
- Implémenter un système de connexion/déconnexion
- Protéger certains endpoints avec des rôles
- Gérer les autorisations utilisateur

## 📚 Concepts théoriques

### Qu'est-ce que l'authentification ?

**L'authentification** répond à la question : **"Qui es-tu ?"**

- Avant : N'importe qui peut accéder à tous les endpoints
- Après : Seuls les utilisateurs identifiés peuvent accéder aux données sensibles

### JWT : Passeport numérique

Un **JWT** est comme un **passeport numérique** qui contient :

- Qui vous êtes (user_id, email)
- Vos droits (admin, user)
- Validité (expiration)

```txt
JWT = Header + Payload + Signature
eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJyb2xlIjoiYWRtaW4ifQ.signature
```

### Flux d'authentification simple

```txt
1. Login → Email + Mot de passe
2. Serveur → Vérifie les credentials
3. Serveur → Génère un JWT
4. Client → Stocke le JWT
5. Requêtes → Envoie le JWT dans les headers
6. Serveur → Vérifie le JWT et autorise/refuse
```

### Rôles utilisateur simples

- 👤 **USER** : Peut consulter ses propres données
- 👑 **ADMIN** : Peut tout faire (CRUD complet)
- 🔒 **ANONYMOUS** : Accès limité (lecture publique uniquement)

## 🚀 Mise en pratique

### Structure du projet (ajouts à l'Atelier 3)

```txt
atelier4/
├── [Structure Atelier 3]
├── auth/
│   ├── __init__.py
│   ├── jwt_handler.py      # Gestion des tokens JWT
│   ├── auth_service.py     # Logique d'authentification
│   └── dependencies.py    # Dépendances FastAPI
├── models/
│   └── user.py            # Modèle utilisateur
├── schemas/
│   └── auth.py            # Schémas d'auth
├── create_users.py        # Script création utilisateurs
└── test_auth.py           # Tests authentification
```

### Installation des dépendances

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

### 1. Modèle utilisateur : `models/user.py`

```python
from sqlalchemy import Column, Integer, String, Boolean
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="user")  # "user" ou "admin"
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
```

### 2. Mise à jour `models/__init__.py`

```python
from .database import get_db, engine, Base, test_connection, SessionLocal
from .passenger import Passenger
from .user import User

__all__ = ["get_db", "engine", "Base", "test_connection", "SessionLocal", "Passenger", "User"]
```

### 3. Schémas d'authentification : `schemas/auth.py`

```python
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    """Données de connexion"""
    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., min_length=4, description="Mot de passe")

class UserCreate(BaseModel):
    """Création d'utilisateur"""
    email: EmailStr = Field(..., description="Adresse email")
    password: str = Field(..., min_length=4, description="Mot de passe")
    role: str = Field("user", description="Rôle: user ou admin")

class UserResponse(BaseModel):
    """Réponse utilisateur (sans mot de passe)"""
    id: int
    email: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """Token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    """Données contenues dans le token"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    role: Optional[str] = None
```

### 4. Mise à jour `schemas/__init__.py`

```python
from .response import StandardResponse, success_response, error_response
from .passenger import PassengerCreate, PassengerUpdate, PassengerResponse, StatisticsGroup
from .auth import UserLogin, UserCreate, UserResponse, Token, TokenData

__all__ = [
    "StandardResponse", "success_response", "error_response",
    "PassengerCreate", "PassengerUpdate", "PassengerResponse", "StatisticsGroup",
    "UserLogin", "UserCreate", "UserResponse", "Token", "TokenData"
]
```

### 5. Gestionnaire JWT : `auth/jwt_handler.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration JWT simple
SECRET_KEY = "votre_cle_secrete_super_securisee_123456789"  # En production, utilisez une vraie clé secrète !
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class JWTHandler:
    """Gestionnaire simplifié pour les tokens JWT"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hacher un mot de passe"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifier un mot de passe"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(user_id: int, email: str, role: str) -> str:
        """Créer un token JWT"""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Décoder et valider un token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Vérifier que le token n'est pas expiré
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                return None
            
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email"),
                "role": payload.get("role")
            }
        except JWTError:
            return None
```

### 6. Service d'authentification : `auth/auth_service.py`

```python
from sqlalchemy.orm import Session
from models import User
from schemas import UserCreate, UserLogin, UserResponse, Token, success_response
from exceptions import ValidationError, PassengerNotFound
from .jwt_handler import JWTHandler

class AuthService:
    """Service d'authentification simplifié"""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate):
        """Créer un nouvel utilisateur"""
        # Vérifier si l'email existe déjà
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise ValidationError("Un utilisateur avec cet email existe déjà")
        
        # Valider le rôle
        if user_data.role not in ["user", "admin"]:
            raise ValidationError("Le rôle doit être 'user' ou 'admin'")
        
        # Hacher le mot de passe
        password_hash = JWTHandler.hash_password(user_data.password)
        
        # Créer l'utilisateur
        db_user = User(
            email=user_data.email,
            password_hash=password_hash,
            role=user_data.role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return success_response(
            data=UserResponse.from_orm(db_user),
            message="Utilisateur créé avec succès"
        )
    
    @staticmethod
    def login(db: Session, login_data: UserLogin):
        """Connecter un utilisateur"""
        # Chercher l'utilisateur par email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise ValidationError("Email ou mot de passe incorrect")
        
        # Vérifier le mot de passe
        if not JWTHandler.verify_password(login_data.password, user.password_hash):
            raise ValidationError("Email ou mot de passe incorrect")
        
        # Vérifier que l'utilisateur est actif
        if not user.is_active:
            raise ValidationError("Compte désactivé")
        
        # Créer le token JWT
        access_token = JWTHandler.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )
        
        # Retourner le token et les infos utilisateur
        token_response = Token(
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
        
        return success_response(
            data=token_response,
            message="Connexion réussie"
        )
    
    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Récupérer l'utilisateur actuel depuis le token"""
        # Décoder le token
        payload = JWTHandler.decode_token(token)
        if not payload:
            raise ValidationError("Token invalide ou expiré")
        
        # Récupérer l'utilisateur
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            raise ValidationError("Utilisateur non trouvé")
        
        if not user.is_active:
            raise ValidationError("Compte désactivé")
        
        return user
    
    @staticmethod
    def get_all_users(db: Session):
        """Récupérer tous les utilisateurs (admin seulement)"""
        users = db.query(User).all()
        user_responses = [UserResponse.from_orm(user) for user in users]
        
        return success_response(
            data=user_responses,
            message=f"{len(users)} utilisateurs trouvés"
        )
```

### 7. Dépendances FastAPI : `auth/dependencies.py`

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from models import get_db
from .auth_service import AuthService
from exceptions import ValidationError

# Sécurité HTTP Bearer (pour récupérer le token des headers)
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dépendance pour récupérer l'utilisateur actuel"""
    try:
        token = credentials.credentials
        user = AuthService.get_current_user(db, token)
        return user
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"}
        )

def get_current_active_user(current_user = Depends(get_current_user)):
    """Dépendance pour vérifier que l'utilisateur est actif"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Utilisateur inactif"
        )
    return current_user

def require_admin(current_user = Depends(get_current_active_user)):
    """Dépendance pour vérifier que l'utilisateur est admin"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis"
        )
    return current_user

def require_user_or_admin(current_user = Depends(get_current_active_user)):
    """Dépendance pour vérifier que l'utilisateur est connecté (user ou admin)"""
    if current_user.role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authentification requise"
        )
    return current_user
```

### 8. Fichier `auth/__init__.py`

```python
from .jwt_handler import JWTHandler
from .auth_service import AuthService
from .dependencies import get_current_user, get_current_active_user, require_admin, require_user_or_admin

__all__ = [
    "JWTHandler", "AuthService", 
    "get_current_user", "get_current_active_user", "require_admin", "require_user_or_admin"
]
```

### 9. Routes d'authentification : `api/auth_routes.py`

```python
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
```

### 10. Protection des routes existantes : `api/routes.py` (mise à jour)

```python
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
```

### 11. Mise à jour de l'application : `main.py`

```python
from fastapi import FastAPI

from models import engine, Base, test_connection
from api.routes import router as passenger_router
from api.auth_routes import router as auth_router

# Créer les tables (y compris la table users)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Titanic - Sécurisée",
    description="API avec authentification JWT et gestion des rôles",
    version="4.0.0"
)

# Inclure les routes
app.include_router(auth_router)      # Routes d'authentification
app.include_router(passenger_router) # Routes des passagers

@app.get("/")
def welcome():
    return {
        "message": "API Titanic v4.0 - Sécurisée ! 🚢🔐",
        "features": [
            "Authentification JWT",
            "Gestion des rôles (user/admin)",
            "Endpoints protégés",
            "Sécurité des données"
        ],
        "endpoints": {
            "public": ["GET /passengers", "GET /passengers/{id}", "GET /passengers/search/*"],
            "authenticated": ["POST /passengers"],
            "admin_only": ["PUT /passengers/{id}", "DELETE /passengers/{id}"]
        }
    }

@app.get("/health")
def health_check():
    """Vérification de santé"""
    db_status = "ok" if test_connection() else "error"
    
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
        "version": "4.0.0",
        "security": "JWT enabled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 12. Script de création d'utilisateurs : `create_users.py`

```python
import sys
import os

if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from models import SessionLocal, engine, Base, User
from auth import JWTHandler

def create_default_users():
    """Créer des utilisateurs par défaut pour les tests"""
    print("👥 Création des utilisateurs par défaut")
    print("=" * 40)
    
    # Créer les tables si nécessaire
    Base.metadata.create_all(bind=engine)
    
    # Utilisateurs par défaut
    default_users = [
        {
            "email": "admin@titanic.com",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "user@titanic.com", 
            "password": "user123",
            "role": "user"
        },
        {
            "email": "jack@titanic.com",
            "password": "rose123",
            "role": "user"
        }
    ]
    
    db = SessionLocal()
    try:
        for user_data in default_users:
            # Vérifier si l'utilisateur existe déjà
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"ℹ️  {user_data['email']} existe déjà")
                continue
            
            # Créer l'utilisateur
            password_hash = JWTHandler.hash_password(user_data["password"])
            
            user = User(
                email=user_data["email"],
                password_hash=password_hash,
                role=user_data["role"]
            )
            
            db.add(user)
            print(f"✅ Créé: {user_data['email']} ({user_data['role']})")
        
        db.commit()
        print(f"\n🎉 Utilisateurs créés avec succès !")
        
        print("\n📋 Comptes de test disponibles:")
        print("👑 Admin: admin@titanic.com / admin123")
        print("👤 User:  user@titanic.com / user123")
        print("👤 User:  jack@titanic.com / rose123")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_default_users()
```

### 13. Tests d'authentification : `test_auth.py`

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_authentication():
    print("🔐 Test de l'authentification JWT\n")
    
    # 1. Test connexion admin
    print("1️⃣ Test connexion admin")
    login_data = {
        "email": "admin@titanic.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        print(f"Réponse brute: {response.text}")  # DEBUG
        
        if response.status_code == 200:
            login_result = response.json()
            print(f"Structure réponse: {type(login_result)}")  # DEBUG
            
            # Vérifier la structure de la réponse
            if 'data' in login_result and login_result['data']:
                if isinstance(login_result['data'], list) and len(login_result['data']) > 0:
                    # Si data est une liste, prendre le premier élément
                    token_data = login_result['data'][0]
                else:
                    # Si data est un objet direct
                    token_data = login_result['data']
                
                admin_token = token_data['access_token']
                admin_user = token_data['user']
                
                print(f"✅ Connexion admin réussie")
                print(f"✅ Role: {admin_user['role']}")
                print(f"✅ Token reçu: {admin_token[:20]}...")
            else:
                print(f"❌ Structure réponse inattendue: {login_result}")
                return
        else:
            print(f"❌ Erreur connexion: {response.text}")
            return
    except Exception as e:
        print(f"❌ Exception: {e}")
        print(f"❌ Type erreur: {type(e)}")
        return
    print()
    
    # 2. Test connexion utilisateur normal
    print("2️⃣ Test connexion utilisateur")
    user_login = {
        "email": "user@titanic.com",
        "password": "user123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=user_login)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            user_result = response.json()
            
            # Même logique de parsing que pour admin
            if isinstance(user_result['data'], list):
                user_token_data = user_result['data'][0]
            else:
                user_token_data = user_result['data']
                
            user_token = user_token_data['access_token']
            print(f"✅ Connexion user réussie")
            print(f"✅ Role: {user_token_data['user']['role']}")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 3. Test endpoint public (sans token)
    print("3️⃣ Test endpoint public (sans authentification)")
    try:
        response = requests.get(f"{BASE_URL}/passengers?limit=3")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Accès public OK")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 4. Test endpoint protégé SANS token
    print("4️⃣ Test endpoint protégé SANS token")
    new_passenger = {
        "name": "Test, Mr. NoAuth",
        "sex": "male",
        "age": 30,
        "survived": True,
        "pclass": 2,
        "fare": 25.0,
        "embarked": "S"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/passengers", json=new_passenger)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Accès refusé sans token (normal)")
        elif response.status_code == 403:
            print("✅ Accès interdit sans token (normal)")
        else:
            print(f"❌ Accès autorisé sans token (problème!) : {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 5. Test endpoint protégé AVEC token utilisateur
    print("5️⃣ Test endpoint protégé AVEC token utilisateur")
    if 'user_token' in locals():
        headers = {"Authorization": f"Bearer {user_token}"}
        
        try:
            response = requests.post(f"{BASE_URL}/passengers", json=new_passenger, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                created = response.json()
                print("✅ Création réussie avec token utilisateur")
                # Récupérer l'ID du passager créé
                if isinstance(created['data'], list):
                    passenger_id = created['data'][0]['id']
                else:
                    passenger_id = created['data']['id']
                print(f"✅ ID du passager créé: {passenger_id}")
            else:
                print(f"❌ Erreur: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    else:
        print("❌ Token utilisateur non disponible")
    print()
    
    # 6. Test endpoint admin AVEC token utilisateur (doit échouer)
    print("6️⃣ Test endpoint admin avec token utilisateur")
    if 'passenger_id' in locals() and 'user_token' in locals():
        update_data = {"age": 31}
        headers = {"Authorization": f"Bearer {user_token}"}
        
        try:
            response = requests.put(f"{BASE_URL}/passengers/{passenger_id}", 
                                  json=update_data, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 403:
                print("✅ Accès refusé pour utilisateur normal (normal)")
            else:
                print(f"❌ Accès autorisé (problème!) : {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    print()
    
    # 7. Test endpoint admin AVEC token admin (doit réussir)
    print("7️⃣ Test endpoint admin avec token admin")
    if 'passenger_id' in locals() and 'admin_token' in locals():
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        update_data = {"age": 32}
        
        try:
            response = requests.put(f"{BASE_URL}/passengers/{passenger_id}", 
                                  json=update_data, headers=admin_headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Modification réussie avec token admin")
            else:
                print(f"❌ Erreur: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    print()
    
    # 8. Test récupération profil utilisateur
    print("8️⃣ Test récupération du profil")
    if 'user_token' in locals():
        headers = {"Authorization": f"Bearer {user_token}"}
        try:
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                profile = response.json()
                if isinstance(profile['data'], list):
                    user_info = profile['data'][0]
                else:
                    user_info = profile['data']
                print(f"✅ Profil récupéré: {user_info['email']}")
            else:
                print(f"❌ Erreur: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    print()
    
    # 9. Test liste des utilisateurs (admin seulement)
    print("9️⃣ Test liste utilisateurs (admin seulement)")
    if 'user_token' in locals() and 'admin_token' in locals():
        try:
            # Avec token user (doit échouer)
            user_headers = {"Authorization": f"Bearer {user_token}"}
            response = requests.get(f"{BASE_URL}/auth/users", headers=user_headers)
            if response.status_code == 403:
                print("✅ Accès refusé pour utilisateur normal")
            
            # Avec token admin (doit réussir)
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            response = requests.get(f"{BASE_URL}/auth/users", headers=admin_headers)
            if response.status_code == 200:
                users = response.json()
                print(f"✅ Liste des utilisateurs récupérée: {users['count']} utilisateurs")
            else:
                print(f"❌ Erreur admin: {response.text}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    print()
    
    # 10. Test avec token invalide
    print("🔟 Test avec token invalide")
    fake_headers = {"Authorization": "Bearer token_bidon_invalide"}
    
    try:
        response = requests.post(f"{BASE_URL}/passengers", json=new_passenger, headers=fake_headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Token invalide correctement rejeté")
        else:
            print(f"❌ Token invalide accepté (problème!)")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_authentication()
```

### 14. Script d'initialisation complet : `init_data.py` (mise à jour)

```python
import sys
import os

if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from models import SessionLocal, engine, Base, Passenger, User, test_connection
from auth import JWTHandler

def init_complete_data():
    print("🚢 Initialisation complète - Atelier 4")
    print("=" * 50)
    
    print("🔍 Test de connexion...")
    if not test_connection():
        print("❌ Impossible de se connecter à la base")
        return False

    try:
        print("🏗️  Création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées (passengers + users)")
    except Exception as e:
        print(f"❌ Erreur tables : {e}")
        return False

    db = SessionLocal()
    try:
        # 1. Créer les utilisateurs par défaut
        print("\n👥 Création des utilisateurs...")
        
        default_users = [
            {"email": "admin@titanic.com", "password": "admin123", "role": "admin"},
            {"email": "user@titanic.com", "password": "user123", "role": "user"},
            {"email": "jack@titanic.com", "password": "rose123", "role": "user"}
        ]
        
        for user_data in default_users:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                password_hash = JWTHandler.hash_password(user_data["password"])
                user = User(
                    email=user_data["email"],
                    password_hash=password_hash,
                    role=user_data["role"]
                )
                db.add(user)
                print(f"✅ Créé: {user_data['email']} ({user_data['role']})")
            else:
                print(f"ℹ️  Existe: {user_data['email']}")
        
        # 2. Créer les passagers Titanic si nécessaire
        print("\n🚢 Vérification des passagers...")
        passengers_count = db.query(Passenger).count()
        
        if passengers_count == 0:
            print("📊 Insertion des données Titanic...")
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
            
            for data in passengers_data:
                passenger = Passenger(**data)
                db.add(passenger)
            
            print(f"✅ {len(passengers_data)} passagers ajoutés")
        else:
            print(f"ℹ️  {passengers_count} passagers déjà présents")
        
        db.commit()
        
        # Résumé final
        print(f"\n📊 Résumé:")
        users_count = db.query(User).count()
        passengers_count = db.query(Passenger).count()
        print(f"👥 Utilisateurs: {users_count}")
        print(f"🚢 Passagers: {passengers_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = init_complete_data()
    if success:
        print(f"\n🎉 Initialisation terminée !")
        print(f"\n📋 Comptes de test:")
        print(f"👑 Admin: admin@titanic.com / admin123")
        print(f"👤 User:  user@titanic.com / user123")
        print(f"👤 User:  jack@titanic.com / rose123")
        print(f"\n💡 Lancez: python main.py")
    else:
        print(f"\n💥 Échec de l'initialisation")
```

## 🚀 Instructions de démarrage

### 1. Installer les nouvelles dépendances :

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart pydantic[email]
```

### 2. Créer la structure auth :

```bash
mkdir auth
touch auth/__init__.py
```

### 3. Initialiser les données complètes :

```bash
python init_data.py
```

### 4. Lancer l'API :

```bash
python main.py
```

### 5. Tester l'authentification :

```bash
python test_auth.py
```

### 6. Documentation interactive :

- Ouvrez `http://localhost:8000/docs`
- Vous verrez un bouton "Authorize" pour tester avec des tokens !

## 💡 Points clés à retenir

### Flux d'utilisation typique :

1. **S'inscrire/Se connecter** → Obtenir un token JWT
2. **Stocker le token** → Dans l'application cliente
3. **Envoyer le token** → Dans le header Authorization: Bearer <token>
4. **Accéder aux ressources** → Selon les permissions du rôle

### Niveaux de protection :

- 🌍 **Public** : Lecture des passagers, statistiques
- 🔒 **Authentifié** : Création de passagers
- 👑 **Admin** : Modification/Suppression des passagers

### Sécurité implémentée :

- ✅ Mots de passe hachés (bcrypt)
- ✅ Tokens JWT avec expiration
- ✅ Validation automatique des tokens
- ✅ Gestion des rôles
- ✅ Protection CSRF (stateless)

------

## 🎯 Exercice Pratique

### Énoncé

Créez un nouveau rôle **"moderator"** qui peut :

✅ Voir tous les passagers (comme tout le monde)
✅ Créer des passagers (comme les users)
✅ Modifier des passagers (comme les admins)
❌ **MAIS PAS** supprimer des passagers (réservé aux admins)

### Tâches :

1. Ajouter le rôle "moderator" dans la validation
2. Créer une nouvelle dépendance `require_moderator_or_admin`
3. Modifier l'endpoint PUT pour accepter les moderators
4. Créer un utilisateur de test moderator
5. Tester les permissions
