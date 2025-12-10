# train_models.py
# Clean, stable, improved ML training pipeline for Cloudburst Project

import os
from pathlib import Path
import joblib
import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_squared_error, r2_score, accuracy_score
)

import lightgbm as lgb

# ----------------------------------------------------
# Paths
# ----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

TRAIN_CSV = DATA_DIR / "training_data.csv"

# ----------------------------------------------------
# Columns that MUST NOT BE USED as features
# ----------------------------------------------------
NON_FEATURE_COLUMNS = {
    "timestamp",
    "node_id",
    "lat",
    "lon",
    "stage",
    "risk_score",
}

# ----------------------------------------------------
# Load training data
# ----------------------------------------------------
def load_data():
    df = pd.read_csv(TRAIN_CSV)
    print("[INFO] Loaded training:", df.shape)
    return df


# ----------------------------------------------------
# Feature preparation
# ----------------------------------------------------
def prepare(df):
    feature_cols = [c for c in df.columns if c not in NON_FEATURE_COLUMNS]

    # Extract X and y
    X_raw = df[feature_cols].copy()
    y_risk = df["risk_score"].astype(float).values
    y_stage = df["stage"].astype(int).values

    # Imputer
    imputer = SimpleImputer(strategy="median")
    X_imp = imputer.fit_transform(X_raw)
    X_imp = pd.DataFrame(X_imp, columns=feature_cols)

    # Optional: Scaling improves LightGBM stability across features
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X_imp)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_cols)

    return X_scaled, imputer, scaler, feature_cols, y_risk, y_stage


# ----------------------------------------------------
# Train LightGBM Regressor
# ----------------------------------------------------
def train_regressor(X, y, path, name="stage"):
    params = {
        "n_estimators": 500,
        "learning_rate": 0.04,
        "num_leaves": 40,
        "min_child_samples": 30,
        "max_depth": -1,
        "random_state": 42,
        "n_jobs": -1,
    }

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = lgb.LGBMRegressor(**params)

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        eval_metric="rmse",
        callbacks=[lgb.early_stopping(50, verbose=False)],
    )

    pred = model.predict(X_val)
    rmse = mean_squared_error(y_val, pred) ** 0.5
    r2 = r2_score(y_val, pred)

    print(f"[{name}]  RMSE={rmse:.4f}  | R2={r2:.4f}")

    joblib.dump(model, path)
    return model


# ----------------------------------------------------
# Train Stage Classifier (Multiclass)
# ----------------------------------------------------
def train_classifier(X, y_stage, path):
    X_train, X_val, y_train, y_val = train_test_split(
        X, y_stage, test_size=0.2, random_state=42, stratify=y_stage
    )

    classes = sorted(np.unique(y_stage))
    cmap = {c: i for c, i in zip(classes, range(len(classes)))}

    y_train_m = np.array([cmap[v] for v in y_train])
    y_val_m = np.array([cmap[v] for v in y_val])

    params = {
        "n_estimators": 500,
        "learning_rate": 0.05,
        "num_leaves": 40,
        "objective": "multiclass",
        "num_class": len(classes),
        "class_weight": "balanced",
        "n_jobs": -1,
        "random_state": 42,
    }

    model = lgb.LGBMClassifier(**params)

    model.fit(
        X_train,
        y_train_m,
        eval_set=[(X_val, y_val_m)],
        eval_metric="multi_logloss",
        callbacks=[lgb.early_stopping(50, verbose=False)],
    )

    pred = model.predict(X_val)
    acc = accuracy_score(y_val_m, pred)

    print(f"[classifier] Accuracy = {acc:.4f}")

    joblib.dump({"model": model, "class_map": cmap}, path)
    return model, cmap


# ----------------------------------------------------
# MAIN TRAINING PIPELINE
# ----------------------------------------------------
def main():
    df = load_data()

    # Prepare features
    X_df, imputer, scaler, feat_cols, y_risk, y_stage = prepare(df)

    # Train 3 separate regressors — one for each stage
    for st in [1, 2, 3]:
        sub = df[df["stage"] == st]
        if len(sub) < 100:
            print(f"[WARN] Stage {st} has too few samples, skipping.")
            continue

        X_sub = X_df.loc[sub.index]
        y_sub = y_risk[sub.index]

        train_regressor(
            X_sub,
            y_sub,
            MODELS_DIR / f"stage{st}_model.pkl",
            name=f"stage{st}",
        )

    # Train classifier for stage detection
    train_classifier(X_df, y_stage, MODELS_DIR / "stage_classifier.pkl")

    # Save preprocessing bundle
    joblib.dump(
        {"imputer": imputer, "scaler": scaler, "feature_cols": feat_cols},
        MODELS_DIR / "preprocessing.joblib",
    )

    print("\n[DONE] All models saved to:", MODELS_DIR, "\n")


if __name__ == "__main__":
    main()
