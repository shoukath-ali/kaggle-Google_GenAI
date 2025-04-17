from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages


class OrderState(TypedDict):
    """State representing the customer's analysis conversation."""

    # The chat conversation. This preserves the conversation history
    # between nodes. The `add_messages` annotation indicates to LangGraph
    # that state is updated by appending returned messages, not replacing
    # them.
    messages: Annotated[list, add_messages]

    # The users in-progress analysis.
    analysis: list[str]
    finished: bool


# The system instruction defines how the chatbot is expected to behave and includes
# rules for when to call different functions, as well as rules for the conversation, such
# as tone and what is permitted for discussion.
agentBOT_SYSINT = (
    "system",  # 'system' indicates the message is a system instruction.
    "You are an analyzer bot. A human will talk to you about the "
    "Ask for the requirement"
    "Fetch the data you have and the data asked"
    "provide accurate information, if no data say no data"
    "If asked analysis perform analysis for curating the available data"
    "Make sure the user is satisfied with the answer"
    "if asked for visualisation provide the code refering to the data"
    "\n\n"
    "If any of the tools are unavailable, you can break the fourth wall and tell the user that "
    "they have not implemented them yet and should keep reading to do so.",
)

# This is the message with which the system opens the conversation.
WELCOME_MSG = "Welcome to the Analysisbot. Type `q` to quit. How can I help you today?"