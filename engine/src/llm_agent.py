from google import genai
from config.settings import settings

class TrustLayerFinancialAgent:
    """Dedicated AI agent for translating credit math into empathetic financial advice."""
    
    def __init__(self):
        # Securely pull the key from our new settings file
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = 'gemini-3.5-flash'
        
    def generate_merchant_advisory(self, score: int, band: str, explanations_summary: str, months_active: int) -> str:
        """Generates a 3-sentence actionable summary for the merchant."""
        
        if not self.api_key or self.api_key == "your_google_api_key_here":
            return f"AI summary engine offline (Check API Key). System assessment: {band} tier."

        try:
            client = genai.Client(api_key=self.api_key)
            
            # The System Persona (Prompt Engineering)
            prompt = (
                f"You are an empathetic financial inclusion AI advisor in Nepal. A small business merchant "
                f"has been audited by our alternative credit scoring system. Here are their metrics:\n"
                f"- Alternative Credit Score: {score}/900\n"
                f"- Risk Classification Category: {band}\n"
                f"- Length of Business Activity: {months_active} months\n"
                f"- Primary Impact Factors: {explanations_summary}\n\n"
                f"Write a clear, encouraging, and highly specific evaluation to the merchant. Explain "
                f"the positive factors supporting them and give exactly 2 concrete behavioral steps they "
                f"can take to lift their loan ceiling safely. Keep the tone professional, localized, and friendly. "
                f"Do NOT use placeholders like [Merchant Name]. Write strictly 3 concise sentences."
            )

            # Generate the response
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            return response.text.strip() if response.text else "Advisory generation returned empty."

        except Exception as e:
            print(f"\n=== [LLM AGENT FAULT] ===\n{str(e)}\n=========================\n")
            return f"AI summary engine currently offline. System assessment: {band} tier standing."

# Export a single instance to be used by the router
financial_agent = TrustLayerFinancialAgent()