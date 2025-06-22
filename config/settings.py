"""
Configuration settings for Biblical RAG Chatbot
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # API Keys
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(DATA_DIR / "chroma_db"))
    BIBLE_DATA_PATH = os.getenv("BIBLE_DATA_PATH", str(DATA_DIR / "bible_data.json"))
    
    # App Configuration
    APP_TITLE = os.getenv("APP_TITLE", "🙏 Biblical RAG Chatbot")
    APP_ICON = os.getenv("APP_ICON", "🙏")
    
    # Model Configuration
    DEFAULT_MODEL = "gpt-4o-mini"
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # RAG Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    RETRIEVAL_K = 5  # Number of documents to retrieve
    
    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file")
        
        return True

# Create config instance
config = Config() 