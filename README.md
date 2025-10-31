# Serper Search Agent

This project shows how Agent Stack’s runtime secrets work — letting agents securely request API keys or credentials at runtime instead of needing them pre-configured.

---

## What It Does

**Runtime Secrets**

* Prompts you for your Serper API key the first time you use it
* Uses the platform’s secure credential UI
* Supports both pre-set and on-demand secrets

**Smart Search**

* Turns natural questions into search queries automatically
* Example: “tell me about the sky” → “facts about the sky”
* Refines searches when needed

**Custom Serper Tool**

* Async HTTP with error handling
* Proper schemas and BeeAI Framework patterns

**Citations & Logs**

* Clickable sources with metadata for highlighting in the UI
* Query traces like `Query: 'facts about the sky'`
* Full execution visibility

---

## Run It

**Requirements**

* [Agent Stack](https://docs.beeai.dev/introduction/quickstart) running locally
* [Serper API key](https://serper.dev)

### Using `uv` (recommended)

This project uses a `pyproject.toml` — not a `requirements.txt` — so `uv` is the easiest way to install dependencies.

```bash
git clone https://github.com/jenna-winkler/serper-search-agent
cd serper-search-agent

uv venv
source .venv/bin/activate
uv sync
uv run server
```

Then open [http://localhost:8334](http://localhost:8334).

You’ll be prompted for your API key — that’s the runtime secrets feature in action.

---

## Code Highlights

* `SecretsExtensionServer` — runtime credential flow
* `RequirementAgent` — query extraction
* `SerperSearchTool` — custom tool
* `CitationExtensionServer` — source attribution
* `TrajectoryExtensionServer` — execution logs
