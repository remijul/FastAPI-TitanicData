"""
Script pour exécuter tous les tests avec rapport détaillé
"""
import subprocess
import sys
import os

def run_tests():
    """Exécuter tous les tests avec pytest"""
    print("🧪 Exécution des tests automatisés")
    print("=" * 50)
    
    # Commandes pytest avec options détaillées
    test_commands = [
        # Tests de base avec verbose
        ["pytest", "tests/", "-v", "--tb=short"],
        
        # Tests avec coverage si disponible
        ["pytest", "tests/", "--cov=.", "--cov-report=term-missing", "-v"],
        
        # Tests spécifiques par module
        ["pytest", "tests/test_auth.py", "-v"],
        ["pytest", "tests/test_passengers.py", "-v"],
    ]
    
    for i, cmd in enumerate(test_commands):
        print(f"\n{'='*20} Commande {i+1}/{len(test_commands)} {'='*20}")
        print(f"Exécution: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                print("✅ Tests réussis")
                print(result.stdout)
            else:
                print("❌ Tests échoués")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
            # Arrêter après le premier test réussi pour éviter la redondance
            if result.returncode == 0:
                break
                
        except FileNotFoundError:
            print(f"⚠️  Commande non trouvée: {cmd[0]}")
            continue
        except Exception as e:
            print(f"❌ Erreur: {e}")
            continue
    
    print(f"\n🎉 Tests terminés")

if __name__ == "__main__":
    run_tests()