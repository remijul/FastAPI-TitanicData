import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration encodage pour Windows
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# URL de connexion PostgreSQL
DATABASE_URL = "postgresql://titanic_user:titanic_password@localhost:5432/titanic_db"

print(f"🔗 Connexion à la base : postgresql://titanic_user:***@localhost:5432/titanic_db")

# Moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
    echo=False  # True pour voir les requêtes SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance pour obtenir une session de base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Tester la connexion à la base de données"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT current_database(), current_user"))
            row = result.fetchone()
            print(f"✅ Connexion réussie ! Base: {row[0]}, Utilisateur: {row[1]}")
            return True
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        print("💡 Vérifications :")
        print("   - PostgreSQL est-il démarré ?")
        print("   - La base 'titanic_db' existe-t-elle ?")
        print("   - L'utilisateur 'titanic_user' existe-t-il ?")
        return False

if __name__ == "__main__":
    test_connection()