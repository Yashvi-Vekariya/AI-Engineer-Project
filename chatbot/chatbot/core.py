import os, joblib, pandas as pd
from .faq_engine import FAQEngine
from .recommender import recommend_products
from .train_intent import train_and_save

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "intent_model.joblib")
FAQ_CSV = os.path.join(BASE_DIR, "data", "faq.csv")
PRODUCTS_CSV = os.path.join(BASE_DIR, "data", "products.csv")

SAFE_DEFAULTS = {
    "greeting": "Hi! How can I help you today? You can ask about shipping, returns, warranty, payments, or ask for product suggestions.",
    "goodbye": "Goodbye! Have a great day 👋",
    "thanks": "You're welcome! Anything else I can help with?",
    "fallback": "Hmm, I didn't quite get that. You can ask me about shipping, returns, warranty, payments, order tracking, or product recommendations."
}

class ChatBot:
    def __init__(self):
        # Load or train model
        if not os.path.exists(MODEL_PATH):
            print("Intent model not found, training a new one...")
            report, _ = train_and_save()
            print(report)
        self.model = joblib.load(MODEL_PATH)
        self.faq = FAQEngine(FAQ_CSV)
        self.products_df = pd.read_csv(PRODUCTS_CSV)

    def predict_intent(self, text: str):
        return self.model.predict([text])[0]

    def handle(self, user_text: str):
        intent = self.predict_intent(user_text)

        if intent in SAFE_DEFAULTS:
            return SAFE_DEFAULTS[intent]

        if intent in ("shipping_policy","return_policy","warranty","payment","track_order","cancellation","store_hours"):
            return self.faq.answer_for_intent(user_text, intent)

        if intent == "product_recommendation":
            recs = recommend_products(user_text, self.products_df, top_k=3)
            if not recs:
                return "I couldn't find matching products. Can you share your budget or category (phone, laptop, headphones, etc.)?"
            lines = [f"- {r['name']} (₹{r['price']}, rating {r['rating']}/5): {r['description']}" for r in recs]
            return "Here are some picks for you:\n" + "\n".join(lines)

        return SAFE_DEFAULTS["fallback"]
