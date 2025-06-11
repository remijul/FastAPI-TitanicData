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