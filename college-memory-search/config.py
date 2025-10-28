import os
from dotenv import load_dotenv

load_dotenv()

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("⚠️ GROQ_API_KEY not found in .env file!")

# Vector Database Configuration
COLLECTION_NAME = "college_lectures"
PERSIST_DIRECTORY = "./chroma_db"

# Groq Model Configuration
GROQ_MODEL = "llama-3.3-70b-versatile"  # Latest and most capable model
# Alternative models:
# "llama-3.1-8b-instant" - Fastest, good for quick responses
# "llama-3.1-70b-versatile" - Balanced performance
# "mixtral-8x7b-32768" - Good for long context