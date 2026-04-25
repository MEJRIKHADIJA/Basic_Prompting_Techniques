import json
import os
import re
from pathlib import Path

import requests
from flask import Flask, jsonify, request, send_file

HOST = "127.0.0.1"
PORT = int(os.getenv("PORT", "8000"))
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
INDEX_FILE = Path(__file__).with_name("index.html")
REVIEW_TEXT = (
    "The movie had great visuals, but the story was confusing and boring."
)
LABEL_PATTERN = re.compile(r"\b(Positive|Negative|Neutral)\b", re.IGNORECASE)

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

ZERO_SHOT_TEMPLATE = (
    "Classify this movie review as Positive, Negative, or Neutral.\n"
    "Return only one label: Positive, Negative, or Neutral.\n\n"
    'Review: "{review}"\n'
    "Classification:"
)

FEW_SHOT_TEMPLATE = (
    "Classify this movie review as Positive, Negative, or Neutral.\n"
    "Return only one label: Positive, Negative, or Neutral.\n\n"
    'Example 1: "The film was amazing and visually stunning." -> Positive\n'
    'Example 2: "The movie was terrible and a waste of time." -> Negative\n'
    'Example 3: "It was an average movie, nothing special." -> Neutral\n\n'
    'Review: "{review}"\n'
    "Classification:"
)


def extract_label(response_text: str) -> str:
    """Extract the sentiment label from the model response."""
    match = LABEL_PATTERN.search(response_text)
    if match:
        return match.group(1).capitalize()
    return response_text.strip()


def call_llm(prompt: str, model_name: str = MODEL_NAME) -> str:
    """Send a prompt to the LLM using Ollama and return the raw response text."""
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/chat",
            json={
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()
        return result.get("message", {}).get("content", "").strip()
    except requests.exceptions.ConnectionError:
        raise EnvironmentError(f"Could not connect to Ollama at {OLLAMA_API_URL}. Make sure Ollama is running.")
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            raise EnvironmentError(f"Model '{model_name}' not found. Please install it with: ollama pull {model_name}")
        raise EnvironmentError(f"HTTP Error from Ollama: {exc}")
    except Exception as exc:
        raise EnvironmentError(f"Error calling Ollama API: {exc}")


def zero_shot_classify(review: str) -> dict:
    """Classify a review using zero-shot prompting."""
    prompt = ZERO_SHOT_TEMPLATE.format(review=review)
    raw_response = call_llm(prompt)
    return {
        "mode": "zero-shot",
        "prompt": prompt,
        "review": review,
        "raw_response": raw_response,
        "label": extract_label(raw_response),
    }


def few_shot_classify(review: str) -> dict:
    """Classify a review using few-shot prompting."""
    prompt = FEW_SHOT_TEMPLATE.format(review=review)
    raw_response = call_llm(prompt)
    return {
        "mode": "few-shot",
        "prompt": prompt,
        "review": review,
        "raw_response": raw_response,
        "label": extract_label(raw_response),
    }


# Flask Routes
@app.route("/")
@app.route("/index.html")
def serve_index():
    """Serve the index.html file."""
    if not INDEX_FILE.exists():
        return jsonify({"error": "index.html was not found."}), 500
    return send_file(INDEX_FILE, mimetype="text/html")


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "default_review": REVIEW_TEXT,
        "model": MODEL_NAME,
        "provider": "Ollama",
        "ollama_url": OLLAMA_API_URL,
    })


@app.route("/api/classify", methods=["POST"])
def classify():
    """Classify a review using the specified mode."""
    try:
        data = request.get_json() or {}
        review = str(data.get("review", REVIEW_TEXT)).strip() or REVIEW_TEXT
        mode = str(data.get("mode", "")).strip().lower()
        
        if mode == "zero-shot":
            result = zero_shot_classify(review)
        elif mode == "few-shot":
            result = few_shot_classify(review)
        else:
            return jsonify({"error": "Mode must be zero-shot or few-shot."}), 400
            
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/zero-shot", methods=["POST"])
def zero_shot():
    """Zero-shot classification endpoint."""
    try:
        data = request.get_json() or {}
        review = str(data.get("review", REVIEW_TEXT)).strip() or REVIEW_TEXT
        result = zero_shot_classify(review)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/few-shot", methods=["POST"])
def few_shot():
    """Few-shot classification endpoint."""
    try:
        data = request.get_json() or {}
        review = str(data.get("review", REVIEW_TEXT)).strip() or REVIEW_TEXT
        result = few_shot_classify(review)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


def main() -> None:
    """Run the Flask development server."""
    print(f"Prompt Engineering Demo running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop the server.")
    app.run(host=HOST, port=PORT, debug=False)


if __name__ == "__main__":
    main()
