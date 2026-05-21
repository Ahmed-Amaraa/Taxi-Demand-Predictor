# Pre-Commit Hook for Model Validation

Ce dossier contient les Git hooks personnalisés pour valider la qualité du modèle ML avant chaque commit.

## Configuration

### Sur Windows:
```bash
make setup-hooks
```

Ou manuellement:
```bash
git config core.hooksPath .githooks
```

### Sur Linux/Mac:
```bash
bash setup-hooks.sh
```

Ou manuellement:
```bash
git config core.hooksPath .githooks
chmod +x .githooks/pre-commit
```

## Fichiers

- **pre-commit** - Hook bash (pour Linux/Mac)
- **pre-commit.bat** - Hook batch (pour Windows)
- **setup-hooks.sh** - Script de configuration (Linux/Mac)
- **setup-hooks.bat** - Script de configuration (Windows) - Exécutable via `make setup-hooks`

## Fonctionnement

Le hook `pre-commit` vérifie que l'**accuracy du meilleur modèle** est >= 0.80 avant chaque commit.

Si l'accuracy est inférieure à 0.80:
- Le commit est **refusé**
- Un message d'erreur s'affiche

Si aucune expérience MLflow n'est trouvée:
- Le hook est **ignoré** et le commit est autorisé

## Résolution des problèmes

### Le hook ne s'exécute pas:
1. Vérifiez que Git hooks est configuré: `git config core.hooksPath`
2. Assurez-vous que le fichier est exécutable (Linux/Mac): `chmod +x .githooks/pre-commit`

### Bypass du hook (si nécessaire):
```bash
git commit --no-verify
```

### Modifier la valeur d'accuracy seuil:
Éditez le fichier `.githooks/pre-commit` ou `.githooks/pre-commit.bat` et changez la valeur `0.80`.
