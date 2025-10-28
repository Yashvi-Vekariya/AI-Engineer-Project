import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

CATEGORY_KEYWORDS = {
    "phone": ["phone", "smartphone", "mobile", "camera phone"],
    "laptop": ["laptop", "notebook", "ultrabook"],
    "headphone": ["headphone", "headphones", "headset", "earphone", "earbuds"],
    "camera": ["camera", "vlog", "vlogging"],
    "accessory": ["accessory", "powerbank", "charger", "cable", "microphone", "mic"],
    "wearable": ["watch", "smartwatch", "fitness"],
    "gaming": ["console", "gaming"]
}

def parse_budget(text: str):
    # Extract a budget like "under 30000" / "below 30k" / "<= 40000"
    text = text.lower().replace(",", "")
    # Normalize k (e.g., 40k -> 40000)
    text = re.sub(r"(\d+)\s*k", lambda m: str(int(m.group(1)) * 1000), text)
    numbers = [int(n) for n in re.findall(r"\b\d{4,6}\b", text)]
    budget = None
    if "under" in text or "below" in text or "<=" in text or "upto" in text or "up to" in text or "less than" in text:
        budget = min(numbers) if numbers else None
    elif "around" in text or "approx" in text or "about" in text:
        budget = min(numbers) if numbers else None
    elif "under" not in text and "below" not in text and numbers:
        # User just mentioned a number; treat as budget cap
        budget = min(numbers)
    return budget

def guess_category(text: str):
    text_l = text.lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        if any(kw in text_l for kw in kws):
            return cat
    return None

def build_product_index(df: pd.DataFrame):
    corpus = (df["name"].fillna("") + " " + df["tags"].fillna("") + " " + df["description"].fillna("")).tolist()
    vec = TfidfVectorizer(ngram_range=(1,2), min_df=1)
    X = vec.fit_transform(corpus)
    return vec, X

def recommend_products(query: str, products_df: pd.DataFrame, top_k: int = 3):
    # Filter by inferred constraints
    cat = guess_category(query)
    budget = parse_budget(query)
    df = products_df.copy()
    if cat:
        df = df[df["category"] == cat]
    if budget:
        df = df[df["price"] <= budget]
    if df.empty:
        df = products_df.copy()  # fall back
    
    vec, X = build_product_index(df)
    qv = vec.transform([query])
    sims = cosine_similarity(qv, X)[0]
    df = df.assign(score=sims)
    df = df.sort_values(["score","rating"], ascending=[False, False]).head(top_k)
    cols = ["id","name","category","price","rating","description"]
    return df[cols].to_dict(orient="records")
