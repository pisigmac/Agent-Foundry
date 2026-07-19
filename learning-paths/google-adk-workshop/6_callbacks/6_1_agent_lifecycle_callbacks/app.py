#!/usr/bin/env python3
"""
    Handle the core logic for this module.
    """

import streamlit as st
import asyncio
from assistant import llm_agent_with_callbacks, runner
from google.genai import types

# Page configuration
st.set_page_config(
    page_title="Assistant Lifecycle Callbacks Demo",
    page_icon="🔄",
    layout="wide"
)

# Title and description
st.title("🔄 Assistant Lifecycle Callbacks Demo")
st.markdown("""
This demo shows how to use `before_agent_callback` and `after_agent_callback` to monitor assistant execution.
Watch the console output to see the callback timing information.
""")

# Sidebar
with st.sidebar:
    st.header("📊 Callback Information")
    st.markdown("""
    **Before Callback:**
    - Records start time
    - Logs assistant execution start
    
    **After Callback:**
    - Calculates execution duration
    - Logs completion time
    """)
    
    st.header("🔧 Technical Details")
    st.markdown("""
    - Uses `InMemoryRunner` for session management
    - Callbacks receive `CallbackContext` with assistant info
    - State is shared between callbacks via session
    """)

# Main chat interface
st.header("💬 Chat with Assistant")

# Define the get_response function
async def get_response(prompt_text: str) -> str:
    """Run assistant with the given prompt"""
    account_id = "demo_user"
    context_id = "demo_session"
    
    # Get the bundled session service
    session_service = runner.session_service
    
    # Get or create session
    session = await session_service.get_session(
        service_name="agent_lifecycle_callback_demo", 
        account_id=account_id, 
        context_id=context_id
    )
    if not session:
        session = await session_service.create_session(
            service_name="agent_lifecycle_callback_demo",
            account_id=account_id,
            context_id=context_id
        )
    
    # Create user content
    user_content = types.Content(
        role='user',
        parts=[types.Part(text=prompt_text)]
    )
    
    # Run assistant and get response
    response_text = ""
    async for event in runner.run_async(
        account_id=account_id,
        context_id=context_id,
        new_message=user_content
    ):
        if event.is_final_response() and event.content:
            response_text = event.content.parts[0].text.strip()
            # Don't break - let the loop complete to ensure callbacks run
    
    return response_text

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add assistant response to chat history
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Show loading message
        message_placeholder.markdown("🤔 Thinking...")
        
        # Get response
        response = asyncio.run(get_response(prompt))
        
        # Update placeholder with response
        message_placeholder.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Quick test buttons
st.markdown("---")
st.header("⚡ Quick Tests")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👋 Greeting Test"):
        with st.chat_message("user"):
            st.markdown("Hello, how are you?")
        with st.chat_message("assistant"):
            with st.spinner("🤖 Assistant is processing..."):
                response = asyncio.run(get_response("Hello, how are you?"))
                st.markdown(response)

with col2:
    if st.button("🧮 Math Test"):
        with st.chat_message("user"):
            st.markdown("What's 2 + 2?")
        with st.chat_message("assistant"):
            with st.spinner("🤖 Assistant is processing..."):
                response = asyncio.run(get_response("What's 2 + 2?"))
                st.markdown(response)

with col3:
    if st.button("😄 Joke Test"):
        with st.chat_message("user"):
            st.markdown("Tell me a short joke")
        with st.chat_message("assistant"):
            with st.spinner("🤖 Assistant is processing..."):
                response = asyncio.run(get_response("Tell me a short joke"))
                st.markdown(response)

# Clear chat button
if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Check the console/terminal for callback timing information</p>
</div>
""", unsafe_allow_html=True) 