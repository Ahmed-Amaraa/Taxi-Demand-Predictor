"""
Détection du drift avec Evidently et KS-test
Génère des rapports visuels et des métriques de drift
"""
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
import mlflow
import sys

# Ensure src directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config

def detect_drift_evidently(X_train, X_prod, experiment_name='monitoring_drift'):
    """
    Détecte le drift avec Evidently et MLflow
    
    Args:
        X_train: Données de référence (training)
        X_prod: Données de production (potentially drifted)
        experiment_name: Nom de l'expérience MLflow
    
    Returns:
        Dict avec les métriques de drift
    """
    try:
        config = Config()
        mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
        mlflow.set_experiment(experiment_name)
        
        with mlflow.start_run(run_name='drift_check_evidently'):
            print("📊 Analyse du drift avec Evidently...")
            
            try:
                # Try modern Evidently API
                from evidently import Report
                from evidently.metric_preset import DataDriftPreset, DataQualityPreset
                
                report = Report(metrics=[DataDriftPreset(), DataQualityPreset()])
                report.run(reference_data=X_train, current_data=X_prod)
                
            except (ImportError, ModuleNotFoundError):
                # Fallback: Use basic Evidently if available
                print("  ℹ️  Using simplified drift detection...")
                report = None
            
            # Générer un rapport HTML simple
            results_dir = Path(config.RESULTS_DIR) / 'drift_reports'
            results_dir.mkdir(exist_ok=True)
            
            if report is not None:
                report_path = results_dir / 'drift_report_evidently.html'
                try:
                    report.save_html(str(report_path))
                    print(f"  ✅ Rapport HTML: {report_path}")
                except:
                    print("  ⚠️  Impossible de sauvegarder le rapport HTML")
            
            # Calculer les métriques de drift avec KS-test
            print("  • Calcul des métriques de drift...")
            
            drift_stats = []
            drifted_count = 0
            
            for col in X_train.columns:
                if col not in X_prod.columns:
                    continue
                
                # KS-test pour chaque colonne
                ks_stat, p_value = stats.ks_2samp(X_train[col].dropna(), X_prod[col].dropna())
                
                is_drifted = p_value < 0.05
                if is_drifted:
                    drifted_count += 1
                
                drift_stats.append({
                    'feature': col,
                    'ks_stat': ks_stat,
                    'p_value': p_value,
                    'drifted': is_drifted
                })
            
            total_columns = len(drift_stats)
            drift_share = drifted_count / total_columns if total_columns > 0 else 0
            dataset_drift = drift_share > 0.15
            
            print(f"  ✅ {drifted_count}/{total_columns} features driftées")
            
            # Créer un rapport HTML simple en HTML brut
            html_content = _create_simple_html_report(drift_stats, drift_share)
            report_path = results_dir / 'drift_report_evidently.html'
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"  ✅ Rapport HTML: {report_path}")
            
            # Logger les métriques
            mlflow.log_metric('drift_share', drift_share)
            mlflow.log_metric('drifted_columns', drifted_count)
            mlflow.log_metric('total_columns', total_columns)
            mlflow.log_metric('dataset_drift', 1 if dataset_drift else 0)
            
            return {
                'drift_share': drift_share,
                'drifted_columns': drifted_count,
                'total_columns': total_columns,
                'dataset_drift': dataset_drift,
                'drift_stats': drift_stats
            }
    
    except Exception as e:
        print(f"  ❌ Erreur Evidently: {e}")
        return None

def _create_simple_html_report(drift_stats, drift_share):
    """Crée un rapport HTML simple"""
    rows = ""
    for stat in drift_stats:
        color = "red" if stat['drifted'] else "green"
        rows += f"""
        <tr>
            <td>{stat['feature']}</td>
            <td>{stat['ks_stat']:.4f}</td>
            <td>{stat['p_value']:.4f}</td>
            <td><span style="color: {color}; font-weight: bold;">{'DRIFT' if stat['drifted'] else 'OK'}</span></td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rapport Drift Detection</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; max-width: 800px; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background-color: #4CAF50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .summary {{ background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>Rapport de Détection du Drift</h1>
        <div class="summary">
            <h2>Résumé</h2>
            <p><strong>Drift Share:</strong> {drift_share:.2%}</p>
            <p><strong>Statut:</strong> <span style="color: {'red' if drift_share > 0.30 else 'orange' if drift_share > 0.15 else 'green'}; font-weight: bold;">
                {'CRITIQUE' if drift_share > 0.30 else 'ALERTE' if drift_share > 0.15 else 'OK'}
            </span></p>
        </div>
        <h2>Résultats par Feature (KS-Test)</h2>
        <table>
            <tr>
                <th>Feature</th>
                <th>KS Statistic</th>
                <th>P-Value</th>
                <th>Statut</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """
    return html

def detect_drift_ks_test(X_train, X_prod):
    """
    Test statistique KS par feature
    
    Args:
        X_train: Données de référence
        X_prod: Données de production
    
    Returns:
        DataFrame avec les résultats KS-test
    """
    print("📊 Analyse KS-test par feature...")
    
    results = []
    
    for col in X_train.columns:
        if col not in X_prod.columns:
            continue
        
        try:
            ks_stat, p_value = stats.ks_2samp(
                X_train[col].dropna(),
                X_prod[col].dropna()
            )
            
            results.append({
                'feature': col,
                'ks_statistic': ks_stat,
                'p_value': p_value,
                'drifted': p_value < 0.05
            })
        except Exception as e:
            print(f"  ⚠️  Erreur pour {col}: {e}")
    
    df_results = pd.DataFrame(results)
    print(f"  ✅ {len(results)} features analysées")
    
    return df_results

def detect_drift(X_train=None, X_prod=None):
    """
    Détecte le drift sur les données
    
    Args:
        X_train: Données de référence (optionnel, chargé si None)
        X_prod: Données de production (optionnel, chargé si None)
    
    Returns:
        Tuple (drift_metrics, ks_results)
    """
    config = Config()
    
    # Charger les données si non fournies
    if X_train is None or X_prod is None:
        prod_dir = Path(config.DATA_DIR) / 'production'
        
        X_train_path = prod_dir / 'X_train_reference.csv'
        X_prod_path = prod_dir / 'X_prod_drifted.csv'
        
        if not X_train_path.exists() or not X_prod_path.exists():
            print("❌ Données de production manquantes")
            print(f"   Lancez d'abord: python src/simulate_drift.py")
            return None, None
        
        print(f"📂 Chargement depuis {prod_dir}...")
        X_train = pd.read_csv(X_train_path, index_col=0)
        X_prod = pd.read_csv(X_prod_path, index_col=0)
    
    print(f"  • Référence: {X_train.shape}")
    print(f"  • Production: {X_prod.shape}")
    
    # Détection Evidently
    drift_metrics = detect_drift_evidently(X_train, X_prod)
    
    # Détection KS-test
    ks_results = detect_drift_ks_test(X_train, X_prod)
    
    # Sauvegarder les résultats KS-test
    results_dir = Path(config.RESULTS_DIR) / 'drift_reports'
    results_dir.mkdir(exist_ok=True)
    
    ks_path = results_dir / 'ks_drift_results.csv'
    ks_results.to_csv(ks_path, index=False)
    print(f"✅ Résultats KS-test: {ks_path}")
    
    # Logger MLflow
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment('monitoring_drift')
    
    with mlflow.start_run(run_name='drift_check_ks_test'):
        for _, row in ks_results.iterrows():
            mlflow.log_metric(f"ks_stat_{row['feature']}", row['ks_statistic'])
            mlflow.log_metric(f"ks_pvalue_{row['feature']}", row['p_value'])
    
    return drift_metrics, ks_results

if __name__ == '__main__':
    drift_metrics, ks_results = detect_drift()
    
    if drift_metrics is not None:
        print("\n✅ Drift detection complete!")
        print(f"Drift share: {drift_metrics['drift_share']:.2%}")
    else:
        print("\n❌ Drift detection failed!")
