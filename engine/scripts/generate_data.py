import numpy as np
import pandas as pd

np.random.seed(42)

def generate_merchants(n, profile):
    
    if profile == "platinum":
        return {
            "months_active": np.random.randint(6, 60, n),        # overlap with gold
            "bill_payment_ratio": np.random.uniform(0.65, 1.0, n), # overlap with gold
            "qr_transaction_consistency": np.random.uniform(0.60, 1.0, n),
            "airtime_topup_frequency": np.random.uniform(0.50, 1.0, n),
            "psychometric_score": np.random.uniform(3.0, 5.0, n), # overlap
            "network_trust_score": np.random.uniform(0.40, 1.0, n),
            "avg_transaction_value": np.random.randint(3000, 50000, n),  # heavy overlap
            "transaction_volatility": np.random.uniform(0.0, 0.50, n),  # overlap
            "days_since_last_transaction": np.random.randint(0, 20, n),
            "community_fraud_flag": np.random.choice([0,1], n, p=[0.92, 0.08]),
            "risk_band": np.full(n, 3)
        }

    elif profile == "gold":
        return {
            "months_active": np.random.randint(4, 40, n),
            "bill_payment_ratio": np.random.uniform(0.45, 0.92, n), # overlaps both sides
            "qr_transaction_consistency": np.random.uniform(0.40, 0.88, n),
            "airtime_topup_frequency": np.random.uniform(0.35, 0.80, n),
            "psychometric_score": np.random.uniform(2.5, 4.5, n),
            "network_trust_score": np.random.uniform(0.30, 0.80, n),
            "avg_transaction_value": np.random.randint(2000, 30000, n), # overlaps all
            "transaction_volatility": np.random.uniform(0.10, 0.65, n),
            "days_since_last_transaction": np.random.randint(1, 25, n),
            "community_fraud_flag": np.random.choice([0,1], n, p=[0.88, 0.12]),
            "risk_band": np.full(n, 2)
        }

    elif profile == "silver":
        return {
            "months_active": np.random.randint(2, 25, n),
            "bill_payment_ratio": np.random.uniform(0.25, 0.75, n), # overlaps refused+gold
            "qr_transaction_consistency": np.random.uniform(0.20, 0.70, n),
            "airtime_topup_frequency": np.random.uniform(0.15, 0.65, n),
            "psychometric_score": np.random.uniform(1.5, 3.8, n),
            "network_trust_score": np.random.uniform(0.15, 0.65, n),
            "avg_transaction_value": np.random.randint(500, 20000, n), # overlaps all
            "transaction_volatility": np.random.uniform(0.25, 0.85, n),
            "days_since_last_transaction": np.random.randint(3, 45, n),
            "community_fraud_flag": np.random.choice([0,1], n, p=[0.80, 0.20]),
            "risk_band": np.full(n, 1)
        }

    elif profile == "refused":
        return {
            "months_active": np.random.randint(0, 15, n),         # overlap with silver
            "bill_payment_ratio": np.random.uniform(0.0, 0.55, n), # overlap with silver
            "qr_transaction_consistency": np.random.uniform(0.0, 0.50, n),
            "airtime_topup_frequency": np.random.uniform(0.0, 0.45, n),
            "psychometric_score": np.random.uniform(1.0, 3.0, n),
            "network_trust_score": np.random.uniform(0.0, 0.45, n),
            "avg_transaction_value": np.random.randint(100, 15000, n), # overlap with silver
            "transaction_volatility": np.random.uniform(0.40, 1.0, n),
            "days_since_last_transaction": np.random.randint(10, 90, n),
            "community_fraud_flag": np.random.choice([0,1], n, p=[0.45, 0.55]),
            "risk_band": np.full(n, 0)
        }


sizes = {"platinum": 400, "gold": 700, "silver": 600, "refused": 300}
data_segments = [pd.DataFrame(generate_merchants(size, prof)) for prof, size in sizes.items()]
df = pd.concat(data_segments, ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv("scripts/synthetic_merchants.csv", index=False)
print(f"✅ Generated {len(df)} records")

# This script creates a synthetic dataset of merchants with 11 features and a target variable 'risk_band' that categorizes them into four risk levels: refused (0), silver (1), gold (2), and platinum (3). Each profile has overlapping feature distributions to mimic real-world ambiguity in risk assessment. The final dataset is saved as 'synthetic_merchants.csv'.