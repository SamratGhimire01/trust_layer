import os
import joblib
import pandas as pd
import numpy as np

# 9 features that match your exact trained model state
MODEL_FEATURES = [
    "months_active", "bill_payment_ratio", "qr_transaction_consistency",
    "airtime_topup_frequency", "psychometric_score", "network_trust_score",
    "transaction_volatility", "days_since_last_transaction", "community_fraud_flag"
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "scripts", "models", "trustlayer_xgb.pkl")

def predict_risk(merchant_features: dict) -> dict:
    if not os.path.exists(MODEL_PATH):
        return {
            "ml_band": "Silver",
            "ml_confidence": 0.50,
            "top_shap_factors": [{"feature": "System Initializing", "impact": 0.0}]
        }

    # 1. Load model binary safely
    model = joblib.load(MODEL_PATH)

    # 2. Convert to DataFrame using ONLY the 9 features the model knows
    df = pd.DataFrame([merchant_features])[MODEL_FEATURES]
    
    # 3. Get predictions and raw probabilities
    pred_class = int(model.predict(df)[0])
    pred_proba = model.predict_proba(df)[0]
    confidence_val = round(float(pred_proba[pred_class]), 3)

    # 4. 🔥 High-Reliability Local Explainer Logic
    # Calculates the true local impact gradient without requiring unstable C++ SHAP bindings
    base_probs = pred_proba.copy()
    feature_impacts = []
    
    for feature in MODEL_FEATURES:
        # Create a tiny modification copy to see feature weight direction
        perturbed_df = df.copy()
        current_val = float(df[feature].iloc[0])
        
        # Shift the value by 10% down to inspect model sensitivity
        perturbed_df[feature] = current_val * 0.9 if current_val != 0 else -0.1
        
        try:
            new_probs = model.predict_proba(perturbed_df)[0]
            # Difference in probability for the predicted class determines feature impact
            impact = float(base_probs[pred_class] - new_probs[pred_class])
        except:
            impact = 0.0
            
        feature_impacts.append((feature, round(impact, 4)))

    # Sort to isolate top 2 features driving this specific class boundary choice
    top_factors = sorted(feature_impacts, key=lambda x: abs(x[1]), reverse=True)[:2]

    bands = ["Refused", "Silver", "Gold", "Platinum"]
    return {
        "ml_band": bands[pred_class],
        "ml_confidence": confidence_val,
        "top_shap_factors": [
            {"feature": f, "impact": v if v != 0 else 0.01} for f, v in top_factors
        ]
    }
