import streamlit as st
import json
import os
from llm.chat_openai import LLMClient
from assistant.assistant_agent import Assistant
from mail.email_fetcher import EmailFetcher
from mail.email_sender import EmailSender
from email.utils import parseaddr
import html

# Fitxer per guardar els emails contestats
ANSWERED_EMAILS_FILE = "answered_emails.json"

def load_answered_emails():
    if os.path.exists(ANSWERED_EMAILS_FILE):
        with open(ANSWERED_EMAILS_FILE, "r") as f:
            return json.load(f)
    return []

def save_answered_emails(answered_list):
    with open(ANSWERED_EMAILS_FILE, "w") as f:
        json.dump(answered_list, f)

# Page setup
st.set_page_config(page_title="📧 SH Concept Formació - Email Assistant", layout="wide")

st.title("📥 Assistència per correus del centre esportiu SH Concept Formació")

# --- Load answered emails from file if not in session_state ---
if "answered_emails" not in st.session_state:
    st.session_state["answered_emails"] = load_answered_emails()

if "assistant" not in st.session_state:
    llm_agent = LLMClient(stream=False)
    st.session_state["assistant"] = Assistant(llm_agent=llm_agent.getClient())

if "emails" not in st.session_state:
    fetcher = EmailFetcher()
    fetcher.connect()
    st.session_state["emails"] = fetcher.fetch_latest_email()
    fetcher.disconnect()

    if isinstance(st.session_state["emails"], (dict, str)):
        st.session_state["emails"] = [st.session_state["emails"]]

if "email_index" not in st.session_state:
    st.session_state["email_index"] = 0

if "response_text" not in st.session_state:
    st.session_state["response_text"] = ""

# Filtrar emails no contestats segons id
def filter_unanswered_emails(all_emails, answered_ids):
    return [email for email in all_emails if email.get("id", "") not in answered_ids]

unanswered_emails = filter_unanswered_emails(st.session_state["emails"], st.session_state["answered_emails"])
if not unanswered_emails:
    st.warning("No hi ha correus pendents de resposta.")
else:
    # Selecció de correu via menú lateral
    col_menu, col_detail = st.columns([1, 3])

    with col_menu:
        st.subheader("📬 Correus pendents")
        for i, email in enumerate(unanswered_emails):
            sender = parseaddr(email.get("sender", ""))[1]
            subject = email.get("subject", "Sense assumpte")
            email_id = email.get("id", "")
            label = f"{subject} ({sender})"

            row_col1, row_col2 = st.columns([0.2, 0.8])
            
            with row_col1:
                if st.button("❌", key=f"ignore_menu_{email_id}"):
                    if email_id not in st.session_state["answered_emails"]:
                        st.session_state["answered_emails"].append(email_id)
                        save_answered_emails(st.session_state["answered_emails"])
                    st.rerun()

            with row_col2:
                if st.button(label, key=f"select_menu_{i}"):
                    st.session_state["email_index"] = i
                    st.rerun()


    with col_detail:
        index = st.session_state["email_index"]
        email_content = unanswered_emails[index]

        sender = email_content.get("sender", "Remitent desconegut")
        subject = email_content.get("subject", "Sense assumpte")
        content = email_content.get("content", "")
        id = email_content.get("id", "")
        name, email_address = parseaddr(sender)

        sender_escaped = html.escape(email_address)
        subject_escaped = html.escape(subject)
        body_escaped = html.escape(content).replace('\n', '<br>')

        st.subheader(f"✉️ Missatge seleccionat")
        st.markdown(f"""
        <div class="email-box" style="background-color:#fff; border-left:5px solid #4a90e2; border-radius:12px; padding:20px; margin:10px 0; box-shadow:1px 2px 8px rgba(0,0,0,0.05);">
            <div style="font-weight:600; color:#555; margin-bottom:4px; font-size:14px;">📧 De: {sender_escaped}</div>
            <div style="font-size:18px; font-weight:bold; color:#333; margin-bottom:10px;">📝 Assumpte: {subject_escaped}</div>
            <div style="font-size:15px; color:#444; white-space: pre-wrap;">{body_escaped}</div>
        </div>
        """, unsafe_allow_html=True)

        """if st.button("❌ Ignora aquest correu", key=f"ignore_{id}"):
            if id not in st.session_state["answered_emails"]:
                st.session_state["answered_emails"].append(id)
                save_answered_emails(st.session_state["answered_emails"])
            st.rerun()"""

        content_text = content

        if st.button("🔍 Genera resposta en català"):
            try:
                response = st.session_state["assistant"](user_input=content_text)
                st.session_state["response_text"] = response.content
                st.success("✅ Resposta generada:")
            except Exception as e:
                st.error(f"❌ Error al generar la resposta: {e}")

        st.session_state["response_text"] = st.text_area(
            "✏️ Revisa o edita la resposta abans d'enviar",
            value=st.session_state["response_text"],
            height=200
        )

        with st.form("send_email_form"):
            to_email = st.text_input("📨 Correu destinatari", value=sender_escaped)
            subject_to_send = st.text_input("📝 Assumpte", value=f"Re: {subject_escaped}")
            body_to_send = st.session_state["response_text"]
            submit = st.form_submit_button("📤 Envia la resposta")

            if submit:
                sender_client = EmailSender()
                sender_client.connect()
                success = sender_client.send_email(
                    to_address=to_email,
                    subject=subject_to_send,
                    body=body_to_send,
                    reply_to=None
                )
                sender_client.disconnect()

                if success:
                    st.success("✅ El correu s'ha enviat correctament.")
                    if id not in st.session_state["answered_emails"]:
                        st.session_state["answered_emails"].append(id)
                        save_answered_emails(st.session_state["answered_emails"])
                    st.session_state["response_text"] = ""
                    st.rerun()
                else:
                    st.error("❌ Error en l'enviament del correu.")
