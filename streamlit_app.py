import os
from google import genai
from google.genai import types
import streamlit as st

# Load secret key from Streamlit Secrets or local environment
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in Streamlit Secrets or .env file.")
    st.stop()

# Web App Title and Layout
st.set_page_config(page_title="Miss Linda's F&B Tutor", page_icon="🎓", layout="centered")
st.title("🎓 Miss Linda's Food & Beverage Service Tutor")
st.write("Welcome, student! Test your knowledge on F&B service and get instant feedback from your tutor.")

# ==========================================
# MISS LINDA'S CUSTOM TUTOR PERSONA:
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


# Function to get a fresh client connection and send message safely
def send_message_to_gemini(messages_history, new_user_input):
    # Initialize a fresh client instance every time to avoid "client has been closed" errors
    client = genai.Client(api_key=api_key)

    # Format message history for the modern API client
    formatted_contents = []
    for msg in messages_history:
        role = "user" if msg["role"] == "user" else "model"
        formatted_contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])])
        )

    # Append the new input
    formatted_contents.append(
        types.Content(role="user", parts=[types.Part.from_text(text=new_user_input)])
    )

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=formatted_contents,
        config=types.GenerateContentConfig(
            system_instruction=TUTOR_SYSTEM_INSTRUCTION
        )
    )
    return response.text


# Initialize message history in Streamlit memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat history on the screen
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input box at the bottom of the web page
if user_input := st.chat_input("Type your message here (e.g., 'Test me on water service')..."):
    # Display user message instantly
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response from Miss Linda using the fresh client function
    with st.chat_message("assistant"):
        with st.spinner("Miss Linda is preparing your material..."):
            try:
                bot_reply = send_message_to_gemini(st.session_state.messages, user_input)
                st.markdown(bot_reply)

                # Save both messages to history
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.session_state.messages.append({"role": "assistant", "content": bot_reply})
            except Exception as e:
                st.error(f"An error occurred: {e}")