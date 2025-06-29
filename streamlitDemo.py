import streamlit as st
from llm.chat_openai import LLMClient
from assistant.assistant_agent import Assistant
from mail.email_fetcher import EmailFetcher
from mail.email_sender import EmailSender  # <-- importem la nova classe
from email.utils import parseaddr
import html


# Page setup
st.set_page_config(page_title="📧 SH Concept Formació - Email Assistant", layout="wide")

st.title("📥 Assistència per correus del centre esportiu SH Concept Formació")

# --- Session State Setup ---
if "assistant" not in st.session_state:
   llm_agent = LLMClient(stream=False)
    st.session_state["assistant"] = Assistant(llm_agent=llm_agent.getClient())
