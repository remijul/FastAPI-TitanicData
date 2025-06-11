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