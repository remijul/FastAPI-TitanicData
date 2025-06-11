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