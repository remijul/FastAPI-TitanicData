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