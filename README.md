# Serper Search Agent

A demonstration of runtime secrets management and intelligent search using BeeAI Framework + SDK.

## What It Showcases

**1. Runtime Secrets (BeeAI SDK)**
- Requests Serper API key at runtime instead of pre-configuration
- Uses `SecretsExtensionServer` to prompt users for credentials
- Handles both pre-configured and dynamic secret provisioning

**2. RequirementAgent Intelligence (BeeAI Framework)**
- Converts natural language ("tell me about the sky") into search queries ("facts about the sky")
- Performs multiple refined searches automatically
- No hard-coded search logic - agent decides when/how to search

**3. Custom Tool Implementation**
- Production-ready `SerperSearchTool` following BeeAI patterns
- Proper input/output schemas with Pydantic
- Async HTTP integration with error handling

**4. Citation Metadata (BeeAI SDK)**
- Structured citations with `start_index`/`end_index` for UI highlighting
- Clickable source attribution in BeeAI Platform
- Proper markdown formatting

**5. Trajectory Logging (BeeAI SDK)**
- Logs extracted search queries: `"Query: 'facts about the sky'"`
- Tracks multiple search attempts
- Full execution transparency

**6. Agent Registration (BeeAI SDK)**
- Rich metadata for platform discoverability
- Multi-turn interaction mode
- Skills and example queries

## Run It

Prerequisites:
- [BeeAI Platform](https://docs.beeai.dev/introduction/quickstart) installed and running
- Serper API key from [https://serper.dev](https://serper.dev)

```bash
pip install beeai-framework beeai-sdk httpx pydantic
python serper_agent.py
```

Access at `http://localhost:8334/` via BeeAI Platform. Provide your Serper API key when prompted.
