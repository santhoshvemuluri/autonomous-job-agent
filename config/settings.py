import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Pipeline Configuration
MIN_ATS_SCORE = 90.0
MAX_ITERATIONS = 3

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MASTER_PROFILE_PATH = os.path.join(DATA_DIR, "master_profile.json")
GENERATED_RESUMES_DIR = os.path.join(DATA_DIR, "generated_resumes")