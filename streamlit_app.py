import os
from google import genai
from google.genai import types
import streamlit as st

# Load secret key from Streamlit Secrets or environment
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets. Please check your deployment settings.")
    st.stop()

# Initialize Gemini Client
client = genai.Client(api_key=api_key)

# Web App Title and Layout
st.set_page_config(page_title="AI Study Tutor", page_icon="🎓", layout="centered")
st.title("🎓 AI Tutor & Testing Assistant")
st.write("Welcome, student! Ask your tutor for a quiz, test your knowledge, and get instant feedback.")

# Define the Tutor Persona
TUTOR_SYSTEM_INSTRUCTION = """
You are an encouraging, expert AI Tutor. 
Your primary job is to help students learn and test their knowledge.

Rules you MUST follow:
1. When a student requests a quiz or test on a topic (e.g., "Test me on Biology" or "Give me a 3-question Python quiz"):
   - Present the questions clearly one by one or as a short numbered list.
   - Do NOT provide the answers upfront.
2. When the student submits their answers:
   - Evaluate each answer clearly (Mark as Correct or Incorrect).
   - Give constructive feedback and explain WHY an answer was wrong.
   - Provide a final score (e.g., 8/10 or 3/3).
   - Ask if they want another test or if they need a topic re-explained.
3. Be patient, supportive, and clear.
"""

# Initialize chat session and message history in Streamlit memory
if "chat_session" not in st.session_state:
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=TUTOR_SYSTEM_INSTRUCTION
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat history on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box at the bottom of the web page
if user_input := st.chat_input("Type your message here (e.g., 'Quiz me on photosynthesis')..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response from Gemini tutor
    with st.chat_message("assistant"):
        with st.spinner("Tutor is preparing your material..."):
            try:
                response = st.session_state.chat_session.send_message(user_input)
                bot_reply = response.text
                st.markdown(bot_reply)
                # Save assistant response
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"An error occurred: {e}")