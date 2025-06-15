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