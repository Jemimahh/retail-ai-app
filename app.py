"""AI Product Description Generator (Flask + local Ollama LLM).

Run:
    ollama pull gemma3:1b        # or any small model: phi3, qwen2.5:1.5b, ...
    pip install flask requests
    python app.py
Then open http://127.0.0.1:5000/
"""
import os
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:1b")
TIMEOUT_SECONDS = 120

# Stretch goal: each tone maps to a customer segment and style instructions.
# This acts as a small rule-based "decision model" that programs the prompt.
TONES = {
    "professional": {
        "segment": "business buyers and detail-oriented shoppers",
        "style": "clear, polished and credible. Focus on quality, reliability and value.",
    },
    "friendly": {
        "segment": "everyday shoppers",
        "style": "warm, conversational and approachable, as if a helpful store associate is talking.",
    },
    "luxury": {
        "segment": "premium, high-end customers",
        "style": "elegant and refined. Emphasize craftsmanship, exclusivity and sensory detail.",
    },
    "playful": {
        "segment": "younger, social-media-savvy shoppers",
        "style": "fun, energetic and witty, with light humor. No more than one emoji.",
    },
    "eco": {
        "segment": "sustainability-minded consumers",
        "style": "honest and earthy. Highlight durability and responsible choices without making unverifiable claims.",
    },
}

LENGTHS = {
    "short": "about 40 words (one short paragraph)",
    "medium": "about 80 words (one paragraph)",
    "long": "about 150 words (two short paragraphs)",
}


def build_prompt(product_name, keywords, tone, length):
    t = TONES.get(tone, TONES["professional"])
    return (
        "You are an expert e-commerce copywriter.\n"
        f"Write a product description for: {product_name}\n"
        f"Naturally work in these keywords: {', '.join(keywords)}\n"
        f"Target customer segment: {t['segment']}\n"
        f"Tone and style: {t['style']}\n"
        f"Length: {LENGTHS.get(length, LENGTHS['medium'])}\n"
        "Rules: use only the information given, do not invent specifications, "
        "prices, awards or certifications, and do not use a heading. "
        "Output only the description text."
    )


def generate_description(product_name, keywords, tone="professional", length="medium"):
    """Call the local Ollama model and return the description text.

    Raises RuntimeError with a user-friendly message on failure.
    """
    payload = {
        "model": MODEL,
        "prompt": build_prompt(product_name, keywords, tone, length),
        "stream": False,
        "options": {"temperature": 0.7},
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Could not reach Ollama. Make sure it is running (ollama serve) "
            f"at {OLLAMA_URL}."
        )
    except requests.exceptions.Timeout:
        raise RuntimeError("The model took too long to respond. Try a shorter length or a smaller model.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(
            f"Ollama returned an error ({e.response.status_code}). "
            f"Is the model '{MODEL}' installed? Try: ollama pull {MODEL}"
        )
    except ValueError:
        raise RuntimeError("Received an unreadable response from the model.")

    if not text:
        raise RuntimeError("The model returned an empty description. Please try again.")
    return text


@app.route("/", methods=["GET", "POST"])
def index():
    form = {"product_name": "", "keywords": "", "tone": "professional", "length": "medium"}
    description, error = None, None

    if request.method == "POST":
        form["product_name"] = request.form.get("product_name", "").strip()
        form["keywords"] = request.form.get("keywords", "").strip()
        form["tone"] = request.form.get("tone", "professional")
        form["length"] = request.form.get("length", "medium")

        keywords = [k.strip() for k in form["keywords"].split(",") if k.strip()]

        if not form["product_name"]:
            error = "Please enter a product name."
        elif not keywords:
            error = "Please enter at least one keyword (comma-separated)."
        else:
            try:
                description = generate_description(
                    form["product_name"], keywords, form["tone"], form["length"]
                )
            except RuntimeError as e:
                error = str(e)

    return render_template(
        "index.html",
        form=form,
        tones=TONES,
        lengths=LENGTHS,
        description=description,
        error=error,
        model=MODEL,
    )


if __name__ == "__main__":
    app.run(debug=True)
