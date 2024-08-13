import google.generativeai as genai
import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from io import BytesIO

import smtplib, ssl
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders

import markdown2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from bs4 import BeautifulSoup

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


def save_to_pdf(markdown_text):
    # Convert markdown to HTML
    html_text = markdown2.markdown(markdown_text)
    
    # Parse the HTML to plain text while keeping the tags
    soup = BeautifulSoup(html_text, "html.parser")

    # Create a ReportLab document
    pdf_output = BytesIO()
    doc = SimpleDocTemplate(pdf_output, pagesize=letter)

    # Define ReportLab styles
    styles = getSampleStyleSheet()
    custom_style = ParagraphStyle(
        name="Custom",
        alignment=TA_LEFT,
        fontSize=12,
        leading=14,  # Space between lines
        spaceAfter=10,  # Space after each paragraph
        preserveWhiteSpace=True  # Preserve spaces
    )

    # Create a list to hold the content
    story = []

    # Convert each part of the HTML content to a ReportLab Paragraph
    for element in soup:
        if element.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            style = styles["Heading1"] if element.name == "h1" else styles["Heading2"]
        else:
            style = custom_style

        text = str(element)

        # Handle multiple newlines by adding Spacer elements
        if element.name == 'br':
            story.append(Spacer(1, 12))
        else:
            paragraphs = text.split('\n')
            for para in paragraphs:
                if para.strip():  # If the paragraph has content
                    story.append(Paragraph(para, style))
                else:
                    story.append(Spacer(1, 12))  # Add space for empty lines

    # Build the PDF document
    doc.build(story)

    # Move the pointer to the start of the file
    pdf_output.seek(0)

    return pdf_output

def send_email(to_email, attachment=None):
    email_sender = "mmaazkhanhere@gmail.com"
    email_password = "jyhstqcntehyovve"

    if not email_sender or not email_password:
        st.error('Email credentials not found')
        return False
    
    subject = 'Thesis Report'
    content = """
        Hello customer! Thank you for using our service. We
        hope it acted as you supposed it would. Here is the
        detailed report of your thesis. Wish you good luck in your
        future endeavors.
    """

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = email_sender
    msg['To'] = to_email
    msg['Subject'] = subject
    body = MIMEText(content, 'plain')
    msg.attach(body)

    if attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename= Thesis_Report.pdf')
        msg.attach(part)

    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, to_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email to {to_email}. Error: {str(e)}")
        return False


st.title("ThesisLens")

# Initialize email list in session state if it doesn't exist
if 'email_list' not in st.session_state:
    st.session_state.email_list = []

# Display warning or success message depending on emails 
if st.session_state.email_list:
    st.success("Emails added. You can now submit the report.")
else:
    st.warning("Please add at least one email.")

# Input field for entering email
new_email = st.text_input('Enter email address:')

# Button to add the email to the list
if st.button('Add Email'):
    if new_email:  # Check if the email field is not empty
        st.session_state.email_list.append(new_email)

# Display the current list of emails if any
if st.session_state.email_list:
    st.write("Emails to send the report to:")
    for idx, email in enumerate(st.session_state.email_list):
        st.write(f"{idx + 1}. {email}")

file = st.file_uploader("Upload your thesis file here", type='pdf')

submit = st.button('Analyze Thesis')

if submit and file is not None:
    if len(st.session_state.email_list) == 0:
        st.error("Please enter at least one email address")
    else:
        file_content = extract_text_from_pdf(file)  # Extract text from PDF file
        response = gemini_model_interaction(file_content)  # Get the response from the AI model
        
        st.write(response)  # Display the response on the page
        
        # Convert response to PDF
        pdf_file = save_to_pdf(response)

        # send the report via email
        subject = "Thesis Report"
        body = "Please find attached the thesis report generated by ThesisLens."

        email_lists = st.session_state.email_list  # Use the email list from session state
        for email in email_lists:
            if send_email(email, attachment=pdf_file):
                st.success(f"Email sent successfully to {email}!")
            else:
                st.error(f"Failed to send the email to {email}.")

        
        # Provide a download link for the PDF file
        st.download_button(
            label="Download Report as PDF",
            data=pdf_file,
            file_name="Thesis_Report.pdf",
            mime="application/pdf"
        )
