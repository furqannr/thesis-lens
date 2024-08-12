import google.generativeai as genai
import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO, StringIO
from fpdf import FPDF

# Load environment variables
load_dotenv()

# Configure the Google Generative AI
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
    system_message = (f"You are an AI model designed to analyze academic theses. When a user uploads a thesis document in PDF or Word format, your task is to review the document and generate a detailed report according to the following guidelines: First, identify and classify the major sections of the thesis, ensuring all essential sections (e.g., Title Page, Abstract, Introduction, Methodology, Background, Motivation, Problem Statement, etc.) are present and correctly ordered, while noting any missing or misplaced sections and suggesting appropriate adjustments. For sections where specific instructions are not given, assess them against general academic concepts, ensuring, for example, that the Methodology section explains how the proposed solution was attained. Next, identify and list issues in the thesis sequentially as they appear, detailing each issue with specific page numbers, headings, and line numbers. These issues should relate to content relevance, alignment with objectives, use of first-person pronouns, grammatical errors, or other concerns. The report should include a separate section dedicated to the identification of these issues. You also need to assess the alignment of each section's content with the thesis objectives and overall coherence, highlighting any inconsistencies or misalignments, such as contradictions between the methodology and proposed solution. In your evaluation of the abstract, ensure it functions as a summary of the entire thesis, presenting all major elements concisely and serving as a stand-alone text along with the thesis title. For specific sections like the Background, Motivation, and Problem Statement, ensure they fulfill their intended purposes, such as discussing existing work and its limitations, explaining the importance of the problem, and clearly stating the problem without delving into solutions. For sections without specific instructions, verify their alignment with the general concepts and overall thesis structure. Conduct a thorough grammar, spelling, and style check, pointing out errors without suggesting corrections, and ensuring the use of academic tone, proper punctuation, conciseness, and avoidance of first-person pronouns except in reflective sections. Additionally, provide a separate section with specific, actionable suggestions for improvement, including references to page numbers, headings, and line numbers. The final report should be clear, concise, and actionable, with distinct headings and bullet points, including sections for a summary of the thesis structure analysis, feedback on alignment and coherence, a list of identified issues, suggested corrections, and any additional recommendations for enhancing the thesis.")

    response = model.generate_content([file_content, system_message])
    return response.text


def save_to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    
    # Replace unsupported characters with an empty string
    clean_text = text.encode('latin-1', 'replace').decode('latin-1')

    # Add each line of the cleaned text to the PDF
    for line in clean_text.split('\n'):
        pdf.multi_cell(0, 10, line)
    
    # Save the PDF content as a string and write it to BytesIO
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin-1'))
    pdf_output.seek(0)  # Move the pointer to the start of the file
    
    return pdf_output




st.title("ThesisLens")

file = st.file_uploader("Upload your thesis file here", type='pdf')

submit = st.button('Analyze Thesis')

if submit and file is not None:
    file_content = extract_text_from_pdf(file)  # Extract text from PDF file
    response = gemini_model_interaction(file_content)  # Get the response from the AI model
    
    st.write(response)  # Display the response on the page
    
    # Convert response to PDF
    pdf_file = save_to_pdf(response)
    
    # Provide a download link for the PDF file
    st.download_button(
        label="Download Report as PDF",
        data=pdf_file,
        file_name="Thesis_Report.pdf",
        mime="application/pdf"
    )
