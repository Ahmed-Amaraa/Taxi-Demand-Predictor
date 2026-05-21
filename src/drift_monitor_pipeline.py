"""
Pipeline MLOps complet: Monitoring drift → Déclenchement automatique du ré-entraînement
Boucle fermée de monitoring et adaptation
"""
import subprocess
from pathlib import Path
import sys
import mlflow
import pandas as pd

# Ensure src directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from simulate_drift import simulate_drift
from detect_drift import detect_drift, detect_drift_evidently, detect_drift_ks_test

# Seuils de drift
SEUIL_DRIFT_CRITIQUE = 0.30  # 30% de features driftées → ré-entraînement obligatoire
SEUIL_DRIFT_ALERTE = 0.15   # 15% → alerte sans ré-entraînement
SEUIL_RETRAIN = 0.25        # Basé sur drift_share d'Evidently

class DriftMonitoringPipeline:
    """Pipeline MLOps complet avec monitoring du drift"""
    
    def __init__(self):
        self.config = Config()
        mlflow.set_tracking_uri(self.config.MLFLOW_TRACKING_URI)
        
    def run(self):
        """Exécute le pipeline complet"""
        print("\n" + "=" * 70)
        print("PIPELINE MLOps - MONITORING & AUTO-RETRAIN")
        print("=" * 70)
        
        # Étape 1: Simuler le drift
        print("\n[1/4] Simulation du drift sur données de production...")
        X_train, X_test, X_prod = simulate_drift(
            drift_factor=1.6,
            noise_std=0.5,
            features_to_drift=2
        )
        
        if X_prod is None:
            print("❌ Impossible de simuler le drift")
            return False
        
        # Étape 2: Détecter le drift
        print("\n[2/4] Détection du drift...")
        drift_metrics, ks_results = detect_drift(X_train, X_prod)
        
        if drift_metrics is None:
            print("❌ Impossible de détecter le drift")
            return False
        
        # Étape 3: Décider si ré-entraînement nécessaire
        print("\n[3/4] Analyse du drift et décision...")
        decision = self._analyze_and_decide(drift_metrics, ks_results)
        
        # Étape 4: Déclencher actions si nécessaire
        print("\n[4/4] Exécution des actions...")
        self._trigger_actions(decision, drift_metrics)
        
        print("\n" + "=" * 70)
        print("✅ Pipeline complet!")
        print("=" * 70)
        return True
    
    def _analyze_and_decide(self, drift_metrics, ks_results):
        """
        Analyse les métriques et décide si ré-entraînement nécessaire
        Retourne: 'RETRAIN', 'ALERT', ou 'OK'
        """
        drift_share = drift_metrics['drift_share']
        drifted_columns = drift_metrics['drifted_columns']
        total_columns = drift_metrics['total_columns']
        dataset_drift = drift_metrics['dataset_drift']
        
        # Calculer le ratio de features driftées
        drift_ratio = drifted_columns / total_columns if total_columns > 0 else 0
        
        print("\n📊 ANALYSE DU DRIFT:")
        print(f"  • Drift share (Evidently): {drift_share:.2%}")
        print(f"  • Ratio features driftées: {drift_ratio:.2%}")
        print(f"  • Dataset drift: {'OUI ⚠️' if dataset_drift else 'NON ✅'}")
        
        # Seuils d'alerte
        if drift_share > SEUIL_RETRAIN or drift_ratio > SEUIL_DRIFT_CRITIQUE:
            print(f"\n🚨 CRITIQUE: Drift {drift_share:.2%} > seuil {SEUIL_RETRAIN:.0%}")
            return 'RETRAIN'
        
        elif drift_ratio > SEUIL_DRIFT_ALERTE or dataset_drift:
            print(f"\n⚠️  ALERTE: Drift {drift_share:.2%} — surveillance renforcée")
            return 'ALERT'
        
        else:
            print(f"\n✅ OK: Drift {drift_share:.2%} — modèle stable")
            return 'OK'
    
    def _trigger_actions(self, decision, drift_metrics):
        """
        Déclenche les actions appropriées selon la décision
        """
        mlflow.set_experiment('monitoring_drift')
        
        with mlflow.start_run(run_name='drift_decision'):
            mlflow.log_metric('drift_share', drift_metrics['drift_share'])
            
            if decision == 'RETRAIN':
                print("\n🔄 Déclenchement du ré-entraînement...")
                self._trigger_retraining()
                mlflow.log_metric('retrain_triggered', 1)
                
            elif decision == 'ALERT':
                print("\n📢 Alerte enregistrée - Surveillance renforcée")
                mlflow.log_metric('retrain_triggered', 0)
                mlflow.log_param('alert_level', 'warning')
                
            else:
                print("\n✅ Pas d'action nécessaire")
                mlflow.log_metric('retrain_triggered', 0)
                mlflow.log_param('alert_level', 'ok')
    
    def _trigger_retraining(self):
        """
        Lance le ré-entraînement automatique
        """
        try:
            print("  • Lancement du script d'entraînement...")
            result = subprocess.run(
                ['python', 'src/train.py'],
                cwd=self.config.PROJECT_DIR,
                capture_output=True,
                text=True,
                timeout=3600  # 1 heure max
            )
            
            if result.returncode == 0:
                print("  ✅ Ré-entraînement complété avec succès!")
                print("\n  Prochaines étapes:")
                print("  1. Validez le nouveau modèle")
                print("  2. Enregistrez-le dans le Model Registry")
                print("  3. Mettez-le en staging/production")
            else:
                print(f"  ❌ Erreur lors du ré-entraînement: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("  ❌ Ré-entraînement timeout (1h dépassée)")
        except Exception as e:
            print(f"  ❌ Erreur lors du lancement du ré-entraînement: {e}")

def visualize_pipeline():
    """Affiche le diagramme du pipeline MLOps"""
    pipeline_diagram = """
    
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                    PIPELINE MLOps COMPLET                                ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║  [1] Données brutes                                                    ║
    ║      ↓                                                                  ║
    ║  [2] Prétraitement (Data Pipelines)                                    ║
    ║      ↓                                                                  ║
    ║  [3] Entraînement (MLflow Tracking)                                    ║
    ║      ├── Params, métriques, artefacts loggés                           ║
    ║      ↓                                                                  ║
    ║  [4] Model Registry (MLflow)                                            ║
    ║      ├── Staging → Production                                           ║
    ║      ↓                                                                  ║
    ║  [5] Serving API (Flask/FastAPI)                                        ║
    ║      ├── Predictions à la demande                                       ║
    ║      ↓                                                                  ║
    ║  [6] Monitoring du drift (Evidently + KS-test)                          ║
    ║      ├── Détection du drift                                             ║
    ║      ├── Rapports HTML visuels                                          ║
    ║      ↓                                                                  ║
    ║  [7] Décision automatique                                               ║
    ║      ├── drift > 30% ? → OUI → Retour à [3] (ré-entraînement) BOUCLE   ║
    ║      └── drift < 15% ? → NON → Surveillance continue                   ║
    ║                                                                          ║
    ║  SEUILS DE DRIFT:                                                       ║
    ║  • CRITIQUE (>30%): ré-entraînement automatique                         ║
    ║  • ALERTE (>15%): alerte + surveillance renforcée                       ║
    ║  • OK (<15%): modèle stable, sans action                                ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
    """
    print(pipeline_diagram)

if __name__ == '__main__':
    # Afficher le diagramme
    visualize_pipeline()
    
    # Exécuter le pipeline
    pipeline = DriftMonitoringPipeline()
    success = pipeline.run()
    
    if success:
        print("\n📚 Documentation:")
        print("  • Rapports Evidently: results/drift_reports/drift_report_evidently.html")
        print("  • Résultats KS-test: results/drift_reports/ks_drift_results.csv")
        print("  • MLflow: http://localhost:5000")
