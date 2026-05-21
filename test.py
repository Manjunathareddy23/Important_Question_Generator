import streamlit as st
import fitz  # PyMuPDF for extracting text from PDFs
import google.generativeai as genai
import os  # For environment variables
from dotenv import load_dotenv  # To load .env file

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key exists
if not GEMINI_API_KEY:
    st.error("⚠️ Gemini API Key is missing! Set it as an environment variable.")
else:
    genai.configure(api_key=GEMINI_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = "\n".join(page.get_text("text") for page in doc)
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

# Function to generate important questions using Gemini API
def generate_questions(pdf_file, num_questions):
    if not pdf_file:
        return "❌ Please upload a PDF file."
    
    text = extract_text_from_pdf(pdf_file)
    
    if not text:
        return "❌ No text found in the PDF."

    prompt = f"Extract {num_questions} important questions from the following content:\n\n{text}"

    try:
        # Use the correct model name from list_models() output
        model = genai.GenerativeModel("gemini-pro")  
        response = model.generate_content(prompt)
        
        return response.text if response.text else "⚠️ Could not generate questions."
    
    except Exception as e:
        return f"❌ Error generating questions: {e}"

# Streamlit UI
st.title("📘 AI-Based Important Question Generator")
st.write("Upload a PDF and specify the number of important questions you need.")

# File uploader
pdf_file = st.file_uploader("📂 Upload a PDF", type=["pdf"])

# Number input for questions
num_questions = st.number_input("🔢 Number of Questions", min_value=1, value=5)

# Generate button
if st.button("🎯 Generate Questions"):
    if pdf_file:
        with st.spinner("⏳ Generating Questions... Please wait!"):
            questions = generate_questions(pdf_file, num_questions)
        st.subheader("📜 Generated Questions:")
        st.write(questions)
    else:
        st.error("❌ Please upload a PDF file first!")
