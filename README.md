<div align="center">

# 🤖 Agents Foundry

**Autonomous agent systems for real workloads.**

100+ production-ready agent templates — from single-task assistants to multi-agent squads, voice interfaces, tool bridges, and generative frontends. Every template is a complete runnable system with clear architecture, not a framework wrapper.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript)](https://typescriptlang.org)

</div>

---

## What This Is

Agents Foundry is a collection of **autonomous agent systems built as standalone modules**. Each template is a complete working agent — not a framework demo, not a toy example, not a wrapper around someone else's abstraction.

Every project includes:
- Working code with clear component boundaries
- Requirements or package manifest with working versions
- A minimal README explaining the architecture
- No hidden orchestration magic — you see every decision

## Architecture Philosophy

We believe agent systems should be **understandable before they are autonomous**. Each template follows these principles:

1. **Explicit control flow** — every agent decision is traceable
2. **Provider-agnostic** — swap models, tools, and frameworks with one config change
3. **Composable** — agents from different templates can be combined into larger systems
4. **Testable** — every template includes a test or validation script

## Quick Start

```bash
# Clone and run any template in under 60 seconds
git clone https://github.com/pisigmac/Agent-Foundry.git
cd Agent-Foundry/single-agents/itinerary-planner
pip install -r requirements.txt
streamlit run itinerary_planner.py
```

## Categories

### Single Agents (34)
One assistant, one task, one clear output. Perfect for understanding agent fundamentals.

| Template | Task | Stack |
|---|---|---|
| `itinerary-planner` | Travel planning | Streamlit + Agno |
| `data-insight-analyst` | CSV analysis | Streamlit + Pandas |
| `medical-image-analyzer` | Medical imaging | Vision models |
| `meme-creator-browser` | Browser automation | Browser-use |
| `music-composition-assistant` | Music generation | Audio models |
| `step-by-step-reasoner` | Chain-of-thought reasoning | Any LLM |
| `startup-intelligence-scout` | Startup trend tracking | Web search |
| `content-podcast-converter` | Blog → podcast | TTS + summarization |
| `emotional-support-companion` | Conversational support | Any LLM |
| `chart-generation-assistant` | Auto-visualization | Plotly + Streamlit |
| `insurance-policy-advisor` | Insurance recommendations | Structured output |
| `ensemble-consensus-engine` | Multi-model voting | Mixture of agents |
| `vision-text-reasoner` | Multimodal reasoning | Vision + text |
| `deep-research-assistant` | Web research | Firecrawl + LLM |
| `structured-web-extractor` | Web scraping | Structured extraction |
| `finance-market-analyzer` | Financial analysis | xAI models |
| `business-strategy-advisor` | Consulting | Structured output |
| `support-ticket-resolver` | Customer support | Ticket resolution |
| `web-research-orchestrator` | Deep research | Multi-source |
| `outreach-automation-engine` | Email outreach | GTM automation |
| `fraud-detection-analyst` | Fraud investigation | Pattern detection |
| `wellness-coach` | Health coaching | Health data |
| `portfolio-optimizer` | Investment analysis | Portfolio models |
| `news-writing-assistant` | Journalism | News generation |
| `meeting-intelligence` | Meeting analysis | Transcription + action items |
| `film-production-planner` | Movie planning | Production pipeline |
| `budget-tracker-advisor` | Personal finance | Budget analysis |
| `meal-planner-creator` | Meal planning | Recipe generation |
| `startup-signal-detector` | Startup signals | Intelligence gathering |
| `system-design-assistant` | System architecture | Design assistance |
| `earnings-analyzer` | Earnings calls | Financial analysis |
| `gemini-research-pipeline` | Gemini research | Gemini API |
| `desktop-automation-controller` | Windows automation | Desktop control |
| `tarot-reading-assistant` | Tarot interpretation | Conversational |
| `github-conversation-agent` | GitHub chat | Repo Q&A |
| `gmail-conversation-agent` | Gmail chat | Email Q&A |
| `resume-job-matcher` | Resume matching | Job matching |
| `database-administrator` | SQL optimization | Streamlit + Agno |
| `security-vulnerability-scanner` | Security scanning | Multi-language |
| `devops-pipeline-monitor` | CI/CD monitoring | Pipeline logs |
| `log-anomaly-detector` | Log analysis | Pattern detection |
| `accessibility-auditor` | WCAG compliance | HTML/CSS audit |
| `data-quality-validator` | Data profiling | Pandas + numpy |
| `cost-optimizer` | Cloud cost analysis | Billing data |
| `incident-response-coordinator` | On-call triage | Runbook execution |

### Swarm Coordination (16)
Multiple agents working together with explicit handoffs and shared state.

| Template | Squad Size | Coordination |
|---|---|---|
| `agent-team-framework` | 3-5 | Generic team pattern |
| `air-quality-research-team` | 4 | Environmental data |
| `domain-research-squad` | 3 | Deep domain research |
| `gtm-outreach-squad` | 5 | Go-to-market automation |
| `wealth-advisory-swarm` | 6 | Financial coaching |
| `home-redesign-vision-team` | 4 | Vision + design |
| `mental-health-support-team` | 3 | Wellness support |
| `negotiation-practice-arena` | 2 | AI vs AI practice |
| `news-podcast-production-team` | 4 | Content pipeline |
| `self-improving-collective` | 3 | Auto-optimization |
| `public-speaking-coach-team` | 3 | Speech training |
| `developer-analytics-squad` | 4 | Dev productivity |
| `collaborative-research-team` | 5 | Multi-researcher |
| `trust-verification-network` | 3 | Trust layer |
| `launch-intelligence-team` | 4 | Product launch |
| `gated-trust-collective` | 3 | Gated execution |

### Autonomous Systems (3)
Agents that operate without human intervention.

| Template | Environment | Game |
|---|---|---|
| `3d-game-navigator` | 3D PyGame | Navigation |
| `chess-strategist` | Chess | Strategy |
| `tic-tac-toe-solver` | Tic-tac-toe | Perfect play |

### Tool Bridges (6)
Model Context Protocol integrations connecting agents to external tools.

| Template | Tools | Protocol |
|---|---|---|
| `travel-mcp-collective` | Calendar + Maps + Search | MCP |
| `browser-automation-bridge` | Browser | MCP |
| `github-repository-bridge` | GitHub | MCP |
| `notion-workspace-bridge` | Notion | MCP |
| `multi-service-router` | GitHub + Perplexity + Calendar + Gmail | MCP |
| `intelligent-mcp-router` | Dynamic routing | MCP |

### Voice Interfaces (4)
Real-time voice interaction with agents.

| Template | Voice Stack | Use Case |
|---|---|---|
| `claims-processing-live-team` | Gemini Live | Insurance claims |
| `voice-support-agent` | OpenAI Realtime | Customer support |
| `location-audio-guide` | TTS + Location | Audio tours |
| `voice-enabled-retrieval` | Voice + RAG | Voice Q&A |

### Generative Interfaces (7)
Next.js + CopilotKit agents that generate user interfaces from natural language.

| Template | Generates | Stack |
|---|---|---|
| `dashboard-canvas-builder` | Dashboards | Next.js + CopilotKit |
| `research-ui-generator` | Research UIs | Next.js + CopilotKit |
| `finance-coach-interface` | Financial UIs | Next.js + CopilotKit |
| `app-builder-from-nl` | Full applications | Next.js + MCP |
| `component-factory` | shadcn/ui components | Next.js + CopilotKit |
| `ui-starter-template` | Starter template | Next.js + CopilotKit |
| `mcp-ui-showcase` | MCP-powered UIs | Next.js + MCP |

### Persistent Agents (1)
Agents that run on schedules without human intervention.

| Template | Schedule | Output |
|---|---|---|
| `daily-tech-brief-scheduler` | Daily | HN tech brief |

### Agent Capabilities (10)
Reusable capabilities, skills, and learning paths for agent systems.

| Template | Type | What It Does |
|---|---|---|
| `meta-loop-orchestrator` | Skill | Advisor → Orchestrator → Worker pattern |
| `evaluation-framework` | Skill | Agent evaluation harness |
| `project-revival-analyzer` | Skill | Find and revive dead projects |
| `auto-optimization-skill` | Skill | Self-improving agent capabilities |
| `memory-patterns-collection` | Tutorial | 6 memory patterns for agents |
| `model-finetuning-guides` | Tutorial | Gemma 3 + Llama 3.2 fine-tuning |
| `context-optimization-suite` | Tool | Context + token optimization |
| `video-moment-detector` | Tool | Find moments in videos |
| `thought-process-chatbot` | Tool | Visualize agent reasoning |
| `critique-improvement-loop` | Tool | Self-improving critique |
| `cursor-ide-experiments` | Tool | Cursor IDE experiments |

### Learning Paths (2)
Step-by-step workshops for building with agent frameworks.

| Course | Framework | Lessons |
|---|---|---|
| `google-adk-workshop` | Google ADK | 9 lessons: starter → multi-agent |
| `openai-agents-workshop` | OpenAI Agents SDK | 11 lessons: agents → voice → observability |

## Common Stack

- **Agent frameworks:** Agno, Google ADK, OpenAI Agents SDK
- **UI:** Streamlit (Python), Next.js + CopilotKit (Generative UI)
- **API:** FastAPI, Uvicorn
- **MCP:** Model Context Protocol with npx-based servers
- **Voice:** Gemini Live, OpenAI Realtime API
- **Models:** GPT-4o, Claude, Gemini, Llama, Qwen, xAI
- **Memory:** SQLite, LanceDB, session-based

## Roadmap

See our [Agent Templates Roadmap](AGENT_TEMPLATES_ROADMAP.md) for a complete list of all planned, proposed, and under-consideration agent templates. You can use it to track what is currently being built or pick up an unassigned template to contribute!

## Testing

Every template includes a validation script. Run it after setup:

```bash
python test.py  # or check the README in each project
```

## Contributing

This is a living collection. If you have an agent system that works in production, open a PR with:
1. Working code in a new directory
2. `requirements.txt` or `package.json` with working versions
3. A minimal README explaining the architecture
4. A test or validation script

## License

MIT License. Use it, modify it, ship it, sell it.

---

<div align="center">

Built for engineers who need agents that work, not frameworks that promise.

</div>
