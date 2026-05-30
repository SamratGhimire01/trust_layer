import json
from pathlib import Path
import traceback
from fastapi import APIRouter, HTTPException

from api.schemas import ScoreRequest, ScoreResponse, ExplanationItem, GraphResponse, FairnessResponse
from src.scoring import run_scoring_engine
from src.graph import process_social_graph
from src.fairness import generate_fairness_summary, compute_fairness_metrics

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
                
        # 3. FUSE THE SCORES (0.8 Personal + 0.2 Graph)
        # Trust is usually 0.0 to 1.0, scale it to 1000 for the formula
        scaled_trust = trust_score * 1000
        final_fused_score = int((0.8 * base_score) + (0.2 * scaled_trust))
        
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
        
        # 5. Generate AI Summary
        ai_summary = generate_fairness_summary(
            score=final_fused_score, # Use the fused score
            band=band,
            explanations=raw_explanations,
            months_active=payload.months_active
        )
        
        return ScoreResponse(
            merchant_id=payload.merchant_id,
            score=final_fused_score,
            band=band,
            confidence=confidence,
            loan_ceiling=loan_ceiling,
            gate_status=gate_status, # Updated Gate
            explanations=validated_explanations,
            ai_summary=ai_summary
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
    # (Leave your existing get_social_graph code exactly as it is)
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