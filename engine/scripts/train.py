import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
# pyrefly: ignore [missing-import]
import shap
import joblib
import pandas as pd

FEATURES = [
    "months_active", "bill_payment_ratio", "qr_transaction_consistency",
    "airtime_topup_frequency", "psychometric_score", "network_trust_score",
    "avg_transaction_value", "transaction_volatility",
    "days_since_last_transaction", "community_fraud_flag"
]

def train_model(df: pd.read_csv):

    

    X = df[FEATURES]
    y = df["risk_band"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42
    )
    model.fit(X_train, y_train,
              eval_set=[(X_test, y_test)],
              early_stopping_rounds=20,
              verbose=False)

    print(classification_report(y_test, model.predict(X_test),
          target_names=["Refused","Silver","Gold","Platinum"]))

    # SHAP explainability — huge judge points
    explainer = shap.TreeExplainer(model)

    joblib.dump(model, "models/trustlayer_xgb.pkl")
    joblib.dump(explainer, "models/shap_explainer.pkl")
    return model, explainer


def predict_risk(merchant_features: dict) -> dict:
    model = joblib.load("models/trustlayer_xgb.pkl")
    explainer = joblib.load("models/shap_explainer.pkl")

    df = pd.DataFrame([merchant_features])[FEATURES]
    pred_class = int(model.predict(df)[0])
    pred_proba = model.predict_proba(df)[0]

    shap_values = explainer.shap_values(df)
    # Top 2 features driving this prediction
    top_factors = sorted(
        zip(FEATURES, shap_values[pred_class][0]),
        key=lambda x: abs(x[1]),
        reverse=True
    )[:2]

    bands = ["Refused", "Silver", "Gold", "Platinum"]
    return {
        "ml_band": bands[pred_class],
        "ml_confidence": round(float(max(pred_proba)), 3),
        "top_shap_factors": [
            {"feature": f, "impact": round(v, 4)} for f, v in top_factors
        ]
    }

train_model("data/synthetic_merchants.csv")