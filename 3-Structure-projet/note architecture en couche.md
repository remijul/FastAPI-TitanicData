# 🏗️ Architecture en couches - Bénéfices

## Flux de données typique :

```txt
HTTP Request → API Layer → Service Layer → Data Layer → Database
                ↓              ↓             ↓
            Validation    Logique métier   Persistance
                ↓              ↓             ↓
HTTP Response ← Sérialisation ← Traitement ← Données
```

## Avantages de cette organisation :

- 🔄 Testabilité : Chaque couche peut être testée indépendamment
- 🔧 Maintenabilité : Modifications isolées par responsabilité
- 📈 Évolutivité : Facile d'ajouter de nouvelles fonctionnalités
- 👥 Collaboration : Équipes peuvent travailler sur différentes couches
- 🎯 Lisibilité : Code organisé et prévisible

## Règles de dépendance :

- API → Services (peut appeler)
- Services → Models (peut appeler)
- Models ← Services ← API (ne remonte jamais)

## 💡 Concepts pédagogiques clés

### 1. Separation of Concerns

Chaque module a UNE responsabilité claire :

- `models/` = Données
- `services/` = Logique métier
- `api/` = Interface HTTP
- `schemas/` = Validation
- `exceptions/` = Gestion d'erreurs

### 2. Dependency Injection

```python
def get_passenger(db: Session = Depends(get_db)):
    # FastAPI injecte automatiquement la session DB
```

### 3. Single Source of Truth

- Une seule définition du modèle Passenger
- Un seul endroit pour la logique métier
- Un seul format de réponse

### 4. Don't Repeat Yourself (DRY)

- Fonctions utilitaires réutilisées
- Configuration centralisée
- Validation factorisée

Cette architecture vous prépare aux projets professionnels où la maintenabilité et la collaboration sont essentielles ! 🎯✨