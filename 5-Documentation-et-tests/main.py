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