# AI Retail Product Description Generator

A Flask web app that uses a local LLM (via Ollama) to generate product descriptions from a product name and comma-separated keywords. Includes tone/customer-segment and length selection.

## Demo Video

[Watch the demo](retail-ai-app-demo.mp4)

## Files

- `app.py` - Flask application and LLM integration
- `templates/index.html` - input form and output display
- `writeup.md` - short write-up (LLM choice, challenges, improvements, ethics)

## Setup

1. Install and start [Ollama](https://ollama.com), then pull a small model:
   ```
   ollama pull gemma3:1b
   ```
2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install flask requests
   ```
3. Run the app:
   ```
   python app.py
   ```
4. Open http://127.0.0.1:5000/

To use a different model, set `OLLAMA_MODEL` (for example `OLLAMA_MODEL=phi3 python app.py`).

## Usage

Enter a product name and keywords (e.g. `lightweight, waterproof, grippy`), choose a tone and length, then click **Generate description**.
