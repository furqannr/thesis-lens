from dotenv import load_dotenv
import os

import google.generativeai as genai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# System message for the LLM
system_message = {
    "prompt": (
        "You are an expert evaluator. You will be given a document and are required to assess it based on three key metrics: "
        "clarity, readability, and content quality. You will provide a score out of 10 for each metric based on the following criteria:\n\n"
        
        "1. **Clarity (1-10):**\n"
        "- Criteria: How clearly are the ideas and arguments presented? Is the purpose of the document easily understandable? "
        "Are the key points and conclusions well-articulated?\n\n"
        
        "2. **Readability (1-10):**\n"
        "- Criteria: How easy is the document to read and comprehend? Consider factors such as sentence structure, grammar, use of language, "
        "and flow.\n\n"
        
        "3. **Content Quality (1-10):**\n"
        "- Criteria: How well does the document meet its intended purpose? Is the content accurate, well-researched, and relevant?\n\n"
        
        "Please return only a score for each metric."
    )
}

def metric_llm_model(file_content):
    template = """
    # System message

    {system_message["prompt"]}

    text: ```{{file_content}}```
    """

    llm = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = llm.generate_content([file_content, template])
    return response.text
