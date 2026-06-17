import json
from pathlib import Path
import traceback
from fastapi import APIRouter, HTTPException

from api.schemas import ScoreRequest, ScoreResponse, ExplanationItem, GraphResponse, FairnessResponse
from src.scoring import run_scoring_engine
from src.graph import process_social_graph
from src.fairness import compute_fairness_metrics
from src.llm_agent import financial_agent
from src.ml_model import predict_risk


router = APIRouter(prefix="/api/v1", tags=["TrustLayer Core"])

# ==========================================
# DAY 1 & 3: FUSION ENGINE & FRAUD GATE
# ==========================================
@router.post("/score", response_model=ScoreResponse)
async def calculate_merchant_score(payload: ScoreRequest):
    try:
        # 1. Get Base Personal Score
        answers = payload.quiz_answers if payload.quiz_answers is not None else []
        base_score, band, confidence, loan_ceiling, raw_explanations = run_scoring_engine(
            months_active=payload.months_active,
            bills_paid_on_time=payload.bills_paid_on_time,
            total_bills_due=payload.total_bills_due,
            qr_consistency=payload.qr_transaction_consistency,
            airtime_frequency=payload.airtime_topup_frequency,
            quiz_answers=answers
        )
        
        # 2. Get Graph Trust Score (Day 2 Integration)
        base_dir = Path(__file__).resolve().parent.parent
        data_path = base_dir / "data" / "seed_data.json"
        with open(data_path, "r", encoding="utf-8") as f:
            network_data = json.load(f)
            
        graph_result = process_social_graph(
            merchants=network_data.get("merchants", []),
            vouches=network_data.get("vouches", [])
        )
        
        # Find this merchant in the graph
        trust_score = 0.0
        for node in graph_result["nodes"]:
            if node["id"] == payload.merchant_id:
                trust_score = node["trust"]
                break
                
        # =================================================================
        # LAYER 3: Machine Learning Framework Layer (XGBoost + SHAP Engine)
        # =================================================================
        
        # Build features safely extracting properties from incoming payload schemas
        ml_features = {
            "months_active": payload.months_active,
            "bill_payment_ratio": payload.bills_paid_on_time / max(payload.total_bills_due, 1),
            "qr_transaction_consistency": getattr(payload, 'qr_transaction_consistency', 0.8),
            "airtime_topup_frequency": getattr(payload, 'airtime_topup_frequency', 0.7),
            "psychometric_score": sum(answers) / max(len(answers), 1) if answers else 4.0,
            "network_trust_score": float(trust_score),
            "avg_transaction_value": getattr(payload, 'avg_transaction_value', 15000),
            "transaction_volatility": getattr(payload, 'transaction_volatility', 0.2),
            "days_since_last_transaction": getattr(payload, 'days_since_last_transaction', 3),
            "community_fraud_flag": 1 if any(n.get("id") == payload.merchant_id and n.get("fraud") for n in graph_result.get("nodes", [])) else 0
        }

        # Calculate prediction results + SHAP metrics matrix arrays
        ml_result = predict_risk(ml_features)

        # Map ML classifications into explicit risk scores
        band_to_score = {"Refused": 200, "Silver": 425, "Gold": 625, "Platinum": 825}
        ml_score = band_to_score[ml_result["ml_band"]]

        # 3-WAY FUSION FORMULA: (60% Math Formula + 20% Graph Network + 20% ML Variant)
        scaled_trust = trust_score * 1000
        final_fused_score = int((0.6 * base_score) + (0.2 * scaled_trust) + (0.2 * ml_score))
        
        # Ensure it stays within 0-900 bounds
        final_fused_score = min(max(final_fused_score, 0), 900)

        # 4. FRAUD GATE: Loan Size Anomaly
        gate_status = "PASSED"
        if payload.requested_loan_amount:
            # If they ask for more than 1.5x their safe ceiling, flag it for manual review
            if payload.requested_loan_amount > (loan_ceiling * 1.5):
                gate_status = "FLAGGED: ANOMALOUS_REQUEST"
                
        validated_explanations = [
            ExplanationItem(factor=item["factor"], impact=item["impact"])
            for item in raw_explanations
        ]
        
        # 5. Generate AI Summary (Synchronized to feed Graph Data and ML predictions)
        explanations_summary = ", ".join([f"{item['factor']} ({item['impact']})" for item in raw_explanations])
        
        ai_summary = financial_agent.generate_merchant_advisory(
            score=final_fused_score,
            band=band,
            explanations_summary=explanations_summary,
            months_active=payload.months_active,
            ml_data={
                "ml_band": ml_result["ml_band"],
                "ml_confidence": ml_result["ml_confidence"],
                "top_shap_factors": ml_result["top_shap_factors"]
            },
            graph_data={
                "trust_score": float(trust_score),
                "community_fraud_flag": ml_features["community_fraud_flag"]
            }
        )
        
        # Map output metrics safely back to response models
        return ScoreResponse(
            merchant_id=payload.merchant_id,
            score=final_fused_score,
            band=band,
            confidence=confidence,
            loan_ceiling=loan_ceiling,
            gate_status=gate_status,
            explanations=validated_explanations,
            ai_summary=ai_summary,
            ml_band=ml_result["ml_band"],
            ml_confidence=ml_result["ml_confidence"],
            ml_shap_factors=ml_result["top_shap_factors"]
        )
        
    except Exception as e:
        print("\n=== [DIAGNOSTIC] SCORING ENGINE FAULT ===")
        traceback.print_exc()
        print("=========================================\n")
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred while calculating the merchant score."
        )

# ==========================================
# DAY 2: GRAPH ENGINE
# ==========================================
@router.get("/graph", response_model=GraphResponse)
async def get_social_graph():
    try:
        base_dir = Path(__file__).resolve().parent.parent
        data_path = base_dir / "data" / "seed_data.json"
        
        with open(data_path, "r", encoding="utf-8") as f:
            network_data = json.load(f)
            
        result = process_social_graph(
            merchants=network_data.get("merchants", []),
            vouches=network_data.get("vouches", [])
        )
        return result
        
    except Exception as e:
        print("\n=== [DIAGNOSTIC] GRAPH ENGINE FAULT ===")
        traceback.print_exc()
        print("=======================================\n")
        raise HTTPException(
            status_code=500, 
            detail="An internal error occurred while processing the trust network."
        )

# ==========================================
# DAY 3: FAIRNESS AUDIT API
# ==========================================
@router.get("/fairness", response_model=FairnessResponse)
async def get_fairness_data():
    """Returns the gap analysis data for the frontend Fairness Chart."""
    try:
        return compute_fairness_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Failed to compute fairness metrics."
        )
