# Serper Search Agent

This project demonstrates Agent Stack's runtime secrets feature - how agents can securely request API keys and credentials at runtime instead of requiring pre-configuration.

## What It Does

**Runtime Secrets (Main Feature)**
- Agent asks for your Serper API key the first time you use it
- Secure credential prompt through the platform UI
- Works with both pre-configured secrets and on-demand requests

**Smart Search with RequirementAgent**
- Converts conversational questions into search queries automatically
- "tell me about the sky" becomes "facts about the sky"
- Refines searches on its own if needed

**Custom Serper Tool**
- Production-ready implementation with proper schemas
- Async HTTP with error handling
- Follows BeeAI Framework patterns

**Citations & Transparency**
- Clickable sources with position metadata for UI highlighting
- Trajectory logs show extracted queries: `"Query: 'facts about the sky'"`
- Full execution visibility for debugging

## Run It

**Prerequisites:**
- [Agent Stack](https://docs.beeai.dev/introduction/quickstart) running locally
- [Serper API key](https://serper.dev)

```bash
pip install beeai-framework beeai-sdk httpx pydantic
python serper_agent.py
```

Open `http://localhost:8334` and try asking something. The agent will prompt you for your API key - that's the runtime secrets feature in action.

## Code Highlights

- `SecretsExtensionServer` - Handles the runtime credential flow
- `RequirementAgent` - Powers intelligent query extraction
- `SerperSearchTool` - Custom tool
- `CitationExtensionServer` - Structured source attribution
- `TrajectoryExtensionServer` - Execution logging

This is a reference implementation for building agents that need secure credential management.