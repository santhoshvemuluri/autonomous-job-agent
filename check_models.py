import os
from dotenv import load_dotenv
from groq import Groq

# Load your API key from .env
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Fetch the exact models your account is allowed to use
try:
    models = client.models.list()
    print("\n✅ SUCCESS! Here are the exact model names you can use:\n")
    for m in models.data:
        print(f'"{m.id}"')
    print("\nPick ONE of the names above and paste it into src/agents/tailor.py and ats_evaluator.py")
except Exception as e:
    print(f"\n❌ Error fetching models: {e}")