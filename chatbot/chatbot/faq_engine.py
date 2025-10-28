import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FAQEngine:
    def __init__(self, faq_csv_path: str):
        self.df = pd.read_csv("D:/AI-Chatbot-Agent/data/faq.csv")
        self.df["question"] = self.df["question"].fillna("")
        self.df["answer"] = self.df["answer"].fillna("")
        self.vec = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        self.X = self.vec.fit_transform(self.df["question"].tolist())

    def answer_for_intent(self, user_text: str, intent: str):
        sub = self.df[self.df["intent"] == intent]
        if sub.empty:
            sub = self.df
        X_sub = self.vec.transform(sub["question"].tolist())
        qv = self.vec.transform([user_text])
        sims = cosine_similarity(qv, X_sub)[0]
        best_idx = sims.argmax()
        import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class FAQEngine:
    def __init__(self, faq_csv_path: str):
        # Use provided path instead of hardcoding
        self.df = pd.read_csv(faq_csv_path)
        
        # Ensure required columns exist
        for col in ["question", "answer"]:
            if col not in self.df.columns:
                self.df[col] = ""
                
        self.df["question"] = self.df["question"].fillna("")
        self.df["answer"] = self.df["answer"].fillna("")
        
        self.vec = TfidfVectorizer(ngram_range=(1,2), min_df=1)
        self.X = self.vec.fit_transform(self.df["question"].tolist())

    def answer_for_intent(self, user_text: str, intent: str):
        if "intent" in self.df.columns:
            sub = self.df[self.df["intent"] == intent]
        else:
            sub = self.df  # fallback if no intent column

        if sub.empty:
            sub = self.df

        # Transform only the subset
        X_sub = self.vec.transform(sub["question"].tolist())
        qv = self.vec.transform([user_text])

        sims = cosine_similarity(qv, X_sub)[0]
        best_idx = sims.argmax()
        return sub.iloc[best_idx]["answer"]

        return sub.iloc[best_idx]["answer"]
