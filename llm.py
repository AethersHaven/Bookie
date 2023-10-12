from model import load_llm_model
from dotenv import load_dotenv
from os import getenv
from string import punctuation
from embed import get_relevant_books
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import streamlit

class CustomStreamingHandler:
    """Base callback handler that can be used to handle callbacks from langchain."""
    def __init__(self):
        self.raise_error = False
        self.ignore_llm = False
        self.ignore_chat_model = False
        self.text = ""

    def on_llm_start(self, serialized, prompts, **kwargs):
        pass

    def on_chat_model_start(self, serialized, messages, **kwargs):
        pass

    def on_llm_new_token(self, token, **kwargs):
        streamlit.write(self.text + token)
        self.text += token

    def on_llm_end(self, response, **kwargs):
        pass

    def on_llm_error(self, error, **kwargs):
        pass

class LLM:
    def __init__(self):
        # Loading environment variables
        load_dotenv()
        openai_api_key = getenv('OPENAI_API_KEY')

        # Loading the backend model
        self.backend_model = load_llm_model("chatopenai", openai_api_key, "gpt-3.5-turbo-16k", temperature=0, streaming=False)
        self.refinement_template = """
            You are an expert at refining and rephrasing user queries to make them perfect for similarity search embeddings in a book database. 
            Your mission is to take any request, extract its core elements, and present it in a concise manner suitable for identifying the most relevant book matches.

            Please transform the request into a refined query optimized for similarity search.
            Provide nothing but the refined query.
            If there is no query to refine, respond with "NO QUERY TO REFINE".
        """.replace('  ', '').strip()

        # Loading the chat model
        self.conversation_model = load_llm_model("chatopenai", openai_api_key, "gpt-3.5-turbo-16k", temperature=1, streaming=True) # , callbacks=[StreamingStdOutCallbackHandler()]
        self.conversation_template = """
            You are "Bookie", the ever-friendly librarian with an uncanny knack for finding the right book for every reader.
            Your vast experience and love for literature make you the perfect guide in the vast world of books. 
            Whenever you come across a suggestion that's part of a series, always recommend the first book so newcomers can start at the beginning.

            Remember, your charm lies not just in your bookish knowledge, but also in the personal touch you bring. Engage, chat, and ensure the recommendation truly fits the reader's mood or interests. 
            And if they don't ask for a book directly, just have a friendly chat or share a bit of your wisdom.

            To assist in your mission, here's a list of potentially relevant books with brief descriptions, if provided:
            {relevant_books}
        """.replace('  ', '').strip()

        self.conversation_history = []
        self.memory_length = 6


    def chat(self, user_input):
        if not self.conversation_model:
            return "Model must be initialized before query."
        if len(user_input) == 0:
            return "You did not input anything."
        if user_input[-1] not in punctuation:
            user_input += "."
        
        refined_query = self.backend_model(self.conversation_history[-(self.memory_length*2):] + [SystemMessage(content=self.refinement_template), HumanMessage(content=user_input)]).content
        book_list = ""
        if "NO QUERY" not in refined_query:
            book_list = '-----\n'.join(get_relevant_books(refined_query, 5))

        model_input = self.conversation_template.format(prompt=user_input, relevant_books=book_list)
        response = self.conversation_model(
            self.conversation_history[-(self.memory_length*2):] + [SystemMessage(content=model_input), HumanMessage(content=user_input)],
            callbacks=[CustomStreamingHandler()]
        ).content

        self.conversation_history.append(HumanMessage(content=user_input))
        self.conversation_history.append(AIMessage(content=response))

        return response

    
    def reset_memory(self):
        self.conversation_history = []
