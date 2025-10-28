import os
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Agar __file__ available nahi hai toh fallback use karo
try:
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
except NameError:
    BASE_DIR = os.getcwd()

DATA_PATH = os.path.join(BASE_DIR, "data", "intents.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "intent_model.joblib")

INTENTS = [
    "shipping_policy","return_policy","warranty","payment",
    "track_order","cancellation","store_hours","greeting",
    "goodbye","thanks","product_recommendation","fallback"
]

def train_and_save():
    # yaha DATA_PATH use karo
    df = pd.read_csv("D:\AI-Chatbot-Agent\data\intents.csv")
    X_train, X_test, y_train, y_test = train_test_split(df["text"], df["intent"], test_size=0.2, random_state=42)
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
        ("clf", LinearSVC())
    ])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    report = classification_report(y_test, y_pred, labels=INTENTS, zero_division=0)
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    return report, MODEL_PATH

if __name__ == "__main__":
    report, path = train_and_save()
    print("Model saved to:", path)
    print(report)
