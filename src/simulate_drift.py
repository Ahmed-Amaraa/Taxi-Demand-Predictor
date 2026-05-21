"""
Simulation du drift sur vos données
Crée un jeu de données de production artificiellement drifté à partir des données de test
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from pathlib import Path
import sys

# Ensure src directory is in path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config

def simulate_drift(drift_factor=1.6, noise_std=0.5, features_to_drift=2):
    """
    Simule le drift des données de production
    
    Args:
        drift_factor: Facteur multiplicatif de drift (1.6 = +60%)
        noise_std: Écart-type du bruit gaussien ajouté
        features_to_drift: Nombre de features affectées par le drift
    
    Returns:
        Tuple (X_train, X_test, X_prod) avec les données
    """
    try:
        config = Config()
        
        # Chercher les données disponibles
        # Essayer d'abord les chemins relatifs depuis le répertoire du projet
        project_root = Path(__file__).resolve().parent.parent
        
        data_paths_to_try = [
            project_root / 'data' / 'train' / 'train.csv',
            project_root / 'src' / 'data' / 'cleaned_data.csv',
            Path(config.DATA_DIR) / 'train' / 'train.csv',
            Path(config.DATA_DIR) / 'cleaned_data.csv',
        ]
        
        data_path = None
        for path in data_paths_to_try:
            if path.exists():
                data_path = path
                break
        
        if data_path is None:
            print(f"❌ Erreur: Impossible de trouver les données")
            print(f"   Chemins cherchés:")
            for p in data_paths_to_try:
                print(f"   - {p}")
            return None, None, None
        
        print(f"📊 Chargement des données depuis {data_path}")
        df = pd.read_csv(data_path)
        print(f"✅ Données chargées: {df.shape}")
        
        # Séparer features et target
        # Essayer différentes colonnes targets
        target_candidates = ['target', 'demand', 'label', 'y']
        target_col = None
        
        for col in target_candidates:
            if col in df.columns:
                target_col = col
                break
        
        if target_col:
            X = df.drop(target_col, axis=1)
            y = df[target_col]
        else:
            # Utiliser la dernière colonne comme target
            X = df.iloc[:, :-1]
            y = df.iloc[:, -1]
        
        # Garder seulement les colonnes numériques
        X = X.select_dtypes(include=np.number)
        
        print(f"✅ Features: {X.shape[0]} lignes, {X.shape[1]} colonnes")
        
        # Train/Test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        print(f"✅ Split: {X_train.shape[0]} train, {X_test.shape[0]} test")
        
        # Simulation du drift
        X_prod = X_test.copy()
        num_cols = X_prod.select_dtypes(include=np.number).columns.tolist()
        
        # Appliquer le drift aux N premières colonnes numériques
        drifted_cols = []
        for col in num_cols[:min(features_to_drift, len(num_cols))]:
            original_mean = X_prod[col].mean()
            X_prod[col] = X_prod[col] * drift_factor + np.random.normal(
                0, noise_std, len(X_prod)
            )
            new_mean = X_prod[col].mean()
            drifted_cols.append({
                'feature': col,
                'original_mean': original_mean,
                'drifted_mean': new_mean,
                'change_percent': ((new_mean - original_mean) / abs(original_mean) * 100) if original_mean != 0 else 0
            })
            print(f"🔄 Feature '{col}': {original_mean:.3f} → {new_mean:.3f} ({drifted_cols[-1]['change_percent']:+.1f}%)")
        
        # Sauvegarder les données driftées
        # Créer le répertoire production dans le même endroit que les données source
        if 'data/train' in str(data_path):
            # Si les données proviennent de data/train, sauvegarder dans data/production
            prod_dir = project_root / 'data' / 'production'
        else:
            prod_dir = Path(config.DATA_DIR) / 'production'
        
        prod_dir.mkdir(exist_ok=True, parents=True)
        
        X_prod.to_csv(prod_dir / 'X_prod_drifted.csv', index=False)
        X_train.to_csv(prod_dir / 'X_train_reference.csv', index=False)
        print(f"✅ Données sauvegardées dans {prod_dir}")
        
        return X_train, X_test, X_prod
        
    except Exception as e:
        print(f"❌ Erreur lors de la simulation du drift: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == '__main__':
    print("=" * 60)
    print("Simulation du drift - Données de production")
    print("=" * 60)
    
    X_train, X_test, X_prod = simulate_drift(
        drift_factor=1.6,      # 60% de décalage
        noise_std=0.5,         # Bruit gaussien
        features_to_drift=2    # 2 premières features affectées
    )
    
    if X_prod is not None:
        print("\n" + "=" * 60)
        print("✅ Simulation complète!")
        print("=" * 60)
        print("\nProchaines étapes:")
        print("1. Analysez le drift: python src/detect_drift.py")
        print("2. Lancez le pipeline complet: python src/drift_monitor_pipeline.py")
