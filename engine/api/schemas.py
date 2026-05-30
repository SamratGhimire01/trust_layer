from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# ==========================================
# /score ENDPOINT SCHEMAS
# ==========================================

class ExplanationItem(BaseModel):
    factor: str = Field(..., description="The evaluated factor")
    impact: str = Field(..., description="'+' or '-' impact")

class ScoreRequest(BaseModel):
    merchant_id: str
    months_active: int = Field(..., ge=0)
    bills_paid_on_time: int = Field(..., ge=0)
    total_bills_due: int = Field(..., ge=0)
    qr_transaction_consistency: float = Field(..., ge=0.0, le=1.0)
    airtime_topup_frequency: float = Field(..., ge=0.0, le=1.0)
    quiz_answers: Optional[List[int]] = None

class ScoreResponse(BaseModel):
    merchant_id: str
    score: int
    band: str
    confidence: float
    loan_ceiling: float
    gate_status: str
    explanations: List[ExplanationItem]
    ai_summary: Optional[str] = None

# ==========================================
# /graph ENDPOINT SCHEMAS
# ==========================================

class GraphNode(BaseModel):
    id: str
    name: str
    trust: float
    score: int
    fraud: bool

class GraphEdge(BaseModel):
    source: str
    target: str
    weight: float

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# ==========================================
# /fairness ENDPOINT SCHEMAS
# ==========================================

class FairnessResponse(BaseModel):
    groups: List[str]
    before_disparity: Dict[str, float]
    after_disparity: Dict[str, float]
    note: str
    
    
# (Keep your existing imports and code at the top...)

class ScoreRequest(BaseModel):
    merchant_id: str
    months_active: int
    bills_paid_on_time: int
    total_bills_due: int
    qr_transaction_consistency: float
    airtime_topup_frequency: float
    quiz_answers: List[int] | None = None
    requested_loan_amount: float | None = None # <-- ADDED FOR FRAUD GATE

# ... (Keep your existing Response models) ...

# ADD THIS TO THE VERY BOTTOM:
class FairnessResponse(BaseModel):
    groups: List[str]
    before: Dict[str, float]
    after: Dict[str, float]
    note: str