"""Exemples pour enrichir la documentation OpenAPI"""

# Exemples de réponses pour les schémas
passenger_example = {
    "id": 1,
    "name": "Braund, Mr. Owen Harris",
    "sex": "male",
    "age": 22.0,
    "survived": False,
    "pclass": 3,
    "fare": 7.25,
    "embarked": "S"
}

passenger_create_example = {
    "name": "Nouveau, Mr. Passager",
    "sex": "male",
    "age": 30,
    "survived": True,
    "pclass": 2,
    "fare": 25.0,
    "embarked": "S"
}

passenger_update_example = {
    "age": 31,
    "fare": 26.50
}

user_login_example = {
    "email": "user@titanic.com",
    "password": "user123"
}

user_register_example = {
    "email": "nouveau@titanic.com",
    "password": "motdepasse123",
    "role": "user"
}

token_response_example = {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "email": "user@titanic.com",
        "role": "user",
        "is_active": True
    }
}

success_response_example = {
    "success": True,
    "message": "Opération réussie",
    "data": [passenger_example],
    "count": 1
}

error_response_example = {
    "success": False,
    "message": "Passager non trouvé",
    "data": None,
    "count": 0
}