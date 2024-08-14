from dotenv import load_dotenv
import os
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the GenAI API with the API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# System message for the LLM
system_message = (
    "You are an expert evaluator whose job is to give marks out of 10. You will be given a text and are required to assess it based on three key metrics: "
    "clarity, readability, and content quality. You will provide a score out of 10 for each metric based on the following criteria:\n\n"
    
    "1. **Clarity (1-10):**\n"
    "- Criteria: How clearly are the ideas and arguments presented? Is the purpose of the document easily understandable? "
    "Are the key points and conclusions well-articulated?\n\n"
    
    "2. **Readability (1-10):**\n"
    "- Criteria: How easy is the document to read and comprehend? Consider factors such as sentence structure, grammar, use of language, "
    "and flow.\n\n"
    
    "3. **Content Quality (1-10):**\n"
    "- Criteria: How well does the document meet its intended purpose? Is the content accurate, well-researched, and relevant?\n\n"
    
    "Please return only a score for each metric and make sure to mark exactly as defined above and give low marks if clarity, readibility and content quality are not good as like in the below example:"
    "Clarity: 2/10\n"
    "Readability: 2/10\n"
    "Content Quality: 1/10"
)

def metric_llm_model(file_content):
    # Combine the system message with the content to evaluate
    prompt = f"{system_message}\n\nText: ```{file_content}```"

    # Generate response
    llm = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = llm.generate_content(prompt)
    return response.text

# Example usage
file_content = """Your text to be evaluated goes here."""
result = metric_llm_model(file_content)
print(result)
