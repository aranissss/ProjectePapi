from langchain_openai import ChatOpenAI
import streamlit as st
#import os
#from dotenv import load_dotenv, find_dotenv

#load_dotenv(find_dotenv())
st.write("🔐 Secrets loaded:", list(st.secrets.keys()))
class LLMClient:
    def __init__(self, stream: bool = False):
        st.write("🔐 Secrets loaded:", list(st.secrets.keys()))
        print(st.secrets.keys())
        self.__llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=st.secrets['OPENAI_API_KEY'],
            #api_key=os.getenv('OPENAI_API_KEY'),
            #response_format="json",  # ← actual recomendado
        )

    def getClient(self):
        return self.__llm
