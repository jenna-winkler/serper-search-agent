import os

from a2a.types import (
    AgentCapabilities,
    Message,
)
from a2a.utils.message import get_message_text
from beeai_sdk.server import Server
from beeai_sdk.server.context import Context
from beeai_sdk.a2a.types import AgentMessage
from beeai_sdk.a2a.extensions import AgentDetail

server = Server()

SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

@server.agent(
    default_input_modes=SUPPORTED_CONTENT_TYPES,
    default_output_modes=SUPPORTED_CONTENT_TYPES,
    detail=AgentDetail(ui_type="chat"),
    capabilities=AgentCapabilities(
        streaming=True,
    )
)
async def example_agent(input: Message, context: Context):
    """Polite agent that greets the user"""
    hello_template: str = os.getenv("HELLO_TEMPLATE", "Ciao %s!")
    yield AgentMessage(text=hello_template % get_message_text(input))

def run():
    server.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))


if __name__ == "__main__":
    run()
