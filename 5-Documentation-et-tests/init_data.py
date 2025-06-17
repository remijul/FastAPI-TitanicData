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