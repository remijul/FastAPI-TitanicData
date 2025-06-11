# Atelier 1 : Fondamentaux API REST avec FastAPI

## 🎯 Objectifs

- Comprendre les concepts fondamentaux REST
- Créer votre première API avec FastAPI
- Tester et documenter automatiquement votre API

## 📚 Concepts théoriques

**Qu'est-ce qu'une API REST ?**

REST (Representational State Transfer) est un style architectural pour créer des services web. Une API REST utilise les verbes HTTP pour manipuler des ressources.

**Les verbes HTTP essentiels**

- GET : Récupérer des données (lecture)
- POST : Créer une nouvelle ressource
- PUT : Modifier complètement une ressource
- DELETE : Supprimer une ressource

**Structure d'une URL REST**

```txt
GET /passengers        → Récupérer tous les passagers
GET /passengers/1      → Récupérer le passager avec l'ID 1
POST /passengers       → Créer un nouveau passager
PUT /passengers/1      → Modifier le passager 1
DELETE /passengers/1   → Supprimer le passager 1
```

**Codes de statut HTTP**

- 200 : Succès
- 201 : Créé avec succès
- 404 : Ressource non trouvée
- 500 : Erreur serveur

## 🚀 Mise en pratique

**Installation**

```bash
pip install fastapi uvicorn
```

**Script principal : `main.py`**

```python
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI(
    title="API Titanic",
    description="Une API simple pour gérer les données des passagers du Titanic",
    version="1.0.0"
)

# Modèle Pydantic pour valider les données
class Passenger(BaseModel):
    id: int
    name: str
    sex: str
    age: Optional[float]
    survived: int
    pclass: int
    fare: Optional[float]

# Données en dur - 10 premiers passagers du Titanic
passengers_data = [
    {"id": 1, "name": "Braund, Mr. Owen Harris", "sex": "male", "age": 22.0, "survived": 0, "pclass": 3, "fare": 7.25},
    {"id": 2, "name": "Cumings, Mrs. John Bradley", "sex": "female", "age": 38.0, "survived": 1, "pclass": 1, "fare": 71.28},
    {"id": 3, "name": "Heikkinen, Miss. Laina", "sex": "female", "age": 26.0, "survived": 1, "pclass": 3, "fare": 7.92},
    {"id": 4, "name": "Futrelle, Mrs. Jacques Heath", "sex": "female", "age": 35.0, "survived": 1, "pclass": 1, "fare": 53.10},
    {"id": 5, "name": "Allen, Mr. William Henry", "sex": "male", "age": 35.0, "survived": 0, "pclass": 3, "fare": 8.05},
    {"id": 6, "name": "Moran, Mr. James", "sex": "male", "age": None, "survived": 0, "pclass": 3, "fare": 8.46},
    {"id": 7, "name": "McCarthy, Mr. Timothy J", "sex": "male", "age": 54.0, "survived": 0, "pclass": 1, "fare": 51.86},
    {"id": 8, "name": "Palsson, Master. Gosta Leonard", "sex": "male", "age": 2.0, "survived": 0, "pclass": 3, "fare": 21.08},
    {"id": 9, "name": "Johnson, Mrs. Oscar W", "sex": "female", "age": 27.0, "survived": 1, "pclass": 3, "fare": 11.13},
    {"id": 10, "name": "Nasser, Mrs. Nicholas", "sex": "female", "age": 14.0, "survived": 1, "pclass": 2, "fare": 30.07}
]

@app.get("/")
def welcome():
    """Page d'accueil de l'API"""
    return {"message": "Bienvenue sur l'API Titanic ! 🚢"}

@app.get("/passengers", response_model=List[Passenger])
def get_all_passengers():
    """Récupérer tous les passagers"""
    return passengers_data

@app.get("/passengers/{passenger_id}", response_model=Passenger)
def get_passenger(passenger_id: int):
    """Récupérer un passager par son ID"""
    passenger = next((p for p in passengers_data if p["id"] == passenger_id), None)
    if not passenger:
        raise HTTPException(status_code=404, detail="Passager non trouvé")
    return passenger

@app.get("/passengers/search/survivors")
def get_survivors():
    """Récupérer uniquement les survivants"""
    survivors = [p for p in passengers_data if p["survived"] == 1]
    return {"count": len(survivors), "survivors": survivors}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Script de test : test_api.py**

```python
import requests
import json

# URL de base de votre API
BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Test de l'API Titanic\n")
    
    # Test 1: Page d'accueil
    print("1️⃣ Test de la page d'accueil")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Réponse: {response.json()}\n")
    
    # Test 2: Tous les passagers
    print("2️⃣ Test récupération de tous les passagers")
    response = requests.get(f"{BASE_URL}/passengers")
    print(f"Status: {response.status_code}")
    print(f"Nombre de passagers: {len(response.json())}\n")
    
    # Test 3: Un passager spécifique
    print("3️⃣ Test récupération du passager ID 1")
    response = requests.get(f"{BASE_URL}/passengers/1")
    print(f"Status: {response.status_code}")
    print(f"Passager: {response.json()['name']}\n")
    
    # Test 4: Passager inexistant
    print("4️⃣ Test passager inexistant (ID 999)")
    response = requests.get(f"{BASE_URL}/passengers/999")
    print(f"Status: {response.status_code}")
    print(f"Erreur: {response.json()['detail']}\n")
    
    # Test 5: Survivants
    print("5️⃣ Test récupération des survivants")
    response = requests.get(f"{BASE_URL}/passengers/search/survivors")
    print(f"Status: {response.status_code}")
    print(f"Nombre de survivants: {response.json()['count']}")

if __name__ == "__main__":
    test_api()
```

## 🚀 Lancement

1. **Démarrer l'API** :

```bash
python main.py
```

2. **Tester l'API** (dans un autre terminal) :

```bash
python test_api.py
```

3. **Documentation automatique** :

- Ouvrez votre navigateur sur http://localhost:8000/docs
- Explorez l'interface Swagger générée automatiquement ! 🎉

## 💡 Points clés à retenir

- FastAPI génère automatiquement la documentation
- Les modèles Pydantic valident les données
- Les codes de statut HTTP sont gérés automatiquement
- L'URL structure reflète la logique métier

------

## 🎯 Exercice Pratique

### Énoncé

Ajoutez un nouvel endpoint à votre API pour **récupérer les passagers par classe** (1ère, 2ème ou 3ème classe).

Spécifications :

- URL : /passengers/class/{class_number}
- Paramètre : class_number (entier de 1 à 3)
- Retour : Liste des passagers de cette classe
- Gestion d'erreur : Si la classe n'existe pas (< 1 ou > 3)

**Bonus** : Ajoutez aussi le nombre total de passagers dans la réponse.
