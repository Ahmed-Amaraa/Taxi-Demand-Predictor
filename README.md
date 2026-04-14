# Taxi Demand Prediction - Full Stack Application

Ce projet est une application full-stack pour prédire la demande de taxi utilisant un modèle ML entraîné, une API FastAPI et un frontend React.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                       │
│                    (Port: 3000)                         │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP/REST
                         ↓
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                        │
│                 (Port: 8000)                            │
│         Endpoints: /predict, /batch-predict            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ↓
                  ┌──────────────┐
                  │ ML Model     │
                  │ (joblib)     │
                  └──────────────┘
```

## Structure du Projet

```
taxi/
├── src/
│   ├── api/                          # FastAPI application
│   │   ├── main.py                  # Application principale
│   │   ├── config.py                # Configuration
│   │   └── requirements.txt          # Dépendances Python
│   ├── models/
│   │   └── taxi_demand.joblib       # Modèle ML entraîné
│   └── ...
├── frontend/                         # Application React
│   ├── src/
│   │   ├── components/              # Composants React
│   │   │   ├── PredictionForm.jsx
│   │   │   ├── PredictionResult.jsx
│   │   │   └── ModelInfo.jsx
│   │   ├── styles/                  # Fichiers CSS
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   └── ...
└── README.md
```

## Installation et Démarrage

### 1. Backend - FastAPI

#### Installer les dépendances

```bash
cd src/api
pip install -r requirements.txt
```

#### Démarrer le serveur API

```bash
python main.py
```

Ou avec uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera disponible à: `http://localhost:8000`
- Documentation Swagger: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Frontend - React

#### Installer les dépendances Node

```bash
cd frontend
npm install
```

#### Démarrer le serveur de développement

```bash
npm run dev
```

L'application sera disponible à: `http://localhost:3000`

## Endpoints API

### `/health` (GET)
Vérifier l'état de l'API et du modèle

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### `/predict` (POST)
Faire une prédiction pour une entrée

**Request Body:**
```json
{
  "features": [0.5, 1.2, 0.3, 2.1, 0.8, 1.5, 0.9, 0.6, 1.1, 0.4]
}
```

**Response:**
```json
{
  "prediction": 42.5,
  "message": "Predicted taxi demand: 42.50"
}
```

### `/batch-predict` (POST)
Faire des prédictions pour plusieurs entrées

**Request Body:**
```json
[
  {"features": [0.5, 1.2, 0.3, 2.1, 0.8, 1.5, 0.9, 0.6, 1.1, 0.4]},
  {"features": [0.6, 1.3, 0.4, 2.2, 0.9, 1.6, 1.0, 0.7, 1.2, 0.5]}
]
```

**Response:**
```json
{
  "predictions": [42.5, 45.3],
  "count": 2,
  "message": "Predicted demand for 2 inputs"
}
```

### `/model-info` (GET)
Obtenir les informations sur le modèle chargé

**Response:**
```json
{
  "model_type": "RandomForestRegressor",
  "model_path": "...",
  "status": "ready"
}
```

## Communication Frontend-Backend

### Flux de requête

1. **Frontend**: L'utilisateur remplit le formulaire avec les features
2. **Frontend**: Envoie une requête POST à `http://localhost:8000/predict`
3. **Backend**: Reçoit la requête, valide les données
4. **Backend**: Utilise le modèle ML pour faire la prédiction
5. **Backend**: Retourne le résultat JSON
6. **Frontend**: Affiche le résultat à l'utilisateur

### Headers CORS

Le backend accepte les requêtes de:
- `http://localhost:3000` (Frontend React en développement)
- `http://127.0.0.1:3000`
- `http://localhost:5173` (Vite dev server alternatif)

## Fichiers Importants

### Backend
- `src/api/main.py` - Application FastAPI principale avec tous les endpoints
- `src/api/config.py` - Configuration centralisée
- `src/api/requirements.txt` - Dépendances Python

### Frontend
- `frontend/src/App.jsx` - Composant principal
- `frontend/src/components/PredictionForm.jsx` - Formulaire de prédiction
- `frontend/src/components/PredictionResult.jsx` - Affichage du résultat
- `frontend/src/components/ModelInfo.jsx` - Infos du modèle
- `frontend/package.json` - Dépendances Node.js

## Fonctionnalités

### Frontend
✅ Interface utilisateur moderne et responsive
✅ Formulaire pour entrer les features
✅ Boutons d'action (Predict, Random Values, Reset)
✅ Affichage des résultats de prédiction
✅ Gestion des erreurs
✅ Vérification de l'état de l'API
✅ Design dark theme

### Backend
✅ Validation des données d'entrée
✅ CORS configuré pour le frontend
✅ Documentation Swagger automatique
✅ Health check endpoint
✅ Support pour prédictions simples et batch
✅ Gestion d'erreurs robuste
✅ Informations sur le modèle

## Modification des Features

Si votre modèle a un nombre différent de features, modifiez:

1. **Backend** - `src/api/config.py`:
   ```python
   EXPECTED_FEATURES = 10  # Changez à votre nombre réel
   ```

2. **Frontend** - `frontend/src/components/PredictionForm.jsx`:
   ```javascript
   const [features, setFeatures] = useState(Array(10).fill(0))  // Changez à votre nombre
   const [featureNames] = useState([
     'Feature 1',
     'Feature 2',
     // ... Ajoutez les noms appropriés
   ])
   ```

## Troubleshooting

### "API Connection Error"
- Vérifiez que le server FastAPI est en cours d'exécution
- Port 8000 doit être disponible
- Vérifiez que le modèle existe à `taxi/models/taxi_demand.joblib`

### CORS Errors
- Vérifiez que le frontend s'exécute sur `localhost:3000`
- Vérifiez les paramètres CORS dans `src/api/main.py`

### Model Not Loading
- Vérifiez le chemin du modèle dans `src/api/main.py`
- Assurez-vous que le fichier `.joblib` existe et est valide

## Prochaines Étapes (Optionnel)

- Ajouter l'authentification
- Ajouter une base de données pour historique
- Ajouter des tests unitaires
- Déployer sur Azure/cloud
- Ajouter de plus de visualisations
- Ajouter du logging

## Notes

- Cette architecture n'utilise pas de microservices
- Une seule API pour servir le modèle
- Communication directe REST entre frontend et backend
- Pas de base de données (peut être ajoutée si nécessaire)

---

**Créé avec ❤️ pour la prédiction de demande de taxi**
