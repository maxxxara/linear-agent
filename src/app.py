"""
Linear Agent - A Streamlit application for interacting with Linear via LangGraph.

NOTE: This file only contains the Streamlit UI implementation.
For the LangGraph implementation, please see src/graph/graph.py
"""
import asyncio
import os
import sys
import time
from pathlib import Path

import streamlit as st

# Add parent directory to path to import modules correctly
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

# Import the graph from graph.py
from src.graph.graph import graph
from src.graph.utils.helpers import convert_messages_to_langchain_format

# Constants
INITIAL_MESSAGE = "Hey there! I'm Lino, your project manager buddy. Ready to help with tasks, track issues, or just chat about the latest tech drama. What can I help you with today?"
APP_TITLE = "Linear Agent"
APP_DESCRIPTION = "Chat with your LangGraph assistant"
APP_ICON = "🔷"
FOOTER_TEXT = "Built with Streamlit and LangGraph"

# Enable hot-reloading for development
os.environ['STREAMLIT_SERVER_RUN_ON_SAVE'] = 'true'


def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
    )


def render_header():
    """Render the application header."""
    st.title(APP_TITLE)
    st.caption(APP_DESCRIPTION)


def render_task_card(task_name, description, task_id):
    """
    Render a task card with Linear styling.
    
    Args:
        task_name (str): The name of the task
        description (str): The task description
        task_id (str): The Linear task ID
    """
    html = f"""
    <style>
    .task-card {{
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        background-color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}
    .task-header {{
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }}
    .task-title {{
        font-weight: 600;
        color: #111111;
        font-size: 16px;
    }}
    .task-description {{
        color: #555555;
        font-size: 14px;
        line-height: 1.5;
        margin-bottom: 16px;
    }}
    .task-button {{
        display: inline-block;
        background-color: #5E6AD2;
        color: white!important;
        padding: 8px 16px;
        text-decoration: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s ease;
    }}
    .task-button:hover {{
        background-color: #4954C3;
        box-shadow: 0 2px 8px rgba(94, 106, 210, 0.3);
    }}
    </style>
    
    <div class="task-card">
        <div class="task-header">
            <div class="task-title">{task_name}</div>
        </div>
        <div class="task-description">{description}</div>
        <a href="https://linear.app/issue/{task_id}" class="task-button" target="_blank">View in Linear</a>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def initialize_chat_history():
    """Initialize the chat history if it doesn't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": INITIAL_MESSAGE}]


def display_chat_history():
    """Display all messages from the chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


async def run_graph_async(messages):
    """
    Run the LangGraph with the given messages.
    
    Args:
        messages (list): List of message dictionaries
        
    Returns:
        str: The response content
    """
    try:
        # Run the graph
        result = await graph.ainvoke({"messages": convert_messages_to_langchain_format(messages)})
        
        # Debug output - only in development mode
        if os.getenv("DEBUG", "false").lower() == "true":
            with st.expander("Debug Information"):
                st.code(result, language="python")
        
        # Get the response message
        response = result.get("messages", None)
        
        # Check if we have params with task_name in the message object
        if response and hasattr(response, 'params') and response.params and 'task_name' in response.params:
            task_name = response.params['task_name']
            description = response.params.get('description', '')
            task_id = response.params.get('task_id', '')
            
            # Create a fancy task card
            render_task_card(task_name, description, task_id)
        
        if response and hasattr(response, 'content') and response.content:
            response_content = response.content
        else:
            response_content = "No response from the graph."
        
        return response_content
    except Exception as e:
        st.error(f"Error executing graph: {str(e)}")
        return f"I encountered an error while processing your request."


def process_user_input(prompt):
    """
    Process user input and generate a response.
    
    Args:
        prompt (str): The user's input message
    """
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process with the LangGraph and display assistant response
    with st.chat_message("assistant"):
        # Create placeholder for streaming response
        message_placeholder = st.empty()
        message_placeholder.markdown("▌")
        
        # Run the async function
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(run_graph_async(st.session_state.messages))
            loop.close()
            
            # Display the response with a typing effect
            full_response = ""
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.01)  # Faster typing effect
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            message_placeholder.markdown("Sorry, I encountered an error. Please try again.")


def render_footer():
    """Render the application footer."""
    st.divider()
    st.caption(FOOTER_TEXT)


def main():
    """Main application entry point."""
    # Setup page configuration
    setup_page_config()
    
    # Render header
    render_header()
    
    # Initialize and display chat history
    initialize_chat_history()
    display_chat_history()
    
    # Process user input if provided
    if prompt := st.chat_input("Type your message here..."):
        process_user_input(prompt)
    
    # Render footer
    render_footer()


if __name__ == "__main__":
    main() 