import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# Single shared model instance used by all analyst nodes
# Automatically detects provider from MODEL_NAME:
# - "claude-opus-4-7" or "claude-3-5-sonnet-20241022" → Anthropic Claude
# - "gpt-4" or "gpt-4-turbo" → OpenAI
# - "grok-3-mini" or "grok-3" → xAI Grok
# - "llama2", "mistral", etc. → Ollama (local)
_model = init_chat_model(
    model=os.getenv('MODEL_NAME', 'grok-3-mini'),
    temperature=float(os.getenv('TEMPERATURE', '0.2')),
)


class BaseNode:
    def __init__(self):
        self.model = _model
