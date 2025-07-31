import os

from a2a.types import (
    AgentCapabilities,
    Message,
    TextPart,
)
from beeai_sdk.server import Server
from beeai_sdk.server.context import Context
from beeai_sdk.a2a.extensions import AgentDetail

server = Server()

SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

@server.agent(
    default_input_modes=SUPPORTED_CONTENT_TYPES,
    default_output_modes=SUPPORTED_CONTENT_TYPES,
    details=AgentDetail(ui_type="chat"),
    capabilities=AgentCapabilities(
        streaming=True,
    )
)
async def example_agent(input: Message, context: Context):
    """Polite agent that greets the user"""
    hello_template: str = os.getenv("HELLO_TEMPLATE", "Ciao %s!")
    yield TextPart(text=hello_template % str(input.parts[0].content))


def run():
    server.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    run()
