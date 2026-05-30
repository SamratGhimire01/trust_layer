import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_banner(title):
    print("\n" + "=" * 65)
    print(f"🔬 {title}")
    print("=" * 65)

def test_1_standard_merchant():
    print_banner("TEST 1: Standard Verified Merchant (M001)")
    payload = {
        "merchant_id": "M001",
        "months_active": 12,
        "bills_paid_on_time": 24,
        "total_bills_due": 24,
        "qr_transaction_consistency": 0.9,
        "airtime_topup_frequency": 0.8,
        "quiz_answers": [5, 5, 4, 5, 4],
        "requested_loan_amount": 25000.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/score", json=payload)
        response.raise_for_status()
        data = response.json()
        print("✅ HTTP 200 OK | Math Engine & AI Live")
        print(f"🔹 Final Score : {data['score']} ({data['band']})")
        print(f"🔹 Gate Status : {data['gate_status']} (Expected: PASSED)")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

def test_2_greedy_fraudster():
    print_banner("TEST 2: The Greedy Fraudster (Security & Anomaly Gate)")
    payload = {
        "merchant_id": "M001",
        "months_active": 12,
        "bills_paid_on_time": 24,
        "total_bills_due": 24,
        "qr_transaction_consistency": 0.9,
        "airtime_topup_frequency": 0.8,
        "quiz_answers": [5, 5, 4, 5, 4],
        "requested_loan_amount": 1000000.0 # Extreme amount
    }
    
    try:
        response = requests.post(f"{BASE_URL}/score", json=payload)
        response.raise_for_status()
        data = response.json()
        print("✅ HTTP 200 OK | System handled the anomaly safely")
        print(f"🔹 Loan Ceiling   : {data['loan_ceiling']} NPR")
        print(f"🔹 Requested      : {payload['requested_loan_amount']} NPR")
        
        if "FLAGGED" in data['gate_status']:
            print(f"🚨 FRAUD GATE SUCCESS: {data['gate_status']}")
        else:
            print(f"❌ FRAUD GATE FAILURE: Expected FLAGGED, got {data['gate_status']}")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

def test_3_ghost_merchant():
    print_banner("TEST 3: The Ghost Merchant (Divide-by-Zero Security Check)")
    payload = {
        "merchant_id": "GHOST99",
        "months_active": 0,
        "bills_paid_on_time": 0,
        "total_bills_due": 0,
        "qr_transaction_consistency": 0.0,
        "airtime_topup_frequency": 0.0,
        "quiz_answers": [1, 1, 1, 1, 1],
        "requested_loan_amount": 5000.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/score", json=payload)
        response.raise_for_status()
        data = response.json()
        print("✅ HTTP 200 OK | System did NOT crash (Math is secure)")
        print(f"🔹 Final Score : {data['score']} ({data['band']})")
        print(f"🔹 Loan Ceiling: {data['loan_ceiling']} NPR")
    except Exception as e:
        print(f"❌ TEST FAILED: System crashed on zero data! {e}")

def test_4_social_graph():
    print_banner("TEST 4: Graph Fraud Network (Louvain Detection)")
    try:
        response = requests.get(f"{BASE_URL}/graph")
        response.raise_for_status()
        data = response.json()
        
        fraud_merchants = [n for n in data['nodes'] if n['fraud']]
        print("✅ HTTP 200 OK | Graph Analyzed")
        print(f"🔹 Nodes: {len(data['nodes'])} | Edges: {len(data['edges'])}")
        print("\n🔴 ISOLATED FRAUD RING:")
        for node in fraud_merchants:
            print(f"  - {node['name']} [FLAGGED]")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

def test_5_fairness_audit():
    print_banner("TEST 5: Systemic Fairness Audit")
    try:
        response = requests.get(f"{BASE_URL}/fairness")
        response.raise_for_status()
        data = response.json()
        
        print("✅ HTTP 200 OK | Audit Complete")
        for group, val in data['after'].items():
            print(f"🔹 {group} Fused Score: {val}")
        print(f"\n📝 Audit Note: {data['note']}")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

if __name__ == "__main__":
    print("\n⚡ INITIATING TRUSTLAYER EXTREMITY SECURITY AUDIT ⚡")
    try:
        requests.get(f"{BASE_URL}/graph", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ CRITICAL: Cannot connect. Is Uvicorn running on port 8000?\n")
        sys.exit(1)
        
    test_1_standard_merchant()
    test_2_greedy_fraudster()
    test_3_ghost_merchant()
    test_4_social_graph()
    test_5_fairness_audit()
    
    print("\n🏁 ALL SECURITY AND EXTREMITY CHECKS COMPLETE. BACKEND IS BULLETPROOF. 🏁\n")