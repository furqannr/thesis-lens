import google.generativeai as genai
import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO

load_dotenv()

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(BytesIO(file.read()))
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text() or ""
    return text

def gemini_model_interaction(file_content):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    system_message = ("You are an AI model designed to analyze academic theses. When a user uploads a thesis document in PDF or Word format, your task is to review the document and generate a detailed report thoroughly. This report should identify and classify the major sections of the thesis (e.g., Title Page, Abstract, Introduction, Methodology, etc.) and ensure that all essential sections are present and correctly ordered. You need to assess the alignment of each section's content with the thesis objectives, highlighting any irrelevant or misaligned content. Additionally, conduct a thorough grammar and spelling check, evaluating the writing style for adherence to academic standards, including ensuring that the writer does not use first-person pronouns like "I," "we," or "us" in the text. The report should also identify specific page numbers, headings, and line numbers where grammatical mistakes or sentence structure issues occur, as well as any contradictions with information on other pages. The final report should include a summary of the thesis structure analysis, feedback on the alignment between the content and the thesis objectives, a list of grammar and style corrections, a list of shortcomings with suggestions for improvement, and any additional recommendations for enhancing the thesis. Ensure that the report is clear, concise, and actionable, with clear headings and bullet points.")

    response = model.generate_content([file_content, system_message])
    return response.text

st.title("ThesisLens")

file = st.file_uploader("Upload your thesis file here", type='pdf')

submit = st.button('Analyze Thesis')

if submit and file is not None:
    file_content = extract_text_from_pdf(file)  # Extract text from PDF file
    response = gemini_model_interaction(file_content)
    st.write(response)
