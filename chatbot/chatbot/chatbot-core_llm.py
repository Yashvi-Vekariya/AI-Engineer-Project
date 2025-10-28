# chatbot/core_llm.py
import os
import pandas as pd

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FAQ_CSV = os.path.join(BASE_DIR, "data", "faq.csv")
PRODUCTS_CSV = os.path.join(BASE_DIR, "data", "products.csv")

# Intents we support
INTENTS = [
    "shipping_policy","return_policy","warranty","payment",
    "track_order","cancellation","store_hours","greeting",
    "goodbye","thanks","product_recommendation","fallback"
]

SAFE_DEFAULTS = {
    "greeting": "Hi! How can I help you today? You can ask about shipping, returns, warranty, payments, or product suggestions.",
    "goodbye": "Goodbye! Have a great day 👋",
    "thanks": "You're welcome! Anything else I can help with?",
    "fallback": "Sorry, I didn't catch that. Ask about shipping, returns, warranty, payments, order tracking, or product recommendations."
}

def clean_text(x):
    return "" if pd.isna(x) else str(x)

class ChatBot:
    def __init__(self):
        # 1) LLM & Embeddings
        # NOTE: OPENAI_API_KEY should be present in environment
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)  # low temp for deterministic intent
        self.embed = OpenAIEmbeddings()

        # 2) Load data
        self.faq_df = pd.read_csv(FAQ_CSV)
        needed_faq_cols = ["question", "answer", "intent"]
        for c in needed_faq_cols:
            if c not in self.faq_df.columns:
                self.faq_df[c] = ""
        self.faq_df["question"] = self.faq_df["question"].apply(clean_text)
        self.faq_df["answer"]   = self.faq_df["answer"].apply(clean_text)
        self.faq_df["intent"]   = self.faq_df["intent"].apply(clean_text)

        self.products_df = pd.read_csv(PRODUCTS_CSV)
        # expected columns: id,name,category,price,rating,tags,description
        for c in ["id","name","category","price","rating","tags","description"]:
            if c not in self.products_df.columns:
                self.products_df[c] = ""

        # 3) Build FAISS for FAQ (semantic search over questions)
        faq_texts = (self.faq_df["question"]).tolist()
        faq_metas = self.faq_df.to_dict("records")
        self.faq_store = FAISS.from_texts(faq_texts, self.embed, metadatas=faq_metas)

        # 4) Build FAISS for Products (semantic search over name+desc+tags)
        prod_texts = (self.products_df["name"].fillna("") + " "
                      + self.products_df["tags"].fillna("") + " "
                      + self.products_df["description"].fillna("")).tolist()
        prod_metas = self.products_df.to_dict("records")
        self.prod_store = FAISS.from_texts(prod_texts, self.embed, metadatas=prod_metas)

    # ---------- helpers ----------
    def _classify_intent(self, user_text: str) -> str:
        """Use LLM to classify user_text into one of INTENTS."""
        label_list = ", ".join(INTENTS)
        prompt = (
            "You are an intent classifier. "
            f"Return exactly one label from: {label_list}.\n"
            f"User: {user_text}\n"
            "Answer with only the label, nothing else."
        )
        resp = self.llm.invoke(prompt)
        label = str(resp.content).strip().lower()
        return label if label in INTENTS else "fallback"

    def _answer_faq(self, user_text: str, intent: str) -> str:
        """Semantic search over FAQ (filter by intent if possible), then LLM rephrase the best answer."""
        k = 4  # retrieve few candidates
        docs = self.faq_store.similarity_search(user_text, k=k)
        # Prefer docs whose metadata.intent matches requested intent
        ranked = []
        for d in docs:
            meta = d.metadata or {}
            score_boost = 1.0 if meta.get("intent","") == intent else 0.0
            ranked.append((score_boost, meta))
        ranked.sort(key=lambda x: x[0], reverse=True)
        best = ranked[0][1] if ranked else {}

        answer_text = best.get("answer") or ""
        if not answer_text:
            return SAFE_DEFAULTS["fallback"]

        # Let LLM polish the final answer briefly
        polish_prompt = (
            "Rewrite the following answer in one or two concise sentences, keep policy details intact:\n"
            f"Answer: {answer_text}"
        )
        resp = self.llm.invoke(polish_prompt)
        return resp.content.strip() if hasattr(resp, "content") else answer_text

    def _recommend_products(self, user_text: str, top_k: int = 3) -> str:
        docs = self.prod_store.similarity_search(user_text, k=top_k)
        if not docs:
            return "I couldn't find matching products. Please share your budget and category (phone, laptop, headphones, etc.)."

        lines = []
        for d in docs:
            m = d.metadata or {}
            name = m.get("name", "Product")
            price = m.get("price", "NA")
            rating = m.get("rating", "NA")
            desc = m.get("description", "")
            lines.append(f"- {name} (₹{price}, rating {rating}/5): {desc}")
        return "Here are some picks for you:\n" + "\n".join(lines)

    # ---------- main entry ----------
    def handle(self, user_text: str) -> str:
        intent = self._classify_intent(user_text)

        if intent in ("greeting","goodbye","thanks","fallback"):
            return SAFE_DEFAULTS[intent]

        if intent in ("shipping_policy","return_policy","warranty","payment",
                      "track_order","cancellation","store_hours"):
            return self._answer_faq(user_text, intent)

        if intent == "product_recommendation":
            return self._recommend_products(user_text, top_k=3)

        return SAFE_DEFAULTS["fallback"]
