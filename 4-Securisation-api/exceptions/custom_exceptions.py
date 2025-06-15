class PassengerNotFound(Exception):
    """Passager non trouvé"""
    def __init__(self, passenger_id: int):
        self.message = f"Passager avec ID {passenger_id} introuvable"
        super().__init__(self.message)

class ValidationError(Exception):
    """Erreur de validation des données"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class DatabaseError(Exception):
    """Erreur de base de données"""
    def __init__(self, operation: str):
        self.message = f"Erreur lors de l'opération: {operation}"
        super().__init__(self.message)