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
    system_message = ("You are an AI model designed to analyze academic theses. "
                      "The user has uploaded a thesis document in PDF or Word format. "
                      "Your task is to thoroughly review the document and generate a detailed report highlighting. "
                      "You have to analyze the uploaded thesis document by identifying and classifying its major sections "
                      "(e.g., Title Page, Abstract, Introduction, Methodology, etc.), and ensure all essential sections are present "
                      "and correctly ordered. Assess the alignment of each section's content with the thesis objectives, highlighting any "
                      "irrelevant or misaligned content. Conduct a thorough grammar and spelling check, evaluating the writing style for adherence "
                      "to academic standards. Finally, generate a structured report A summary of the thesis structure analysis. Feedback on the "
                      "alignment between the content and the thesis objectives. A list of grammar and style corrections. .Also give a list of shortcomings and how the thesis can be further improved. Any additional recommendations "
                      "for improving the thesis. Ensure the report is clear, concise, and actionable. Give clear headings in the report and use bullet points.")

    response = model.generate_content([file_content, system_message])
    return response.text

st.title("ThesisLens")

file = st.file_uploader("Upload your thesis file here", type='pdf')

submit = st.button('Analyze Thesis')

if submit and file is not None:
    file_content = extract_text_from_pdf(file)  # Extract text from PDF file
    response = gemini_model_interaction(file_content)
    st.write(response)
