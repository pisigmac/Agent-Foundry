# or latest Unsloth per their guidance

Minimal example to finetune Google's Gemma 3 Instruct models with Unsloth using 4-bit loading + LoRA. Small, readable, and runnable on a CUDA GPU.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

## Architecture

This module uses a modular pipeline approach with clear separation between data ingestion, processing, and output generation.

## Configuration

Set your API keys in environment variables or a `.env` file before running.

## License

Apache-2.0
