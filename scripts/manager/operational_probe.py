"""One bounded localhost-only actual chat probe for a freshly switched model.

This is invoked *after* the guarded executor has started and identity-verified
the target. It proves user-visible text generation, not instruction adherence,
tool calling, or benchmark throughput. Never changes Docker or model state.
"""
from __future__ import annotations

import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ALLOWED_IDS = frozenset(("qwen3.8-flash-next", "qwen3.8-27b"))
ENDPOINT = "http://127.0.0.1:8000/v1/chat/completions"


def verify_chat(served_id: str, *, opener=urlopen) -> bool:
    """Return False on every uncertain outcome; never infer from HTTP 200 alone."""
    if served_id not in ALLOWED_IDS:
        return False
    payload = {
        "model": served_id,
        "messages": [{"role": "user", "content": "Reply with the word ready."}],
        "temperature": 0,
        "max_tokens": 128,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    request = Request(ENDPOINT, data=json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json"}, method="POST")
    try:
        with opener(request, timeout=90) as reply:
            if reply.status != 200:
                return False
            raw = reply.read(65537)
            if not raw or len(raw) > 65536:
                return False
            parsed = json.loads(raw)
        choices = parsed["choices"]
        if (parsed.get("model") != served_id
                or not isinstance(choices, list) or len(choices) != 1):
            return False
        answer = choices[0]["message"]["content"]
        return (isinstance(answer, str) and bool(answer.strip())
                and choices[0].get("finish_reason") == "stop")
    except (OSError, URLError, HTTPError, ValueError, TypeError, KeyError,
            IndexError, TimeoutError):
        return False
