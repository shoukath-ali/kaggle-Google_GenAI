import streamlit as st
from pprint import pprint
import time
from chat import graph_with_menu
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from botprompt import WELCOME_MSG, agentBOT_SYSINT

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide"
)

# App title
st.title("AI Chatbot")

# Initialize configuration
config = {"recursion_limit": 100}

# Initialize session state for chat history and loading state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append(SystemMessage(content=agentBOT_SYSINT[1]))
    st.session_state.messages.append(AIMessage(content=WELCOME_MSG))

if "loading" not in st.session_state:
    st.session_state.loading = False

# Display chat history
for message in st.session_state.messages:
    if isinstance(message, (AIMessage, HumanMessage)):
        role = "assistant" if isinstance(message, AIMessage) else "user"
        with st.chat_message(role):
            content = message.content
            # Handle error messages with appropriate styling
            if isinstance(message, AIMessage) and any(x in content.lower() for x in ["quota exceeded", "⚠️", "error"]):
                st.warning(content)
                if "quota exceeded" in content.lower():
                    st.info("💡 Please wait a minute before sending your next message.")
            else:
                st.markdown(content)

# Chat input and message handling
if prompt := st.chat_input("Type your message here..."):
    # Add user message to state and display it
    user_message = HumanMessage(content=prompt)
    st.session_state.messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response from chatbot
    with st.spinner("🤖 Thinking..."):
        try:
            st.session_state.loading = True
            
            # Get response using the full message history
            state = graph_with_menu.invoke({"messages": st.session_state.messages}, config)
            
            if "messages" in state and state["messages"]:
                # Extract the last message from the response
                bot_message = state["messages"][-1]
                response = bot_message.content if hasattr(bot_message, 'content') else str(bot_message)
                
                # Display assistant response
                with st.chat_message("assistant"):
                    if any(x in response.lower() for x in ["quota exceeded", "⚠️", "error"]):
                        st.warning(response)
                        if "quota exceeded" in response.lower():
                            st.info("💡 Please wait a minute before sending your next message.")
                            st.stop()  # Stop execution to prevent further API calls
                    else:
                        message_placeholder = st.empty()
                        full_response = ""
                        for chunk in response.split():
                            full_response += chunk + " "
                            message_placeholder.markdown(full_response + "▌")
                            time.sleep(0.02)
                        message_placeholder.markdown(full_response)
                
                # Add assistant response to chat history
                st.session_state.messages.append(AIMessage(content=response))
                
                # Handle exit commands or finished state
                if prompt.lower() in {"q", "quit", "exit", "goodbye"} or state.get("finished", False):
                    st.info("Chat session ended. Please refresh the page to start a new chat.")
                    st.stop()
                
        except Exception as e:
            error_msg = str(e)
            if any(x in error_msg.lower() for x in ["quota exceeded", "timeout", "429"]):
                error_msg = "⚠️ API quota exceeded or request timed out. Please wait a minute before trying again."
            st.error(error_msg)
        finally:
            st.session_state.loading = False
