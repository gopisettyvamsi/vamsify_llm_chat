import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.2-1b-instruct-q4_k_m.gguf")
MODEL_PATH = MODELS_DIR / MODEL_NAME
MODEL_URL = os.getenv(
    "MODEL_URL",
    "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf"
)

# System prompt
SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful AI assistant. You provide clear, accurate, and concise responses. You are friendly and professional."
)

# Conversation settings
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "10"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

# Server settings
PORT = int(os.getenv("PORT", "5000"))
HOST = os.getenv("HOST", "0.0.0.0")

# LLM settings
N_CTX = 2048  # Context window size
N_THREADS = None  # Auto-detect CPU threads
N_GPU_LAYERS = 0  # CPU only (set to -1 for GPU)
