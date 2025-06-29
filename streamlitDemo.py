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

st.markdown("""
    <style>
        .email-box {
            background-color: #f5f8fa;
            border-left: 5px solid #4a90e2;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 1px 2px 8px rgba(0,0,0,0.05);
        }
        .email-sender {
            font-weight: 600;
            color: #555;
            margin-bottom: 4px;
            font-size: 14px;
        }
        .email-subject {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .email-body {
            font-size: 15px;
            color: #444;
            white-space: pre-wrap;
        }
    </style>
""", unsafe_allow_html=True)

emails = st.session_state["emails"]

if not emails:
    st.warning("No s'han trobat correus electrònics.")
else:
    index = st.session_state["email_index"]
    email_content = emails[index]

    st.subheader(f"✉️ Missatge {index + 1} de {len(emails)}")

    if isinstance(email_content, dict):
        sender = email_content.get("sender", "Remitent desconegut")
        subject = email_content.get("subject", "Sense assumpte")
        content = email_content.get("content", "")
        name, email_address = parseaddr(sender)

        # Escapem HTML
        sender_escaped = html.escape(email_address)  # per mostrar
        print(sender_escaped)
        subject_escaped = html.escape(subject)
        body_escaped = html.escape(content).replace('\n', '<br>')

        st.markdown(f"""
        <div class="email-box">
            <div class="email-sender">📧 De: {sender_escaped}</div>
            <div class="email-subject">📝 Assumpte: {subject_escaped}</div>
            <div class="email-body">{body_escaped}</div>
        </div>
        """, unsafe_allow_html=True)

        content_text = content
    else:
        st.text_area("Contingut del correu electrònic", value=email_content, height=200)
        content_text = email_content

    # Botó per generar resposta
    if st.button("🔍 Genera resposta en català"):
        try:
            response = st.session_state["assistant"](user_input=content_text)
            st.session_state["response_text"] = response.content
            st.success("✅ Resposta generada:")
        except Exception as e:
            st.error(f"❌ Error al generar la resposta: {e}")

    # Àrea editable per la resposta
    st.session_state["response_text"] = st.text_area(
        "✏️ Revisa o edita la resposta abans d'enviar",
        value=st.session_state["response_text"],
        height=200
    )

    # Formulari per enviar la resposta
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
                reply_to=None  # Pots posar st.session_state["assistant"].username si vols
            )
            sender_client.disconnect()

            if success:
                st.success("✅ El correu s'ha enviat correctament.")
                # Opcional: neteja la resposta per no enviar-la de nou accidentalment
                st.session_state["response_text"] = ""
            else:
                st.error("❌ Error en l'enviament del correu.")

    # Botons anterior i següent
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Anterior") and st.session_state["email_index"] > 0:
            st.session_state["email_index"] -= 1
            st.rerun()
    with col2:
        if st.button("➡️ Següent") and st.session_state["email_index"] < len(emails) - 1:
            st.session_state["email_index"] += 1
            st.rerun()

