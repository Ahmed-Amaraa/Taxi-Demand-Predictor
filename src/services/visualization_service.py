import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from config import Config


def _to_1d(a):
    return np.asarray(a).reshape(-1)


class VisualizationService:
    """Service pour créer des visualisations interactives"""

    def __init__(self):
        self.config = Config()
        self.output_dir = os.path.join(self.config.RESULTS_DIR, "visualizations")
        os.makedirs(self.output_dir, exist_ok=True)
        sns.set_style("whitegrid")
    
    def _convert_path_to_url(self, file_path):
        """Convertit un chemin absolu en URL relative pour l'API"""
        # Extraire le nom du fichier
        filename = os.path.basename(file_path)
        return f"/api/visualizations/{filename}"

    def plot_predictions_vs_actual(self, y_test, y_pred, model_name, run_id):
        y_true = _to_1d(y_test)
        y_hat = _to_1d(y_pred)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=y_true,
            y=y_hat,
            mode="markers",
            name="Prédictions",
            marker=dict(size=8, color=y_true, colorscale="Viridis", showscale=True),
            text=[f"Réel: {r:.2f}<br>Prédit: {p:.2f}" for r, p in zip(y_true, y_hat)],
            hovertemplate="%{text}<extra></extra>"
        ))

        min_val = min(y_true.min(), y_hat.min())
        max_val = max(y_true.max(), y_hat.max())
        fig.add_trace(go.Scatter(
            x=[min_val, max_val], y=[min_val, max_val],
            mode="lines", name="Prédiction parfaite",
            line=dict(color="red", dash="dash")
        ))

        fig.update_layout(
            title=f"Prédictions vs Valeurs réelles - {model_name}",
            xaxis_title="Valeurs réelles",
            yaxis_title="Valeurs prédites",
            width=900, height=700
        )

        file_path = os.path.join(self.output_dir, f"{model_name}_{run_id}_predictions_vs_actual.html")
        fig.write_html(file_path)
        return {"type": "scatter", "file_path": self._convert_path_to_url(file_path), "description": "Graphique de prédictions vs valeurs réelles"}

    def plot_residuals(self, y_test, y_pred, model_name, run_id):
        y_true = _to_1d(y_test)
        y_hat = _to_1d(y_pred)
        residuals = y_true - y_hat

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=y_hat, y=residuals, mode="markers", name="Résidus",
            marker=dict(size=8, color=np.abs(residuals), colorscale="Reds", showscale=True)
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="blue")
        fig.update_layout(
            title=f"Analyse des Résidus - {model_name}",
            xaxis_title="Valeurs prédites",
            yaxis_title="Résidus",
            width=900, height=700
        )

        file_path = os.path.join(self.output_dir, f"{model_name}_{run_id}_residuals.html")
        fig.write_html(file_path)
        return {"type": "residuals", "file_path": self._convert_path_to_url(file_path), "description": "Graphique des résidus"}

    def plot_error_distribution(self, y_test, y_pred, model_name, run_id):
        y_true = _to_1d(y_test)
        y_hat = _to_1d(y_pred)
        errors = np.abs(y_true - y_hat)

        fig = go.Figure()
        fig.add_trace(go.Histogram(x=errors, nbinsx=30, name="Erreurs absolues"))
        fig.update_layout(
            title=f"Distribution des erreurs - {model_name}",
            xaxis_title="Erreur absolue",
            yaxis_title="Fréquence",
            width=900, height=600
        )

        file_path = os.path.join(self.output_dir, f"{model_name}_{run_id}_error_distribution.html")
        fig.write_html(file_path)
        return {"type": "histogram", "file_path": self._convert_path_to_url(file_path), "description": "Distribution des erreurs"}

    def export_results_to_csv(self, y_test, y_pred, model_name, run_id):
        y_true = _to_1d(y_test)
        y_hat = _to_1d(y_pred)

        denom = np.where(y_true == 0, np.nan, y_true)
        results_df = pd.DataFrame({
            "Valeur_Reelle": y_true,
            "Valeur_Predite": y_hat,
            "Erreur_Absolue": np.abs(y_true - y_hat),
            "Erreur_Pourcentage": (np.abs(y_true - y_hat) / np.abs(denom)) * 100,
        })

        file_path = os.path.join(self.output_dir, f"{model_name}_{run_id}_results.csv")
        results_df.to_csv(file_path, index=False)
        return {"type": "csv", "file_path": self._convert_path_to_url(file_path), "rows": len(results_df), "description": "Résultats détaillés exportés en CSV"}

    def export_figure_as_png(self, y_test, y_pred, model_name, run_id):
        y_true = _to_1d(y_test)
        y_hat = _to_1d(y_pred)
        residuals = y_true - y_hat
        errors = np.abs(residuals)

        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        axes[0, 0].scatter(y_true, y_hat, alpha=0.5)
        min_val = min(y_true.min(), y_hat.min())
        max_val = max(y_true.max(), y_hat.max())
        axes[0, 0].plot([min_val, max_val], [min_val, max_val], "r--")
        axes[0, 0].set_title("Prédictions vs Réel")

        axes[0, 1].scatter(y_hat, residuals, alpha=0.5)
        axes[0, 1].axhline(y=0, color="r", linestyle="--")
        axes[0, 1].set_title("Analyse des Résidus")

        axes[1, 0].hist(errors, bins=30)
        axes[1, 0].set_title("Distribution des Erreurs")

        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title("Q-Q Plot")

        plt.tight_layout()
        file_path = os.path.join(self.output_dir, f"{model_name}_{run_id}_analysis.png")
        fig.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close(fig)

        return {"type": "png", "file_path": self._convert_path_to_url(file_path), "description": "Analyse graphique complète en PNG"}

    def plot_models_comparison(self, runs):
        """Crée un graphique comparatif de tous les modèles par R² score"""
        if not runs:
            return None
        
        model_data = {}
        for run in runs:
            model_name = run.get("model_name", "Unknown")
            r2 = run.get("metrics", {}).get("r2")
            if r2 is not None:
                if model_name not in model_data:
                    model_data[model_name] = []
                model_data[model_name].append(r2)
        
        if not model_data:
            return None
        
        fig = go.Figure()
        for model_name, r2_scores in model_data.items():
            fig.add_trace(go.Box(
                y=r2_scores,
                name=model_name,
                boxmean='sd'
            ))
        
        fig.update_layout(
            title="Comparaison des modèles - R² Score",
            yaxis_title="R² Score",
            xaxis_title="Modèle",
            width=900, height=600,
            showlegend=True
        )
        
        file_path = os.path.join(self.output_dir, "models_comparison.html")
        fig.write_html(file_path)
        return {"type": "box", "file_path": self._convert_path_to_url(file_path), "description": "Comparaison des modèles par R² score"}

    def plot_r2_comparison(self, runs):
        """Crée un graphique des scores R² de tous les modèles"""
        if not runs:
            return None
        
        models = []
        r2_scores = []
        rmse_scores = []
        mae_scores = []
        
        for run in runs:
            model_name = run.get("model_name", "Unknown")
            metrics = run.get("metrics", {})
            r2 = metrics.get("r2")
            rmse = metrics.get("rmse")
            mae = metrics.get("mae")
            
            if r2 is not None:
                models.append(f"{model_name} ({run.get('run_id', '')[:8]})")
                r2_scores.append(r2 if r2 is not None else 0)
                rmse_scores.append(rmse if rmse is not None else 0)
                mae_scores.append(mae if mae is not None else 0)
        
        if not models:
            return None
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=models,
            y=r2_scores,
            name="R² Score",
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title="Scores R² par exécution",
            xaxis_title="Modèle",
            yaxis_title="R² Score",
            barmode='group',
            width=900, height=600,
            hovermode='x unified'
        )
        
        file_path = os.path.join(self.output_dir, "r2_comparison.html")
        fig.write_html(file_path)
        return {"type": "bar", "file_path": self._convert_path_to_url(file_path), "description": "Comparaison des scores R²"}

    def plot_feature_importances(self, feature_importances, model_name, run_id):
        """Crée un graphique des importances des features"""
        if not feature_importances or not feature_importances.get("features"):
            return None
        
        features = feature_importances.get("features", [])
        importances = feature_importances.get("importances", [])
        
        # Créer un DataFrame et trier
        df = pd.DataFrame({
            "Feature": features,
            "Importance": importances
        }).sort_values("Importance", ascending=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["Importance"],
            y=df["Feature"],
            orientation='h',
            marker=dict(
                color=df["Importance"],
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Importance")
            )
        ))
        
        fig.update_layout(
            title=f"Feature Importances - {model_name}",
            xaxis_title="Importance Score",
            yaxis_title="Features",
            width=900, height=max(400, len(features) * 30),
            margin=dict(l=200)
        )
        
        file_path = os.path.join(self.output_dir, f"{model_name}_{run_id}_feature_importances.html")
        fig.write_html(file_path)
        return {"type": "feature_importance", "file_path": self._convert_path_to_url(file_path), "description": "Importance des features"}