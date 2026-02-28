"""Thin wrapper around the Ollama REST API."""

import json

import requests

BASE_URL = "http://localhost:11434"


def check_running():
    """Return True if the Ollama server is reachable."""
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        return resp.status_code == 200
    except requests.ConnectionError:
        return False


def list_models():
    """Return a list of locally-installed model names."""
    resp = requests.get(f"{BASE_URL}/api/tags", timeout=10)
    resp.raise_for_status()
    return [m["name"] for m in resp.json().get("models", [])]


def pull_model(name):
    """Pull a model, streaming progress to stdout."""
    resp = requests.post(
        f"{BASE_URL}/api/pull",
        json={"name": name},
        stream=True,
        timeout=600,
    )
    resp.raise_for_status()
    last_status = ""
    for line in resp.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        status = data.get("status", "")
        if status != last_status:
            print(status)
            last_status = status
        # Show download progress
        total = data.get("total")
        completed = data.get("completed")
        if total and completed:
            pct = completed / total * 100
            print(f"\r  {pct:.0f}%", end="", flush=True)
    print()


def generate(model, prompt, stream=True):
    """Generate a response. Yields text chunks if stream=True, else returns full text."""
    resp = requests.post(
        f"{BASE_URL}/api/generate",
        json={"model": model, "prompt": prompt, "stream": stream},
        stream=stream,
        timeout=300,
    )
    resp.raise_for_status()
    if not stream:
        return resp.json().get("response", "")
    return _stream_chunks(resp)


def _stream_chunks(resp):
    """Yield text chunks from a streaming response."""
    for line in resp.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        chunk = data.get("response", "")
        if chunk:
            yield chunk


def create_model(name, modelfile):
    """Create a model from a Modelfile string."""
    resp = requests.post(
        f"{BASE_URL}/api/create",
        json={"name": name, "modelfile": modelfile},
        stream=True,
        timeout=120,
    )
    resp.raise_for_status()
    for line in resp.iter_lines():
        if not line:
            continue
        data = json.loads(line)
        status = data.get("status", "")
        if status:
            print(status)


def delete_model(name):
    """Delete a model from Ollama."""
    resp = requests.delete(
        f"{BASE_URL}/api/delete",
        json={"name": name},
        timeout=30,
    )
    resp.raise_for_status()
