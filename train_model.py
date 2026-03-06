"""
train_model.py — Train the Random Forest flood prediction model.

Run once before starting the backend:
    python train_model.py
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_PATH   = os.path.join(BASE_DIR, "data", "flood_dataset.csv")
MODELS_DIR  = os.path.join(BASE_DIR, "models")
MODEL_PATH  = os.path.join(MODELS_DIR, "flood_model.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")

os.makedirs(MODELS_DIR, exist_ok=True)

def generate_dataset_if_missing():
    """Generate synthetic dataset if the CSV doesn't exist yet."""
    if not os.path.exists(DATA_PATH):
        print("[!] Dataset not found — generating synthetic data...")
        sys.path.insert(0, os.path.join(BASE_DIR, "data"))
        import generate_dataset  # noqa: F401 — side-effect: creates CSV
        print()

def train():
    generate_dataset_if_missing()

    print("[1/6] Loading dataset ...")
    df = pd.read_csv(DATA_PATH)
    print(f"      Rows: {len(df):,}  |  Flood events: {df['flood_occurred'].sum():,}  "
          f"({df['flood_occurred'].mean()*100:.1f}%)")

    FEATURES = ["rainfall_mm", "river_level_m", "humidity_pct",
                "temperature_c", "wind_speed_kmh"]
    TARGET   = "flood_occurred"

    X = df[FEATURES].values
    y = df[TARGET].values

    print("[2/6] Splitting into train / test (80 / 20) ...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("[3/6] Scaling features ...")
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc  = scaler.transform(X_test)

    print("[4/6] Training Random Forest Classifier ...")
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        n_jobs=-1,
        random_state=42,
    )
    clf.fit(X_train_sc, y_train)

    print("[5/6] Evaluating ...")
    y_pred   = clf.predict(X_test_sc)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\n{'='*55}")
    print(f"  Accuracy : {accuracy*100:.2f}%")
    print(f"{'='*55}")
    print(classification_report(y_test, y_pred,
                                target_names=["No Flood", "Flood"]))
    print("Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"  TN={cm[0,0]}  FP={cm[0,1]}")
    print(f"  FN={cm[1,0]}  TP={cm[1,1]}")

    # Feature importances
    print("\nFeature Importances:")
    for feat, imp in sorted(
        zip(FEATURES, clf.feature_importances_), key=lambda x: -x[1]
    ):
        bar = "█" * int(imp * 40)
        print(f"  {feat:<20} {imp:.4f}  {bar}")

    print("\n[6/6] Saving model and scaler ...")
    joblib.dump(clf,    MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"  [✓] Model  → {MODEL_PATH}")
    print(f"  [✓] Scaler → {SCALER_PATH}")
    print("\n[✓] Training complete — ready to start backend.\n")

if __name__ == "__main__":
    train()
