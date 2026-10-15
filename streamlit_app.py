import os
from google import genai
from google.genai import types
import streamlit as st

# Load secret key from Streamlit Secrets or environment
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets. Please check your deployment settings.")
    st.stop()

# Initialize the modern Gemini Client
client = genai.Client(api_key=api_key)

# Web App Title and Layout
st.set_page_config(page_title="Miss Linda's F&B Tutor", page_icon="🎓", layout="centered")
st.title("🎓 Miss Linda's Food & Beverage Service Tutor")
st.write("Welcome, student! Test your knowledge on F&B service and get instant feedback from your tutor.")

# ==========================================
# YOUR CUSTOM TUTOR PERSONA:
# ==========================================
TUTOR_SYSTEM_INSTRUCTION = """
You are Miss Linda, an expert and encouraging Food and Beverage Service teacher.
Your style is encouraging, uses real-world restaurant examples, and speaks directly to your students.

Rules you MUST follow:
1. When a student requests a quiz or test on a topic:
   - Give them 5 challenging questions tailored to our food and beverage curriculum.
   - Do NOT provide the answers upfront.
   - Wait for their answers before grading.
2. When the student submits their answers:
   - Evaluate each answer clearly (Mark as Correct or Incorrect).
   - Give constructive feedback and explain the core concept and WHY an answer was wrong.
   - Provide a final score (e.g., 8/10).
   - Sign off with an encouraging note and ask if they want another test or need a topic re-explained.
"""

# Initialize chat session in Streamlit memory with system instruction
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=TUTOR_SYSTEM_INSTRUCTION
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear chat history cache if persona changes so it updates immediately
if "last_persona" not in st.session_state or st.session_state.last_persona != TUTOR_SYSTEM_INSTRUCTION:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=TUTOR_SYSTEM_INSTRUCTION
        )
    )
    st.session_state.last_persona = TUTOR_SYSTEM_INSTRUCTION

# Display prior chat history on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box at the bottom of the web page
if user_input := st.chat_input("Type your message here (e.g., 'Test me on F&B service')..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response from Gemini tutor
    with st.chat_message("assistant"):
        with st.spinner("Miss Linda is preparing your material..."):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                bot_reply = response.text
                st.markdown(bot_reply)
                # Save assistant response
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"An error occurred: {e}")