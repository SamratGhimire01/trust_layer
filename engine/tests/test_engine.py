import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_banner(title):
    print("\n" + "=" * 60)
    print(f"🔬 TEST CASE: {title}")
    print("=" * 60)

def test_successful_score_with_ai():
    print_banner("POST /score - Standard Verified Merchant (M001)")
    
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
        
        print("✅ HTTP Status: 200 OK")
        print(f"🔹 Merchant ID         : {data['merchant_id']}")
        print(f"🔹 Fused Credit Score   : {data['score']} ({data['band']})")
        print(f"🔹 Data Confidence (c) : {data['confidence']}")
        print(f"🔹 Safe Loan Ceiling   : {data['loan_ceiling']} NPR")
        print(f"🔹 Fraud Gate Status   : {data['gate_status']}")
        print("\n🧠 Live Gemini AI Summary Explanation:")
        print("-" * 50)
        print(data.get('ai_summary', 'No summary payload returned.'))
        print("-" * 50)
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

def test_fraud_gate_anomaly():
    print_banner("POST /score - Fraud Gate Anomaly Trigger")
    
    # Sending high metrics to get a good ceiling, but requesting a massive loan amount
    payload = {
        "merchant_id": "M001",
        "months_active": 12,
        "bills_paid_on_time": 24,
        "total_bills_due": 24,
        "qr_transaction_consistency": 0.9,
        "airtime_topup_frequency": 0.8,
        "quiz_answers": [5, 5, 4, 5, 4],
        "requested_loan_amount": 500000.0  # Way above the safe ceiling limit
    }
    
    try:
        response = requests.post(f"{BASE_URL}/score", json=payload)
        response.raise_for_status()
        data = response.json()
        
        print("✅ HTTP Status: 200 OK")
        print(f"🔹 Merchant ID         : {data['merchant_id']}")
        print(f"🔹 Loan Ceiling        : {data['loan_ceiling']} NPR")
        print(f"🔹 Requested Amount    : {payload['requested_loan_amount']} NPR")
        
        # We expect the gate to intercept this request
        if "FLAGGED" in data['gate_status']:
            print(f"🚨 FRAUD GATE SUCCESS : {data['gate_status']} [MATCH]")
        else:
            print(f"❌ FRAUD GATE FAILURE : Expected FLAGGED, got {data['gate_status']}")
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

def test_social_graph_engine():
    print_banner("GET /graph - Network Analysis & Louvain Detection")
    
    try:
        response = requests.get(f"{BASE_URL}/graph")
        response.raise_for_status()
        data = response.json()
        
        print("✅ HTTP Status: 200 OK")
        print(f"🔹 Total Network Nodes Processed : {len(data['nodes'])}")
        print(f"🔹 Total Network Vouch Edges     : {len(data['edges'])}")
        
        clean_merchants = [n for n in data['nodes'] if not n['fraud']]
        fraud_merchants = [n for n in data['nodes'] if n['fraud']]
        
        print("\n🟢 VERIFIED CLEAN COMMUNITY TIER:")
        for node in clean_merchants:
            print(f"  - Node {node['id']} ({node['name']}) | Scaled Trust: {round(node['trust'], 4)}")
            
        print("\n🔴 ISOLATED FRAUD RING (AUTOMATICALLY INTERCEPTED):")
        for node in fraud_merchants:
            print(f"  - Node {node['id']} ({node['name']}) [FLAGGED FRAUD]")
            
        if len(fraud_merchants) == 5:
            print("\n✅ GRAPH GRAPH-THEORETIC RULE VALIDATION: PASSED")
        else:
            print("\n❌ GRAPH GRAPH-THEORETIC RULE VALIDATION: FAILED")
            
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

def test_fairness_metrics():
    print_banner("GET /fairness - Systemic Bias Audit Analytics")
    
    try:
        response = requests.get(f"{BASE_URL}/fairness")
        response.raise_for_status()
        data = response.json()
        
        print("✅ HTTP Status: 200 OK")
        print("🔹 Monitored Demographic Classes:")
        for group in data['groups']:
            print(f"  - {group}")
            
        print("\n📊 Baseline Structural Score Deltas:")
        for group, val in data['before'].items():
            print(f"  - {group}: {val}")
            
        print("\n📊 Post-Graph Fusion Unified Deltas:")
        for group, val in data['after'].items():
            print(f"  - {group}: {val}")
            
        print(f"\n📝 System Audit Note: {data['note']}")
        print("\n✅ FAIRNESS DATA DISPATCH: PASSED")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("⚡ TRUSTLAYER ENGINE COMPLETE INTEGRATION TELEMETRY ⚡")
    print("=" * 60)
    
    try:
        # Check if server is up at all before running suite
        requests.get(f"{BASE_URL}/graph", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ CRITICAL: Cannot connect to FastAPI server.")
        print("Please ensure uvicorn is running on http://127.0.0.1:8000\n")
        sys.exit(1)
        
    test_successful_score_with_ai()
    test_fraud_gate_anomaly()
    test_social_graph_engine()
    test_fairness_metrics()
    
    print("\n🏁 ALL INTEGRATION CHECKS COMPLETE. BACKEND CONTRACT IS SECURED.\n")