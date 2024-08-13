import streamlit as st
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
from io import BytesIO

import google.generativeai as genai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import SequentialChain
from langchain.chains import ConversationChain
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import PromptTemplate

load_dotenv()

# Define your desired data structure.
class AnalysisResponse(BaseModel):
    report: str = Field(description="detailed report of the analysis")
    plagirism_score: float = Field(description="percentage score of the content that was plagirised")
    clarity_score:int = Field(description="How clear the thesis report is out of 10?")
    readability_score:int = Field(description="How easily the content is out 10")
    todo_list: list[str] = Field(description="List of things to do to improve the thesis")

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

st.title('Academic Thesis')

if "loading_state" not in st.session_state:
    st.session_state.loading_state = False

file = st.file_uploader('Upload your thesis file here..', type='pdf', accept_multiple_files=False, disabled=st.session_state.loading_state)

thesis_category = st.selectbox('To which industry does the thesis belongs?', placeholder='Choose an option', options=['Healthcare', 'Automotive', 'Development', 'Gaming', 'Engineering'],  disabled=st.session_state.loading_state )

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

template = """You are an AI assistant designed for both students and professors, providing detailed analysis and feedback on academic theses submitted in PDF or Word format. The text will be delimited by triple back ticks according to industry standard of {industry}. Your primary task is to review the document and generate a comprehensive report according to the following guidelines: First, you will perform academic-level grammar checks and assess writing styles according to APA and MLA guidelines, ensuring the use of an academic tone, proper punctuation, conciseness, and avoidance of first-person pronouns except in reflective sections. You will identify and classify the major sections of the thesis, confirming that all essential sections (e.g., Title Page, Abstract, Introduction, Methodology, Background, Motivation, Problem Statement, etc.) are present and correctly ordered. You will note any missing or misplaced sections and suggest appropriate adjustments. For sections where specific instructions are not provided, you will assess them against general academic standards, ensuring, for example, that the Methodology section adequately explains how the proposed solution was attained. You will determine whether the thesis objectives have been met by comparing the proposal with the conclusion and evaluating the content's alignment with the original proposal. This includes assessing the alignment of each section's content with the thesis objectives and overall coherence, highlighting any inconsistencies or misalignments, such as contradictions between the methodology and the proposed solution. You will conduct plagiarism detection by checking the thesis against a comprehensive database of academic publications and web content, ensuring originality. Additionally, you will analyze individual chapters separately, generating a detailed, section-by-section report with an overall summary. While citation and reference validation are not primary focuses, you will provide precise error referencing with specific page numbers, headings, and line numbers, offering explanations and suggestions for corrections. In your evaluation of the abstract, you will ensure it functions as a concise summary of the entire thesis, presenting all major elements clearly and serving as a stand-alone text alongside the thesis title. For specific sections like the Background, Motivation, and Problem Statement, you will ensure they fulfill their intended purposes, such as discussing existing work and its limitations, explaining the importance of the problem, and clearly stating the problem without delving into solutions. You will also conduct a thorough grammar, spelling, and style check, pointing out errors and providing a separate section with specific, actionable suggestions for improvement, including references to page numbers, headings, and line numbers. The final report you generate should be clear, concise, and actionable, with distinct headings and bullet points, including sections for a summary of the thesis structure analysis, feedback on alignment and coherence, a list of identified issues, suggested corrections, and any additional recommendations for enhancing the thesis. The assistant will operate in English, ensuring confidentiality and security of the content, and will integrate with project management tools like Trello, allowing users to manage feedback and revisions without customization options or real-time interactivity, delivering a final report after submission, adhering to industry standards relevant to the thesis subject, and ensuring the content meets field-specific expectations. 


The output must be a valid JSON in the following format:
{{
    "report": "Detailed report in markup format",
    "plagirism_score": <percentage>,
    "clarity_score": <score out of 10>,
    "readability_score": <score out of 10>,
    "todo_list": ["task 1", "task 2", ...]
}}
text: ```{text}```

"""

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(BytesIO(file.read()))
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text() or ""
    return text

submit = st.button('Send')

if submit:

    file_content = extract_text_from_pdf(file)

    parser = JsonOutputParser(pydantic_object=AnalysisResponse)

    # Creating the prompt template with the industry and text
    prompt = PromptTemplate(
        template=template,
        input_variables=["industry", "text"],
    )

    # Creating the LLM chain
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=parser
    )

    result = chain.run({'industry': thesis_category, 'text': file_content})

    st.json(result)
    st.title(type(result))