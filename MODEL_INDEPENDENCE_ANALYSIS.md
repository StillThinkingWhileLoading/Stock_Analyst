# Model Independence Analysis

## Executive Summary

**Status: ❌ NOT FULLY MODEL INDEPENDENT**

The project is **hardcoded to use xAI's ChatXAI** (`langchain_xai`). You cannot simply change the environment variables to use Claude, OpenAI, or Ollama. However, **making it model-independent is straightforward** — just 3 files need modification.

---

## Current Limitations

### 1. Hard Dependency on ChatXAI

**File**: `nodes/base.py`
```python
from langchain_xai import ChatXAI  # ← Hard import

_model = ChatXAI(
    api_key=os.getenv('XAI_API_KEY'),
    model=os.getenv('MODEL_NAME', 'grok-3-mini'),
    temperature=float(os.getenv('TEMPERATURE', '0.2')),
)
```

**Problem**: 
- Only `ChatXAI` is imported and instantiated
- Changing `MODEL_NAME` to `claude-opus-4-7` won't work — the code doesn't know how to use Claude
- `XAI_API_KEY` is hardcoded environment variable name

### 2. Environment Variables Are Grok-Specific

**File**: `.env`
```env
XAI_API_KEY=xai-...          # ← Only for Grok
MODEL_NAME=grok-3-mini       # ← Only accepts grok models
```

**Problem**:
- No `ANTHROPIC_API_KEY` variable
- No `OPENAI_API_KEY` variable
- No generic `LLM_PROVIDER` selector

### 3. Package Dependencies

**Installed but Conditional**:
- ✅ `langchain-xai==1.2.2` (XAI Grok)
- ✅ `langchain-openai==1.1.12` (OpenAI)
- ❌ `langchain-anthropic` (Claude) — NOT installed
- ❌ `ollama` — NOT installed

---

## What IS Model-Independent

### ✅ Prompts Are Generic
All prompts in the analyst nodes are **model-agnostic**:
- No Grok-specific instructions
- No mentions of "Grok" or "xAI"
- Work equally well with Claude, OpenAI, or Ollama
- Standard financial analysis terminology

**Example** (`nodes/bull_analyst.py`):
```python
prompt = f"""
System Role: Senior Global Equity Strategist...
Task: Produce a Bull Case Synthesis...
Confidence Rating: X / 10 (7-10 scale)...
"""
# ← Works with ANY LLM
```

### ✅ LangGraph Architecture Is Agnostic
The graph itself (`graph/bull_bear_graph.py`) doesn't care which LLM is used:
```python
from nodes import (
    fetch_stock_data,
    news_analyst,
    bull_analyst,
    bear_analyst,
    financial_analyst,
)
# ← Just uses node callables, doesn't know about ChatXAI
```

### ✅ Rating Extraction Is Universal
`tools/formatters.py` extracts ratings via regex — works for any LLM output:
```python
def extract_rating(analysis_text: str) -> str:
    patterns = [
        r'(?i)\*{0,2}(?:Bull|Bear|Confidence)\s*Rating\s*:\*{0,2}\s*(\d{1,2})',
        r'(\d{1,2})\s*(?:/|out of)\s*10',
    ]
    # ← Works whether Claude, OpenAI, or Grok outputs the rating
```

---

## How to Make It Model-Independent

### Option 1: Use LangChain's `init_chat_model()` (Simplest)

Modify `nodes/base.py`:

```python
import os
from dotenv import load_dotenv
from langchain import init_chat_model

load_dotenv()

# Single shared model instance used by all analyst nodes
_model = init_chat_model(
    model=os.getenv('MODEL_NAME', 'grok-3-mini'),
    temperature=float(os.getenv('TEMPERATURE', '0.2')),
    api_key=os.getenv('LLM_API_KEY'),  # Generic API key
)

class BaseNode:
    def __init__(self):
        self.model = _model
```

**Why this works**:
- LangChain's `init_chat_model()` auto-detects the provider from the model name
- `"claude-opus-4-7"` → uses Claude
- `"gpt-4"` → uses OpenAI
- `"grok-3-mini"` → uses Grok
- Single API key field works for all (each provider reads its own env var)

**Update `.env`**:
```env
# Choose ONE provider:

# For Claude:
# MODEL_NAME=claude-opus-4-7
# ANTHROPIC_API_KEY=sk-ant-...

# For OpenAI:
# MODEL_NAME=gpt-4
# OPENAI_API_KEY=sk-...

# For Grok (current):
MODEL_NAME=grok-3-mini
XAI_API_KEY=xai-...

# For Ollama (local):
# MODEL_NAME=llama2
# (No API key needed)

TEMPERATURE=0.2
```

### Option 2: Manual Provider Detection (More Control)

```python
import os
from dotenv import load_dotenv

load_dotenv()

def get_model():
    model_name = os.getenv('MODEL_NAME', 'grok-3-mini')
    temperature = float(os.getenv('TEMPERATURE', '0.2'))
    
    if 'grok' in model_name.lower():
        from langchain_xai import ChatXAI
        return ChatXAI(
            api_key=os.getenv('XAI_API_KEY'),
            model=model_name,
            temperature=temperature,
        )
    elif 'claude' in model_name.lower():
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY'),
            model_name=model_name,
            temperature=temperature,
        )
    elif 'gpt' in model_name.lower():
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model=model_name,
            temperature=temperature,
        )
    elif 'llama' in model_name.lower() or 'mistral' in model_name.lower():
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model_name,
            temperature=temperature,
        )
    else:
        raise ValueError(f"Unknown model provider: {model_name}")

_model = get_model()

class BaseNode:
    def __init__(self):
        self.model = _model
```

---

## Required Changes Summary

To support Claude, OpenAI, and Ollama:

| File | Change | Impact |
|------|--------|--------|
| `nodes/base.py` | Replace `ChatXAI` with `init_chat_model()` or router | HIGH |
| `.env` | Add `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc. | MEDIUM |
| `.env.example` | Document all provider options | LOW |
| `requirements.txt` (if exists) | Add `langchain-anthropic`, `langchain-ollama` | LOW |

---

## Testing Different Models

Once modified, test with:

```bash
# Test with Claude
export MODEL_NAME=claude-opus-4-7
export ANTHROPIC_API_KEY=sk-ant-...
python main.py

# Test with OpenAI
export MODEL_NAME=gpt-4
export OPENAI_API_KEY=sk-...
python main.py

# Test with Ollama (local, no key needed)
export MODEL_NAME=llama2
python main.py
```

---

## Recommendation

**Use Option 1** (`init_chat_model()`) because:
1. ✅ Single line change
2. ✅ Works with ANY LangChain provider
3. ✅ Future-proof (if new providers added)
4. ✅ Minimal dependencies (just rely on LangChain)
5. ✅ Clean separation of concerns

---

## Conclusion

**Current State**: Model-locked to Grok  
**Effort to Fix**: ~15 minutes (3 files)  
**Result**: Works with Claude, OpenAI, Ollama, Cohere, etc.

The prompts and logic are already universal — only the model instantiation layer needs abstraction.
