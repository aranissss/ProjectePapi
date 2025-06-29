import streamlit as st
from llm.chat_openai import LLMClient
from assistant.assistant_agent import Assistant
from mail.email_fetcher import EmailFetcher
from mail.email_sender import EmailSender  # <-- importem la nova classe
from email.utils import parseaddr
import html

