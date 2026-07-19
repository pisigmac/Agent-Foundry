# Architecture Decision Records

## ADR-001: Agent Framework Selection

**Status:** Accepted
**Date:** 2026-07-14

### Context

Multiple agent frameworks exist: Agno, Google ADK, OpenAI Agents SDK, LangChain, CrewAI.

### Decision

Use **Agno** for single-agent templates. Use **Google ADK** for multi-agent squads. Use **OpenAI Agents SDK** for voice and real-time templates.

### Rationale

- Agno has the simplest API for single agents
- ADK has the best multi-agent orchestration
- OpenAI SDK has the best voice/realtime support

## ADR-002: Memory Strategy

**Status:** Accepted
**Date:** 2026-07-14

### Context

Agents need memory to maintain context across sessions.

### Decision

Use **SQLite** for local memory. Use **LanceDB** for vector memory. Use **Redis** only for production deployments.

### Rationale

- SQLite requires zero infrastructure
- LanceDB handles both structured and vector memory
- Redis is overkill for most templates

## ADR-003: Tool Integration Protocol

**Status:** Accepted
**Date:** 2026-07-14

### Context

Agents need to call external tools: APIs, databases, browsers, etc.

### Decision

Use **MCP (Model Context Protocol)** as the primary tool integration standard. Use **native function calling** as a fallback.

### Rationale

- MCP is becoming the industry standard
- Native function calling is simpler for single tools
- MCP enables tool composition across templates
