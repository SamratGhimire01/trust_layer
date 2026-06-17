import math
from typing import List, Dict, Tuple

def calculate_confidence(months_active: int) -> float:
    """
    Calculates the data-confidence coefficient 'c'.
    Formula: c = min(months / 12, 0.85)
    """
    # SECURITY: Ensure months cannot be negative
    safe_months = max(0, months_active)
    return min(safe_months / 12.0, 0.85)

def calculate_behavior_estimate(bills_paid_on_time: int, total_bills_due: int, 
                                qr_consistency: float, airtime_frequency: float) -> float:
    """
    Computes behavior estimate (B) as a weighted average.
    - Bill repayment (40%)
    - QR consistency (40%)
    - Airtime frequency (20%)
    """
    # SECURITY: Prevent DivisionByZero exception
    if total_bills_due > 0:
        bill_ratio = bills_paid_on_time / total_bills_due
    else:
        bill_ratio = 0.5  # Neutral fallback if no bills ever due
        
    # Clamp inputs just in case Pydantic misses something
    bill_ratio = max(0.0, min(bill_ratio, 1.0))
    safe_qr = max(0.0, min(qr_consistency, 1.0))
    safe_airtime = max(0.0, min(airtime_frequency, 1.0))
    
    b_score = (0.4 * bill_ratio) + (0.4 * safe_qr) + (0.2 * safe_airtime)
    return b_score

def compute_psychometric_floor(quiz_answers: List[int]) -> float:
    """
    Processes the localized situational quiz.
    Formula: (0.35 + 0.15 * psychometric_percentage)
    """
    if not quiz_answers or len(quiz_answers) == 0:
        return 0.5  # Neutral fallback if quiz skipped
    
    # Clamp answers between 1 and 5
    total_score = sum(max(1, min(score, 5)) for score in quiz_answers)
    max_possible = len(quiz_answers) * 5
    percentage = total_score / max_possible
    
    return 0.35 + (0.15 * percentage)

def run_scoring_engine(
    months_active: int,
    bills_paid_on_time: int,
    total_bills_due: int,
    qr_consistency: float,
    airtime_frequency: float,
    quiz_answers: List[int]
) -> Tuple[int, str, float, float, List[Dict[str, str]]]:
    """
    Executes the master formula:
    Personal = c * Behavior + (1 - c) * floor_nudged_by_quiz
    Returns: (Score, Band, Confidence, Loan_Ceiling, Explanations)
    """
    c = calculate_confidence(months_active)
    b = calculate_behavior_estimate(bills_paid_on_time, total_bills_due, qr_consistency, airtime_frequency)
    p_floor = compute_psychometric_floor(quiz_answers)
    
    personal_score_raw = (c * b) + ((1.0 - c) * p_floor)
    
    # Scale to 1000 and clamp securely
    final_score = int(personal_score_raw * 1000)
    final_score = max(0, min(final_score, 1000))
    
    if final_score >= 750:
        band = "Platinum"
    elif final_score >= 500:
        band = "Gold"
    elif final_score >= 350:
        band = "Silver"
    else:
        band = "Refused"
        
    # Day 1 Proxy: cashflow derived from QR and Bill volume
    estimated_monthly_cashflow = (qr_consistency * 80000) + (bills_paid_on_time * 500)
    loan_ceiling = estimated_monthly_cashflow * 0.75
    
    # Limit risk exposure if confidence is low
    if c < 0.4:
        loan_ceiling *= 0.5
        
    explanations = []
    
    bill_ratio = (bills_paid_on_time / total_bills_due) if total_bills_due > 0 else 0.5
    explanations.append({
        "factor": "Bill Repayment History",
        "impact": "+" if bill_ratio >= 0.75 else "-"
    })
    explanations.append({
        "factor": "Digital QR Transaction Volume",
        "impact": "+" if qr_consistency >= 0.6 else "-"
    })
    explanations.append({
        "factor": "Psychometric Reliability Quiz",
        "impact": "+" if p_floor >= 0.45 else "-"
    })
    
    return final_score, band, c, round(loan_ceiling, 2), explanations