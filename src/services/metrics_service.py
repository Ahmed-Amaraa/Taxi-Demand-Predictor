import mlflow
from config import Config


class MetricsService:
    """Service pour récupérer et comparer les métriques"""

    def __init__(self):
        self.config = Config()
        mlflow.set_tracking_uri(self.config.MLFLOW_TRACKING_URI)

    @staticmethod
    def _extract_prefixed(row, prefix: str):
        out = {}
        for k, v in row.items():
            if not isinstance(k, str) or not k.startswith(prefix):
                continue
            key = k[len(prefix):]
            if v is None:
                continue
            try:
                if v != v:  # NaN
                    continue
            except Exception:
                pass
            out[key] = v
        return out

    def _get_experiment(self):
        return mlflow.get_experiment_by_name(self.config.MLFLOW_EXPERIMENT_NAME)

    def get_all_results(self):
        experiment = self._get_experiment()
        if not experiment:
            return {"runs": [], "count": 0}

        runs_df = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
        )
        if runs_df is None or runs_df.empty:
            return {"runs": [], "count": 0}

        results = []
        for _, run in runs_df.iterrows():
            tags = self._extract_prefixed(run, "tags.")
            metrics = self._extract_prefixed(run, "metrics.")
            params = self._extract_prefixed(run, "params.")

            # Convertir les values NaT/NaN en None pour JSON serialization
            run_id = run['run_id'] if 'run_id' in run.index else None
            status = run['status'] if 'status' in run.index else None
            start_time = run['start_time'] if 'start_time' in run.index else None
            end_time = run['end_time'] if 'end_time' in run.index else None
            duration_ms = run['duration_ms'] if 'duration_ms' in run.index else None
            
            # Convert pandas NaT to None
            import pandas as pd
            if pd.isna(start_time):
                start_time = None
            if pd.isna(end_time):
                end_time = None
            if pd.isna(duration_ms):
                duration_ms = None
            if pd.isna(status):
                status = None

            results.append({
                "run_id": run_id,
                "model_name": tags.get("model_type") or tags.get("model_name") or "unknown",
                "status": status,
                "metrics": {
                    "rmse": metrics.get("rmse"),
                    "mae": metrics.get("mae"),
                    "r2": metrics.get("r2"),
                },
                "params": params,
                "start_time": str(start_time) if start_time else None,
                "end_time": str(end_time) if end_time else None,
                "duration_ms": float(duration_ms) if duration_ms and pd.notna(duration_ms) else None,
            })

        return {"runs": results, "count": len(results)}

    def get_results_by_model(self, model_name):
        import pandas as pd
        
        experiment = self._get_experiment()
        if not experiment:
            return {"model_name": model_name, "runs": [], "best_run": None}

        runs_df = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            filter_string=f"tags.model_type = '{model_name}'",
            order_by=["start_time DESC"],
        )
        if runs_df is None or runs_df.empty:
            return {"model_name": model_name, "runs": [], "best_run": None}

        results = []
        for _, run in runs_df.iterrows():
            metrics = self._extract_prefixed(run, "metrics.")
            params = self._extract_prefixed(run, "params.")
            
            # Convertir les values NaT/NaN en None pour JSON serialization
            run_id = run['run_id'] if 'run_id' in run.index else None
            start_time = run['start_time'] if 'start_time' in run.index else None
            end_time = run['end_time'] if 'end_time' in run.index else None
            
            if pd.isna(start_time):
                start_time = None
            if pd.isna(end_time):
                end_time = None
            
            results.append({
                "run_id": run_id,
                "model_name": model_name,
                "metrics": {
                    "rmse": metrics.get("rmse"),
                    "mae": metrics.get("mae"),
                    "r2": metrics.get("r2"),
                },
                "params": params,
                "start_time": str(start_time) if start_time else None,
                "end_time": str(end_time) if end_time else None,
            })

        return {
            "model_name": model_name,
            "runs": results,
            "best_run": self._get_best_run(results),
        }

    def _get_best_run(self, runs):
        if not runs:
            return None

        def score(x):
            r2 = x.get("metrics", {}).get("r2")
            return float("-inf") if r2 is None else r2

        return max(runs, key=score)

    def compare_models(self):
        all_results = self.get_all_results()
        comparison = {}

        for run in all_results["runs"]:
            model_name = run.get("model_name", "unknown")
            if model_name not in comparison:
                comparison[model_name] = run
                continue

            new_r2 = run.get("metrics", {}).get("r2")
            old_r2 = comparison[model_name].get("metrics", {}).get("r2")
            new_r2 = float("-inf") if new_r2 is None else new_r2
            old_r2 = float("-inf") if old_r2 is None else old_r2

            if new_r2 > old_r2:
                comparison[model_name] = run

        return {"comparison": comparison}