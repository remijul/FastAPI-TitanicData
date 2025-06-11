import sys
import os

if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from models.database import SessionLocal, engine, test_connection
from models.passenger import Base, Passenger

def init_data():
    print("🔍 Test de connexion...")
    if not test_connection():
        print("❌ Impossible de se connecter à la base")
        return False

    try:
        print("🏗️  Création des tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tables créées")
    except Exception as e:
        print(f"❌ Erreur tables : {e}")
        return False

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
        existing_count = db.query(Passenger).count()
        if existing_count > 0:
            print(f"ℹ️  Base contient déjà {existing_count} passagers")
            return True
        
        print("📊 Insertion des données...")
        for data in passengers_data:
            passenger = Passenger(**data)
            db.add(passenger)
        
        db.commit()
        final_count = db.query(Passenger).count()
        print(f"✅ {final_count} passagers insérés !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur insertion : {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🚢 Initialisation Atelier 3")
    print("=" * 30)
    if init_data():
        print("\n🎉 Prêt ! Lancez: python main.py")
    else:
        print("\n💥 Échec")