# 📊 Comment lire le rapport de couverture HTML

Le rapport de couverture HTML est un tableau de bord visuel qui vous montre précisément quelles parties de votre code sont testées. Voici comment l'utiliser :

## 🌐 Ouvrir le rapport

1. Localiser le fichier

```bash
# Le rapport se trouve dans le dossier htmlcov/
ls htmlcov/
# Vous devriez voir : index.html (+ autres fichiers)
```

2. Ouvrir dans le navigateur

```bash
# Option 1 : Double-clic sur le fichier
htmlcov/index.html

# Option 2 : Depuis la ligne de commande (Windows)
start htmlcov/index.html

# Option 3 : Chemin complet dans le navigateur
file:///C:/chemin/vers/votre/projet/htmlcov/index.html
```

## 📈 Comprendre le rapport principal (`index.html`)

### Page d'accueil - Vue d'ensemble

```txt
┌─────────────────────────────────────────────────────────┐
│ Coverage Report                                         │
├─────────────────────────────────────────────────────────┤
│ Total coverage: 85%                    📊               │
│                                                         │
│ Module               Statements  Missing  Coverage      │
│ ─────────────────────────────────────────────────────   │
│ api/routes.py            45        3       93%   🟢     │
│ auth/jwt_handler.py      20        5       75%   🟡     │
│ services/passenger.py    35        8       77%   🟡     │
│ models/user.py           15        0      100%   🟢     │
│ main.py                  10        2       80%   🟡     │
└─────────────────────────────────────────────────────────┘
```

### Codes couleur

- 🟢 **Vert** (90-100%) : Très bien couvert
- 🟡 **Jaune** (70-89%) : Correctement couvert
- 🟠 **Orange** (50-69%) : Peu couvert
- 🔴 **Rouge** (0-49%) : Mal couvert

## 🔍 Analyser un fichier spécifique

### Cliquer sur un fichier (ex: `api/routes.py`)

```python
# Les lignes sont colorées :

def get_passengers(skip: int = 0, limit: int = 100):    # 🟢 Ligne testée
    try:                                                # 🟢 Ligne testée
        return PassengerService.get_all(db, skip, limit) # 🟢 Ligne testée
    except DatabaseError as e:                          # 🔴 Ligne NON testée
        raise HTTPException(status_code=500, detail=e)  # 🔴 Ligne NON testée
```

### Légende des couleurs de lignes

- 🟢 **Vert** : Ligne exécutée par les tests
- 🔴 **Rouge** : Ligne jamais exécutée
- 🟡 **Jaune** : Ligne partiellement couverte (ex: une branche if/else)

## 📊 Métriques importantes

1. Statements

Nombre total de lignes de code exécutables

```python
# 3 statements
x = 1
if x > 0:
    print("positif")
```

2. Missing

Nombre de lignes jamais exécutées par les tests

3. Coverage %

Pourcentage de lignes testées

```txt
Coverage = (Statements - Missing) / Statements × 100
```

## 🎯 Interpréter les résultats

### Excellente couverture (90-100%)

```txt
✅ auth/dependencies.py     12     0    100%
✅ models/passenger.py      25     1     96%
```

**Signification** : Code très bien testé, peu de risques

### Couverture correcte (70-89%)

```txt
🟡 services/passenger.py    45     8     82%
🟡 api/routes.py           38     6     84%
```

**Signification** : Bon niveau, quelques cas d'erreur manquent

### Couverture faible (< 70%)

```txt
🔴 utils/helpers.py        20    12     40%
🔴 exceptions/custom.py    15     9     40%
```

**Signification** : Beaucoup de code non testé, risqué

## 🔧 Actions concrètes selon le rapport

### Si une fonction est en rouge

```python
# Fonction non testée
def calculate_survival_rate(passengers):  # 🔴 0% couverture
    if not passengers:                    # 🔴 Jamais testé
        return 0                          # 🔴 Jamais testé
    survivors = sum(1 for p in passengers if p.survived)  # 🔴
    return (survivors / len(passengers)) * 100            # 🔴
```

**Action** : Créer un test

```python
def test_calculate_survival_rate():
    passengers = [{"survived": True}, {"survived": False}]
    rate = calculate_survival_rate(passengers)
    assert rate == 50.0
```

### Si des exceptions ne sont pas testées

```python
def get_passenger(db, id):
    try:                           # 🟢 Testé
        return db.query(...).first()  # 🟢 Testé
    except DatabaseError:         # 🔴 Exception jamais testée
        raise HTTPException(...)   # 🔴 Jamais exécuté
```

**Action** : Tester le cas d'erreur

```python
def test_get_passenger_database_error(mocker):
    mocker.patch('db.query').side_effect = DatabaseError()
    with pytest.raises(HTTPException):
        get_passenger(db, 1)
```

## 📋 Exemple d'analyse complète

### Votre rapport pourrait ressembler à :

```txt
Module                    Statements   Missing   Coverage
─────────────────────────────────────────────────────────
main.py                       12          2        83%    🟡
api/routes.py                 45          5        89%    🟢
api/auth_routes.py            32          8        75%    🟡
auth/jwt_handler.py           28          3        89%    🟢
auth/auth_service.py          55         12        78%    🟡
services/passenger_service.py 67          9        87%    🟢
models/user.py                15          0       100%    🟢
models/passenger.py           18          0       100%    🟢
schemas/auth.py               25          5        80%    🟡
─────────────────────────────────────────────────────────
TOTAL                        297         44        85%    🟢
```

### Priorités d'amélioration

1. **auth/auth_service.py** (78%) : 12 lignes manquantes → Tester les cas d'erreur
2. **api/auth_routes.py** (75%) : 8 lignes manquantes → Tester les validations
3. **schemas/auth.py** (80%) : 5 lignes manquantes → Tester les validateurs

## 🎯 Objectifs de couverture

### Pour un projet pédagogique

- **70-80%** : Acceptable ✅
- **80-90%** : Bien 🟢
- **90%+** : Excellent 🏆

### Pour un projet professionnel

- **Minimum 80%** pour les modules critiques
- **90%+** pour les fonctions de sécurité
- **95%+** pour les fonctions financières/critiques

## 🚀 Commandes utiles

```bash
# Générer le rapport HTML
pytest tests/ --cov=. --cov-report=html

# Ouvrir automatiquement le rapport
pytest tests/ --cov=. --cov-report=html && start htmlcov/index.html

# Rapport dans le terminal + HTML
pytest tests/ --cov=. --cov-report=term --cov-report=html

# Exclure certains fichiers
pytest tests/ --cov=. --cov-report=html --cov-omit="*/tests/*,*/venv/*"
```

Le rapport de couverture est votre **GPS pour améliorer la qualité** de vos tests ! 🗺️✨
