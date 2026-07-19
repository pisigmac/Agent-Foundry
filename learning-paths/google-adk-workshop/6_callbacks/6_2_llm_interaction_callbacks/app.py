#!/usr/bin/env python3
"""
    Coordinate the workflow between components.
    """

import streamlit as st
import sys
import os
import asyncio
from assistant import execute_assistant

# Page configuration
st.set_page_config(
    page_title="LLM Interaction Callbacks",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("🤖 LLM Interaction Callbacks Demo")
st.markdown("""
This demo shows how to monitor LLM requests and responses using callbacks.
Watch the console output to see detailed LLM interaction tracking!
""")

# Sidebar with information
with st.sidebar:
    st.header("📊 LLM Monitoring")
    st.markdown("""
    **Request Callback**: Triggered when LLM request is sent
    - Logs model name and prompt
    - Records request timestamp
    - Tracks prompt length
    
    **Response Callback**: Triggered when LLM response is received
    - Calculates response duration
    - Tracks token usage
    - Estimates API costs
    """)

# Main chat interface
st.header("💬 Chat with LLM Monitor")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me something..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("🤖 LLM is processing..."):
            response = asyncio.run(execute_assistant(prompt))
            st.markdown(response)
    
    # Add assistant response to chat
    st.session_state.messages.append({"role": "assistant", "content": response})

# Quick test buttons
st.markdown("---")
st.header("⚡ Quick Tests")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔬 Science Test"):
        with st.chat_message("user"):
            st.markdown("Explain quantum computing in simple terms")
        with st.chat_message("assistant"):
            with st.spinner("🤖 LLM is processing..."):
                response = asyncio.run(execute_assistant("Explain quantum computing in simple terms"))
                st.markdown(response)

with col2:
    if st.button("📝 Poetry Test"):
        with st.chat_message("user"):
            st.markdown("Write a short poem about AI")
        with st.chat_message("assistant"):
            with st.spinner("🤖 LLM is processing..."):
                response = asyncio.run(execute_assistant("Write a short poem about AI"))
                st.markdown(response)

with col3:
    if st.button("🌍 Environment Test"):
        with st.chat_message("user"):
            st.markdown("What are the benefits of renewable energy?")
        with st.chat_message("assistant"):
            with st.spinner("🤖 LLM is processing..."):
                response = asyncio.run(execute_assistant("What are the benefits of renewable energy?"))
                st.markdown(response)

# Clear chat button
if st.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Information about callbacks
st.markdown("---")
st.header("📋 LLM Callback Output")
st.markdown("""
**Check your console/terminal** to see the LLM interaction output:

```
🤖 LLM Request to gemini-3-flash-preview
⏰ Request time: 10:30:15
📋 Assistant: llm_monitor_agent

📝 LLM Response from gemini-3-flash-preview
⏱️ Duration: 1.45s
🔢 Tokens: 156
💰 Estimated cost: $0.0004
```
""")

# Footer
st.markdown("---")
st.markdown("*Watch the console output to see LLM interaction callbacks in action!*") 