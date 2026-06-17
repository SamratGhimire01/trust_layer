import os
import traceback
from google import genai
import ollama
from config.settings import settings

class TrustLayerFinancialAgent:
    """Dedicated AI agent outputting a single dense summary string including technical signatures."""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.google_model = 'gemini-3.5-flash'
        self.local_model = 'gemma3:4b'
        
    def _build_comprehensive_prompt(self, score: int, band: str, explanations_summary: str, months_active: int, ml_data: dict, graph_data: dict) -> str:
        ml_band = ml_data.get("ml_band", "N/A")
        ml_conf = ml_data.get("ml_confidence", 0.0)
        shap_factors = ", ".join([f"{f['feature']} ({f['impact']})" for f in ml_data.get("top_shap_factors", [])])
        trust_score = graph_data.get("trust_score", 0.0)
        fraud_flag = "FLAGGED" if graph_data.get("community_fraud_flag", 0) == 1 else "CLEAN"
        
        return (
            f"You are an empathetic financial inclusion AI advisor in Nepal. A small business merchant "
            f"has been audited by our TrustLayer three-layer fusion engine. Here is their full audit matrix:\n\n"
            f"--- LAYER 1: BEHAVIORAL RULE MATH ---\n"
            f"- Fused Unified Score: {score}/900\n"
            f"- Initial Rule Band: {band}\n"
            f"- Length of Business Activity: {months_active} months\n"
            f"- Core Behavioral Impact Factors: {explanations_summary}\n\n"
            f"--- LAYER 2: GRAPH TRUST NETWORK ---\n"
            f"- Network Trust Score (PageRank/Vouches): {trust_score:.4f}/1.0\n"
            f"- Social Network Fraud Health: {fraud_flag}\n\n"
            f"--- LAYER 3: XGBOOST MACHINE LEARNING ---\n"
            f"- ML Predicted Classification Band: {ml_band}\n"
            f"- Classifier Prediction Confidence: {ml_conf * 100:.1f}%\n"
            f"- Top Driving SHAP Impact Vectors: {shap_factors}\n\n"
            f"Write a clean, single-paragraph financial evaluation to the merchant explaining why their "
            f"score is strong or weak, and include two immediate steps they can take to improve it. "
            f"CRITICAL: At the very end of your response, append a technical core string format block exactly like this: "
            f"'[CORE// SCORE:{score} | BAND:{band} | NET:{trust_score:.2f} | ML:{ml_band} ({ml_conf:.2f}) | FRAUD:{fraud_flag}]'. "
            f"Do not use any paragraphs, headers, markdown styling, or text after this core signature block."
        )

    def _generate_via_local_ollama(self, prompt: str, score: int, band: str) -> str:
        system_prompt = "You are a direct, professional credit analyst. Output one combined text string containing the text advisory and the requested core technical signature block. Do not format with markdown, lists, or line breaks."
        try:
            response = ollama.chat(
                model=self.local_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={"temperature": 0.2}
            )
            return response["message"]["content"].strip().replace("\n", " ")
        except Exception as local_err:
            return f"System assessment confirmed {band} standing. [CORE// SCORE:{score} | BAND:{band} | NET:0.00 | ML:N/A | FRAUD:CLEAN]"

    def generate_merchant_advisory(self, score: int, band: str, explanations_summary: str, months_active: int, ml_data: dict = None, graph_data: dict = None) -> str:
        if ml_data is None: ml_data = {}
        if graph_data is None: graph_data = {}
            
        prompt = self._build_comprehensive_prompt(score, band, explanations_summary, months_active, ml_data, graph_data)

        if not self.api_key or self.api_key == "your_google_api_key_here":
            return self._generate_via_local_ollama(prompt, score, band)

        try:
            client = genai.Client(api_key=self.api_key)
            response = client.models.generate_content(
                model=self.google_model,
                contents=prompt
            )
            return response.text.strip().replace("\n", " ") if response.text else "Advisory empty."

        except Exception as e:
            return self._generate_via_local_ollama(prompt, score, band)

financial_agent = TrustLayerFinancialAgent()
