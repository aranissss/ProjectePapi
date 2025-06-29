from langchain_core.prompts import ChatPromptTemplate
from .prompt import DEFAULT_PREFIX, HUMAN


class Assistant:
    """
    Simple Assistant that queries an LLM directly with system + human prompts defined externally.
    """

    def __init__(self, llm_agent):
        """
        Initialize with the LLM model and prepare the prompt template.
        """
        self.__llm = llm_agent

        # Create ChatPromptTemplate from your existing prompts
        self.__prompt_template = ChatPromptTemplate([
            ("system", DEFAULT_PREFIX),
            ("human", HUMAN)
        ])

    def __call__(self, user_input: str):
        """
        Call the LLM with the user input and return the response string.
        """
        # Invoke prompt with variable "input" set to user_input
        prompt_value = self.__prompt_template.invoke({"input": user_input})

        # Get the messages to send to the LLM
        messages = prompt_value.messages
        #prompt_text = "\n".join([msg.content for msg in prompt_value.messages])

        try:
            text_response = self.__llm.invoke(messages)
        except Exception as e:
            print(f"[Assistant Error] No s'ha pogut obtenir una resposta: {e}")
            text_response = "Ho sento, hi ha hagut un error processant la teva sol·licitud."

        return text_response
