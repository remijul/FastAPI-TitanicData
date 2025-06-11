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