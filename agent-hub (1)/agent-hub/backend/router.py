"""Bepul API'lar orasida avtomatik almashadigan model router."""
import os
import httpx

PROVIDERS = [
    ("groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY", "llama-3.3-70b-versatile"),
    ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY", "gemini-2.0-flash"),
    ("cerebras", "https://api.cerebras.ai/v1", "CEREBRAS_API_KEY", "llama-3.3-70b"),
    ("openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "meta-llama/llama-3.3-70b-instruct:free"),
    ("mistral", "https://api.mistral.ai/v1", "MISTRAL_API_KEY", "mistral-small-latest"),
]

async def chat(messages, on_log=None):
    errors = []
    async with httpx.AsyncClient(timeout=60) as client:
        for name, url, env, model in PROVIDERS:
            key = os.getenv(env)
            if not key:
                continue
            try:
                r = await client.post(f"{url}/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={"model": model, "messages": messages, "temperature": 0.3})
                r.raise_for_status()
                return r.json()["choices"][0]["message"]["content"]
            except Exception as e:
                errors.append(f"{name}: {e}")
                if on_log: await on_log(f"{name} ishlamadi, keyingisiga o'tilmoqda")
    raise RuntimeError("Hech bir API ishlamadi. .env faylni tekshiring. " + "; ".join(errors))
