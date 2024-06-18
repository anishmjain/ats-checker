import os
import streamlit as st
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Import and configure google.generativeai
def configure_genai():
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    return genai

genai = configure_genai()

def get_gemini_response(input_text):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(input_text)
    return response.text

def input_pdf_text(uploaded_file):
    try:
        reader = pdf.PdfReader(uploaded_file)
        text = ""
        for page in range(len(reader.pages)):
            page = reader.pages[page]
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

# Prompt Template
input_prompt = """
Hey, act like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech field, software engineering, data science, data analyst,
and big data engineer. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
best assistance for improving the resumes. Assign the percentage matching based 
on JD and
the missing keywords with high accuracy.
resume: {text}
description: {jd}

I want the response in one single string having the structure
{{"JD Match": "%", "MissingKeywords": [], "Profile Summary": ""}}
"""

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload the PDF")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        if text:
            full_prompt = input_prompt.format(text=text, jd=jd)
            response = get_gemini_response(full_prompt)
            
            try:
                response_dict = json.loads(response)
                st.subheader("The Response is")
                st.write("**JD Match:** {}".format(response_dict.get("JD Match", "N/A")))
                st.write("**Missing Keywords:** {}".format(", ".join(response_dict.get("MissingKeywords", []))))
                st.write("**Profile Summary:**")
                st.write(response_dict.get("Profile Summary", "No summary provided."))
            except json.JSONDecodeError:
                st.error("Error decoding response from the generative AI. Please try again.")
        else:
            st.write("Failed to extract text from the uploaded PDF. Please check the file and try again.")
    else:
        st.write("Please upload the resume")


