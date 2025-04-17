from langgraph.prebuilt import ToolNode
from SDKsetup import GOOGLE_API_KEY
from tools import get_data
from botprompt import OrderState, agentBOT_SYSINT, WELCOME_MSG
from langgraph.graph import StateGraph, START, END
from typing import Literal
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import time

# Define the tools and create a "tools" node.
tools = [get_data]  #dataattcahed
tool_node = ToolNode(tools)

# Initialize LLM with settings to prevent retries and handle quota limits
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", 
    google_api_key=GOOGLE_API_KEY,
    max_retries=0,  # Disable retries
    temperature=0.7,
    timeout=30  # Add timeout to prevent hanging
)

# Attach the tools to the model so that it knows what it can call.
llm_with_tools = llm.bind_tools(tools)

def human_node(state: OrderState) -> OrderState:
    """Process the human input that's already in the state."""
    return state

def maybe_exit_human_node(state: OrderState) -> Literal["chatbot", "__end__"]:
    """Route to the chatbot, unless it looks like the user is exiting."""
    if state.get("finished", False):
        return END
    else:
        return "chatbot"

def maybe_route_to_tools(state: OrderState) -> Literal["tools", "human"]:
    """Route between human or tool nodes, depending if a tool call is made."""
    if not (msgs := state.get("messages", [])):
        raise ValueError(f"No messages found when parsing state: {state}")
    
    # Only route based on the last message.
    msg = msgs[-1]
    
    # When the chatbot returns tool_calls, route to the "tools" node.
    if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
        return "tools"
    else:
        return "human"

def chatbot_with_tools(state: OrderState) -> OrderState:
    """The chatbot with tools. A wrapper around the model's own chat interface."""
    defaults = {"order": [], "finished": False}
    
    # Initialize messages list with system message if it's empty
    messages = state.get("messages", [])
    if not messages:
        messages = [SystemMessage(content=agentBOT_SYSINT[1]), AIMessage(content=WELCOME_MSG)]
        return defaults | state | {"messages": messages}
    
    # Process normal messages
    try:
        new_output = llm_with_tools.invoke([SystemMessage(content=agentBOT_SYSINT[1])] + messages)
        return defaults | state | {"messages": [new_output]}
    except Exception as e:
        error_msg = str(e).lower()
        if "quota exceeded" in error_msg or "429" in error_msg:
            error_response = AIMessage(content="⚠️ API quota exceeded. Please wait a minute before trying again. For more information about quota limits, visit: https://ai.google.dev/gemini-api/docs/rate-limits")
            state["finished"] = True  # This will make the chat exit gracefully
        else:
            error_response = AIMessage(content=f"An error occurred: {str(e)}")
        return defaults | state | {"messages": [error_response]}

graph_builder = StateGraph(OrderState)

# Add the nodes, including the new tool_node.
graph_builder.add_node("chatbot", chatbot_with_tools)
graph_builder.add_node("human", human_node)
graph_builder.add_node("tools", tool_node)

# Chatbot may go to tools, or human.
graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
# Human may go back to chatbot, or exit.
graph_builder.add_conditional_edges("human", maybe_exit_human_node)

# Tools always route back to chat afterwards.
graph_builder.add_edge("tools", "chatbot")

graph_builder.add_edge(START, "chatbot")
graph_with_menu = graph_builder.compile()