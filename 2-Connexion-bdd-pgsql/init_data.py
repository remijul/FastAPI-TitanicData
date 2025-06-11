import sys
import os

# Configuration encodage
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from database import SessionLocal, engine, test_connection
from models import Base, Passenger

def init_data():
    """Initialiser la base avec les données Titanic"""
    
    print("🔍 Test de connexion...")
    if not test_connection():
        print("❌ Impossible de se connecter à la base")
        return False

    try:
        print("🏗️  Création des tables...")
        # CRÉER LES TABLES D'ABORD
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des tables : {e}")
        return False

    # Données Titanic (sans ID - auto-généré)
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

    db = SessionLocal()
    try:
        # Vérifier si des données existent
        existing_count = db.query(Passenger).count()
        if existing_count > 0:
            print(f"ℹ️  La base contient déjà {existing_count} passagers")
            
            # Afficher quelques exemples existants
            existing_passengers = db.query(Passenger).limit(3).all()
            for p in existing_passengers:
                print(f"   ID {p.id}: {p.name}")
            
            return True
        
        print("📊 Insertion des données...")
        for passenger_data in passengers_data:
            passenger = Passenger(**passenger_data)
            db.add(passenger)
        
        db.commit()
        
        # Vérification
        final_count = db.query(Passenger).count()
        print(f"✅ {final_count} passagers insérés avec succès !")
        
        # Afficher quelques exemples
        first_passengers = db.query(Passenger).limit(3).all()
        for p in first_passengers:
            print(f"   ID {p.id}: {p.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion : {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚢 Initialisation des données Titanic")
    print("=" * 40)
    success = init_data()
    if success:
        print("\n🎉 Prêt à utiliser l'API !")
        print("💡 Lancez: python main.py")
    else:
        print("\n💥 Échec de l'initialisation")