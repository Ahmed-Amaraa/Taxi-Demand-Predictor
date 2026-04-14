# Guide de Démarrage Rapide

## 🚀 Lancer l'Application

### Terminal 1 - Backend (FastAPI)
```bash
cd src/api
pip install -r requirements.txt
python main.py
```

Attendez le message: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2 - Frontend (React)
```bash
cd frontend
npm install   # (première fois seulement)
npm run dev
```

Attendez le message: `Local: http://localhost:3000`

## ✅ Vérifier que tout fonctionne

1. Allez à `http://localhost:3000` dans votre navigateur
2. Vous devriez voir l'interface Taxi Demand Predictor
3. Si vous voyez "API Connection Error":
   - Vérifiez que le backend est lancé sur le terminal 1
   - Attendez quelques secondes et cliquez "Retry Connection"

## 📝 Utiliser l'Application

1. **Remplissez les features** - 10 valeurs numériques
2. **Cliquez "Predict"** - Pour obtenir une prédiction
3. **Cliquez "Random Values"** - Pour remplir avec des valeurs aléatoires
4. **Cliquez "Reset"** - Pour réinitialiser le formulaire

## 🛠️ API Documentation

Accédez à: `http://localhost:8000/docs` pour la documentation Swagger interactive

## 📊 Exemple de Prédiction

Pour tester avec curl:
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [0.5, 1.2, 0.3, 2.1, 0.8, 1.5, 0.9, 0.6, 1.1, 0.4]}'
```

## 🔧 Fichiers Configurables

- **Nombre de features**: Modifiez `EXPECTED_FEATURES` dans `src/api/config.py`
- **Ports**: Modifiez dans les fichiers de config respectifs
- **CORS origins**: Modifiez dans `src/api/main.py` si le frontend est sur un port différent

---

**C'est tout! Votre application est prête à fonctionner! 🎉**
