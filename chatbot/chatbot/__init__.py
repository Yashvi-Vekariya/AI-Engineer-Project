import os
import joblib
import pandas as pd

class ChatBot:
    def __init__(self):
        model_path = r"D:/AI-Chatbot-Agent/models/intent_model.joblib"
        faq_path = r"D:/AI-Chatbot-Agent/data/faq.csv"
        products_path = r"D:/AI-Chatbot-Agent/data/products.csv"

        # Agar model nahi mila to train karo
        if not os.path.exists(model_path):
            from chatbot.train_intent import train_and_save
            train_and_save()

        # Model aur data load karo
        self.model = joblib.load(model_path)
        self.products_df = pd.read_csv(products_path)

        # FAQ engine load
        from chatbot.faq_engine import FAQEngine
        self.faq_engine = FAQEngine(faq_path)
