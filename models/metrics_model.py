from dotenv import load_dotenv
import os

import google.generativeai as genai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Todo: Add system message

def metric_llm_model(file_content):
    template = """
        # system message

        text: ```{file_content}```
    """
    
    llm = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = llm.generate_content([file_content, template])
    return response.text


