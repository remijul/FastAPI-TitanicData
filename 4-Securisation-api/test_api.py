import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_structured_api():
    print("🧪 Test de l'API structurée\n")
    
    # 1. Health check
    print("1️⃣ Test health check")
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Santé API: {health['status']}")
            print(f"✅ Base de données: {health['database']}")
        else:
            print(f"❌ Erreur health: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 2. Pagination
    print("2️⃣ Test pagination")
    try:
        response = requests.get(f"{BASE_URL}/passengers?skip=0&limit=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Succès: {data['success']}")
            print(f"✅ Message: {data['message']}")
            print(f"✅ Total: {data['count']} passagers")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 3. Recherche
    print("3️⃣ Test recherche avancée")
    try:
        response = requests.get(f"{BASE_URL}/passengers/search/advanced?sex=female&survived=true")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
            if 'metadata' in data and 'survival_rate' in data['metadata']:
                print(f"✅ Taux de survie: {data['metadata']['survival_rate']}%")
        else:
            print(f"❌ Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 4. Gestion d'erreur
    print("4️⃣ Test gestion d'erreur")
    try:
        response = requests.get(f"{BASE_URL}/passengers/999")
        print(f"Status: {response.status_code}")
        if response.status_code == 404:
            error = response.json()
            print(f"✅ Erreur capturée: {error['detail']}")
        else:
            print(f"❌ Status inattendu: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")
    print()
    
    # 5. CRUD complet
    print("5️⃣ Test CRUD complet")
    try:
        # Création
        new_passenger = {
            "name": "Test, Mr. Structure",
            "sex": "male",
            "age": 30,
            "survived": True,
            "pclass": 2,
            "fare": 25.0,
            "embarked": "S"
        }
        response = requests.post(f"{BASE_URL}/passengers", json=new_passenger)
        print(f"Création - Status: {response.status_code}")
        
        if response.status_code == 200:
            created = response.json()
            passenger_id = created['data'][0]['id']
            print(f"✅ Passager créé avec ID: {passenger_id}")
            
            # Mise à jour
            update_data = {"age": 31, "fare": 30.0}
            update_response = requests.put(f"{BASE_URL}/passengers/{passenger_id}", json=update_data)
            print(f"Mise à jour - Status: {update_response.status_code}")
            if update_response.status_code == 200:
                print("✅ Mise à jour réussie")
            
            # Suppression
            delete_response = requests.delete(f"{BASE_URL}/passengers/{passenger_id}")
            print(f"Suppression - Status: {delete_response.status_code}")
            if delete_response.status_code == 200:
                print("✅ CRUD complet réussi")
        else:
            print(f"❌ Erreur création: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_structured_api()