import os
from typing import Annotated, Any
import httpx
from textwrap import dedent
from pydantic import BaseModel, Field

from a2a.types import AgentSkill, Message

from beeai_framework.adapters.openai import OpenAIChatModel
from beeai_framework.backend.types import ChatModelParameters
from beeai_framework.agents.requirement import RequirementAgent
from beeai_framework.agents.requirement.events import RequirementAgentFinalAnswerEvent
from beeai_framework.tools import Tool, ToolRunOptions, JSONToolOutput
from beeai_framework.context import RunContext as BeeRunContext
from beeai_framework.emitter import Emitter

from agentstack_sdk.server.context import RunContext
from agentstack_sdk.server.store.platform_context_store import PlatformContextStore
from agentstack_sdk.a2a.types import AgentMessage
from agentstack_sdk.a2a.extensions import (
    AgentDetail, AgentDetailTool, 
    CitationExtensionServer, CitationExtensionSpec, 
    TrajectoryExtensionServer, TrajectoryExtensionSpec, 
    LLMServiceExtensionServer, LLMServiceExtensionSpec
)
from agentstack_sdk.a2a.extensions.auth.secrets import (
    SecretDemand,
    SecretsExtensionServer,
    SecretsExtensionSpec,
    SecretsServiceExtensionParams,
)
from agentstack_sdk.server import Server
from .streaming_citation_parser import StreamingCitationParser

server = Server()


class SerperSearchToolInput(BaseModel):
    query: str = Field(description="Search query to find information")


class SerperSearchTool(Tool[SerperSearchToolInput, ToolRunOptions, JSONToolOutput]):
    name = "serper_search"
    description = "Search Google using Serper API for current information"
    input_schema = SerperSearchToolInput
    
    def __init__(self, api_key: str, options: dict[str, Any] | None = None):
        self.api_key = api_key
        super().__init__(options)
    
    def _create_emitter(self) -> Emitter:
        return Emitter.root().child(namespace=["tool", "serper"], creator=self)
    
    async def _run(self, input: SerperSearchToolInput, options: ToolRunOptions | None, context: BeeRunContext) -> JSONToolOutput:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json={"q": input.query, "num": 8},
                timeout=15.0
            )
            response.raise_for_status()
            return JSONToolOutput(response.json())


@server.agent(
    name="Serper Search Agent",
    detail=AgentDetail(
        interaction_mode="multi-turn",
        user_greeting="Hi! I'm a search agent powered by Serper API and BeeAI Framework. Ask me anything and I'll intelligently search the web for you.",
        version="1.0.0",
        tools=[
            AgentDetailTool(
                name="Serper Search", 
                description="Intelligent web search powered by Google via Serper API. Automatically extracts optimal search terms from conversational queries."
            )
        ],
        framework="BeeAI Framework",
        author={
            "name": "Jenna Winkler"
        },
        source_code_url="https://github.com/jenna-winkler/serper-search-agent"
    ),
    skills=[
        AgentSkill(
            id="serper-search-agent",
            name="Serper Search Agent",
            description=dedent(
                """\
                An intelligent search agent that uses RequirementAgent from BeeAI Framework to process natural language queries 
                and execute web searches via Serper API. The agent automatically extracts optimal search terms from conversational 
                input and demonstrates runtime secrets functionality with API key management.
                """
            ),
            tags=["Search", "Web", "Research"],
            examples=[
                "What are the latest developments in quantum computing?",
                "Tell me about recent AI breakthroughs in 2025",
                "What's happening with electric vehicle technology?",
            ]
        )
    ],
)
async def serper_search_agent(
    input: Message,
    context: RunContext,
    secrets: Annotated[
        SecretsExtensionServer,
        SecretsExtensionSpec.single_demand(key="SERPER_API_KEY", name="Serper API Key", description="Serper API key"),
    ],
    trajectory: Annotated[TrajectoryExtensionServer, TrajectoryExtensionSpec()],
    citation: Annotated[CitationExtensionServer, CitationExtensionSpec()],
    llm: Annotated[
        LLMServiceExtensionServer, 
        LLMServiceExtensionSpec.single_demand(
            suggested=("ibm-granite/granite-4.0-h-small",)
        )
    ],
):
    """Agent demonstrating runtime secrets with Serper API and streaming citations"""
    
    await context.store(input)

    user_query = ""
    for part in input.parts:
        if part.root.kind == "text":
            user_query = part.root.text
            break
    
    if not user_query:
        yield "Please provide a search query."
        return
    
    yield trajectory.trajectory_metadata(title="User Query", content=f"Received: '{user_query}'")
    
    api_key = None
    if secrets and secrets.data and secrets.data.secret_fulfillments:
        api_key = secrets.data.secret_fulfillments['SERPER_API_KEY'].secret
        yield trajectory.trajectory_metadata(title="API Key", content="Using pre-configured Serper API key")
    else:
        yield trajectory.trajectory_metadata(title="API Key", content="Requesting Serper API key from user")
        runtime_provided_secrets = await secrets.request_secrets(
            params=SecretsServiceExtensionParams(
                secret_demands={"SERPER_API_KEY": SecretDemand(description="Serper API key", name="Serper API Key")}
            )
        )
        if runtime_provided_secrets and runtime_provided_secrets.secret_fulfillments:
            api_key = runtime_provided_secrets.secret_fulfillments['SERPER_API_KEY'].secret
            yield trajectory.trajectory_metadata(title="API Key", content="Received API key from user")
    
    if not api_key:
        yield "No API key provided"
        return
    
    yield trajectory.trajectory_metadata(title="Agent Setup", content="Initializing RequirementAgent with Serper search")
    
    try:
        if not llm or not llm.data:
            raise ValueError("LLM service extension is required but not available")

        llm_config = llm.data.llm_fulfillments.get("default")
        if not llm_config:
            raise ValueError("No LLM fulfillment available")

        llm_model = OpenAIChatModel(
            model_id=llm_config.api_model,
            base_url=llm_config.api_base,
            api_key=llm_config.api_key,
            parameters=ChatModelParameters(
                temperature=0.0,
                stream=True  # Enable streaming
            ),
            tool_choice_support=set()
        )
        
        agent = RequirementAgent(
            llm=llm_model,
            tools=[SerperSearchTool(api_key)],
            instructions=dedent("""\
                Use serper_search to find information. Extract key search terms from the user's query.
                
                When providing your final answer, ALWAYS cite sources using markdown format: [description](URL).
                
                Examples:
                - [Latest quantum computing breakthrough](https://example.com/quantum)
                - [IBM's new AI announcement](https://example.com/ibm-ai)
                
                Make sure to include citations for all information you gather from search results.
            """)
        )
        
        search_results = None
        search_count = 0
        response_text = ""
        citation_parser = StreamingCitationParser()
        
        def handle_final_answer_stream(data: RequirementAgentFinalAnswerEvent, meta):
            nonlocal response_text
            if data.delta:
                response_text += data.delta
        
        async for event, meta in agent.run(user_query).on("final_answer", handle_final_answer_stream):
            # Handle streaming final answer
            if meta.name == "final_answer":
                if isinstance(event, RequirementAgentFinalAnswerEvent) and event.delta:
                    clean_text, new_citations = citation_parser.process_chunk(event.delta)
                    if clean_text:
                        yield clean_text
                    if new_citations:
                        yield citation.citation_metadata(citations=new_citations)
                continue
            
            # Handle tool execution
            if meta.name == "success" and event.state.steps:
                step = event.state.steps[-1]
                
                if step.tool and step.tool.name == "serper_search":
                    search_count += 1
                    search_query = step.input.get("query", "Unknown")
                    
                    yield trajectory.trajectory_metadata(
                        title=f"Search #{search_count}", 
                        content=f"Query: '{search_query}'"
                    )
                    
                    search_results = step.output.result
                    
                    if search_results:
                        num_results = len(search_results.get('organic', []))
                        yield trajectory.trajectory_metadata(
                            title=f"Results #{search_count}", 
                            content=f"Found {num_results} results"
                        )
        
        # Finalize any remaining text
        if final_text := citation_parser.finalize():
            yield final_text
        
        # Store message with citations
        if citation_parser.citations:
            yield trajectory.trajectory_metadata(
                title="Complete", 
                content=f"Performed {search_count} search(es) with {len(citation_parser.citations)} citation(s)"
            )
        
        response_message = AgentMessage(
            text=response_text,
            metadata=(citation.citation_metadata(citations=citation_parser.citations) if citation_parser.citations else None)
        )
        await context.store(response_message)
    
    except Exception as e:
        yield trajectory.trajectory_metadata(title="Error", content=f"Exception: {str(e)}")
        error_msg = f"Error: {str(e)}"
        yield error_msg
        await context.store(AgentMessage(text=error_msg))


def run():
    server.run(
        host=os.getenv("HOST", "127.0.0.1"), 
        port=int(os.getenv("PORT", 8000)),
        context_store=PlatformContextStore()
    )


if __name__ == "__main__":
    run()
