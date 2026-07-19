# Deployment Guide

## Local Development

All Python templates run locally with:

```bash
pip install -r requirements.txt
streamlit run app.py
```

For Next.js templates:

```bash
npm install
npm run dev
```

## Docker Deployment

```bash
docker build -t agent-template .
docker run -p 8501:8501 -e OPENAI_API_KEY=$OPENAI_API_KEY agent-template
```

## Cloud Deployment

### Railway / Render

Use the included `railway.json` or `render.yaml` for generative UI templates.

### Kubernetes

For production deployments, use the included K8s manifests in the `k8s/` directory (available in select templates).

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes* | OpenAI API access |
| `ANTHROPIC_API_KEY` | No | Claude access |
| `GOOGLE_API_KEY` | No | Gemini / ADK access |
| `GITHUB_TOKEN` | No | GitHub MCP server |
| `NOTION_TOKEN` | No | Notion MCP server |

*Required for cloud-hosted models. Local templates use Ollama.
