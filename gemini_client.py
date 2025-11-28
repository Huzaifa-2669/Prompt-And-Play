"""
gemini_client.py
Lightweight wrapper around a Gemini-style LLM API to generate extension files.

This module attempts to talk to Gemini via a simple REST POST. It expects
an API key in the GEMINI_API_KEY environment variable. The client requests a
structured JSON response containing file names and their contents.

The implementation is intentionally defensive so it can be mocked in tests
or fall back to local heuristics when no credentials are available.
"""
import os
import json
import logging
from typing import Dict, Any

try:
    import requests
except Exception:  # requests may not be installed in test environments
    requests = None

LOGGER = logging.getLogger(__name__)


def build_prompt(requirements: Dict[str, Any], user_prompt: str) -> str:
    """Construct a prompt for the Gemini LLM asking it to return files.

    We ask the model to return a strict JSON object with these keys
    (if applicable): popup.html, popup.js, content.js, styles.css.
    """
    request_parts = [f"User prompt: {user_prompt}"]
    request_parts.append("Detected requirements:")
    for k, v in requirements.items():
        request_parts.append(f"- {k}: {v}")

    instructions = (
        "Produce a JSON map where keys are filenames and values are the exact"
        " string contents for each file. Only return valid JSON and nothing else."
        " Provide these keys when relevant: \"popup.html\", \"popup.js\","
        " \"content.js\", \"styles.css\". If a file is not needed, omit it."
        " Escape strings appropriately so the JSON loads cleanly."
    )

    prompt = "\n".join(request_parts) + "\n\n" + instructions
    return prompt


def parse_response_text_as_json(text: str) -> Dict[str, str]:
    """Try to recover a JSON object from free-form text returned by LLMs.

    This attempts to find the first JSON-like substring and parse it.
    """
    # quick search for first { ... } block
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in response")

    candidate = text[start:end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        LOGGER.exception('Failed to decode JSON from candidate')
        raise


def generate_files(requirements: Dict[str, Any], user_prompt: str) -> Dict[str, str]:
    """Generate file contents using Gemini API.

    Returns a dict mapping filename -> content on success. Raises exceptions on
    network/format failures.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError('GEMINI_API_KEY not set in environment')

    prompt = build_prompt(requirements, user_prompt)

    # Allow override of endpoint for testing or alternate deployments
    endpoint = os.environ.get('GEMINI_API_URL', 'https://api.openai.google/v1/complete')

    if requests is None:
        raise RuntimeError('requests package not installed; cannot call Gemini API')

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    payload = {
        'model': os.environ.get('GEMINI_MODEL', 'gemini-1.5'),
        'prompt': prompt,
        'max_tokens': 4000,
        'temperature': 0.2,
        'stop': None
    }

    resp = requests.post(endpoint, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()

    # Accept JSON body (preferred) or raw text that contains JSON
    try:
        body = resp.json()
    except Exception:
        # Attempt to parse free-form text
        body_text = resp.text
        return parse_response_text_as_json(body_text)

    # Some LLM servers return {'choices':[{'text': '{...json...}'}]} or similar
    if isinstance(body, dict):
        # Common pattern: body['choices'][0]['text'] contains the JSON string
        if 'choices' in body and isinstance(body['choices'], list) and body['choices']:
            text = body['choices'][0].get('text') or body['choices'][0].get('message') or ''
            if isinstance(text, dict):
                # maybe message content
                content = text.get('content') or text.get('text') or ''
                if isinstance(content, str) and content.strip().startswith('{'):
                    return parse_response_text_as_json(content)
            if isinstance(text, str) and text.strip().startswith('{'):
                return parse_response_text_as_json(text)

        # If the top-level response already is the files map
        # e.g. some deployments might return the JSON map directly
        # Validate shape (all string values)
        if all(isinstance(v, str) for v in body.values()):
            return {k: str(v) for k, v in body.items()}

    raise RuntimeError('Unable to parse response from Gemini API')
