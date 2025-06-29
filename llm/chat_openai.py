import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class LLMClient:
    def __init__(self, stream: bool = False):
        self.__llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=os.getenv('OPENAI_API_KEY'),
            #response_format="json",  # ← actual recomendado
        )

    def getClient(self):
        return self.__llm
