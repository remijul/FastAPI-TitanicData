import sys
import os

if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'

from models import SessionLocal, engine, Base, User
from auth import JWTHandler

def create_default_users():
    """Créer des utilisateurs par défaut pour les tests"""
    print("👥 Création des utilisateurs par défaut")
    print("=" * 40)
    
    # Créer les tables si nécessaire
    Base.metadata.create_all(bind=engine)
    
    # Utilisateurs par défaut
    default_users = [
        {
            "email": "admin@titanic.com",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "user@titanic.com", 
            "password": "user123",
            "role": "user"
        },
        {
            "email": "jack@titanic.com",
            "password": "rose123",
            "role": "user"
        }
    ]
    
    db = SessionLocal()
    try:
        for user_data in default_users:
            # Vérifier si l'utilisateur existe déjà
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"ℹ️  {user_data['email']} existe déjà")
                continue
            
            # Créer l'utilisateur
            password_hash = JWTHandler.hash_password(user_data["password"])
            
            user = User(
                email=user_data["email"],
                password_hash=password_hash,
                role=user_data["role"]
            )
            
            db.add(user)
            print(f"✅ Créé: {user_data['email']} ({user_data['role']})")
        
        db.commit()
        print(f"\n🎉 Utilisateurs créés avec succès !")
        
        print("\n📋 Comptes de test disponibles:")
        print("👑 Admin: admin@titanic.com / admin123")
        print("👤 User:  user@titanic.com / user123")
        print("👤 User:  jack@titanic.com / rose123")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    create_default_users()