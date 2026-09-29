"""
Clustering Agent (unsupervised mode).
Used when no target column is chosen. Runs real KMeans for several values of k,
selects k by silhouette score, and returns cluster sizes, human-readable cluster
profiles and a 2-D PCA projection for plotting. Nothing here is invented --
every number comes from the fitted model.
"""
import os
import uuid
import numpy as np
import pandas as pd
import joblib
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.agents.base_agent import BaseAgent
from app.config import settings
from app.utils.helpers import clean_float

MAX_K = 8
MIN_ROWS = 20
SILHOUETTE_SAMPLE = 2000
PCA_POINTS = 600


class ClusteringAgent(BaseAgent):
    name = "clustering_agent"

    def run(self, df: pd.DataFrame, numeric_cols: list[str], categorical_cols: list[str],
            analysis_id: int) -> dict:
        features = numeric_cols + categorical_cols
        if len(df) < MIN_ROWS or len(features) < 2:
            return {
                "available": False,
                "reason": "Clustering needs at least 20 rows and 2 usable feature columns "
                          f"(found {len(df)} rows, {len(features)} features).",
            }

        X = df[features]
        preprocessor = ColumnTransformer(transformers=[
            ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")),
                                  ("scaler", StandardScaler())]), numeric_cols),
            ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                                      ("encoder", OneHotEncoder(handle_unknown="ignore"))]), categorical_cols),
        ])
        Xt = preprocessor.fit_transform(X)
        if hasattr(Xt, "toarray"):
            Xt = Xt.toarray()
        Xt = np.asarray(Xt, dtype=float)

        max_k = min(MAX_K, max(2, len(df) // 10))
        k_scores, fitted = [], {}
        for k in range(2, max_k + 1):
            model = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = model.fit_predict(Xt)
            if len(set(labels)) < 2:
                continue
            sample = min(SILHOUETTE_SAMPLE, len(Xt))
            score = silhouette_score(Xt, labels, sample_size=sample, random_state=42)
            k_scores.append({"k": k, "silhouette": clean_float(score), "inertia": clean_float(model.inertia_)})
            fitted[k] = (model, labels, score)

        if not fitted:
            return {"available": False, "reason": "KMeans could not find distinct clusters in this data."}

        best_k = max(fitted, key=lambda k: fitted[k][2])
        model, labels, best_score = fitted[best_k]

        work = df[features].copy()
        work["_cluster"] = labels
        sizes = work["_cluster"].value_counts().sort_index()
        clusters = []
        for cid, size in sizes.items():
            part = work[work["_cluster"] == cid]
            numeric_profile = {c: clean_float(part[c].mean()) for c in numeric_cols}
            categorical_profile = {}
            for c in categorical_cols:
                vc = part[c].value_counts(dropna=True)
                if not vc.empty:
                    categorical_profile[c] = {"top_value": str(vc.index[0]),
                                              "share": clean_float(vc.iloc[0] / vc.sum())}
            clusters.append({
                "cluster": int(cid), "size": int(size),
                "share": clean_float(size / len(work)),
                "numeric_means": numeric_profile,
                "categorical_top": categorical_profile,
            })

        # Which numeric features separate the clusters most (spread of cluster means, in std units)
        distinguishing = []
        for c in numeric_cols:
            overall_std = df[c].std()
            if overall_std and not np.isnan(overall_std):
                means = [cl["numeric_means"][c] for cl in clusters if cl["numeric_means"][c] is not None]
                if len(means) >= 2:
                    distinguishing.append({"feature": c,
                                           "separation": clean_float((max(means) - min(means)) / overall_std)})
        distinguishing = sorted([d for d in distinguishing if d["separation"] is not None],
                                key=lambda d: -d["separation"])[:5]

        # 2-D projection for plotting
        n_points = min(PCA_POINTS, len(Xt))
        idx = np.random.default_rng(42).choice(len(Xt), size=n_points, replace=False)
        pca = PCA(n_components=2, random_state=42)
        coords = pca.fit_transform(Xt)
        points = [{"x": clean_float(coords[i, 0]), "y": clean_float(coords[i, 1]), "cluster": int(labels[i])}
                  for i in idx]

        os.makedirs(settings.MODELS_DIR, exist_ok=True)
        model_path = os.path.join(settings.MODELS_DIR, f"analysis_{analysis_id}_kmeans_{uuid.uuid4().hex}.joblib")
        joblib.dump({"preprocessor": preprocessor, "model": model, "features": features}, model_path)

        return {
            "available": True,
            "algorithm": "KMeans",
            "best_k": int(best_k),
            "silhouette": clean_float(best_score),
            "k_scores": k_scores,
            "features_used": features,
            "clusters": clusters,
            "distinguishing_features": distinguishing,
            "pca_points": points,
            "pca_explained_variance": [clean_float(v) for v in pca.explained_variance_ratio_],
            "model_path": model_path,
            "interpretation": (
                "Silhouette ranges from -1 to 1. Above ~0.5 suggests well-separated groups, "
                "0.25-0.5 weak but usable structure, below 0.25 little real cluster structure."
            ),
        }
