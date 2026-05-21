import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os
from dotenv import load_dotenv

# ---------------- LOAD ENV ---------------- #

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("⚠️ GROQ API Key is missing!")
    st.stop()

# ---------------- GROQ CLIENT ---------------- #

client = Groq(api_key=GROQ_API_KEY)

# ---------------- PDF TEXT EXTRACTION ---------------- #

def extract_text_from_pdf(pdf_file):
    try:
        pdf_bytes = pdf_file.read()

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        text = ""

        for page in doc:
            text += page.get_text("text")

        return text.strip()

    except Exception as e:
        return f"❌ Error reading PDF: {e}"

# ---------------- QUESTION GENERATION ---------------- #

def generate_questions(pdf_file, num_questions):

    text = extract_text_from_pdf(pdf_file)

    if not text:
        return "❌ No text found in PDF."

    # Reduce large PDF size
    text = text[:5000]

    prompt = f"""
    Read the following study material carefully.

    Generate {num_questions} important exam questions.

    Rules:
    - Questions should be concise
    - Questions should be meaningful
    - Avoid duplicate questions
    - Format as numbered list

    Study Material:
    {text}
    """

    try:

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational question generator."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.5,
            max_tokens=1024
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Error generating questions: {e}"

# ---------------- STREAMLIT UI ---------------- #

st.set_page_config(
    page_title="AI Question Generator",
    page_icon="📘",
    layout="centered"
)

st.title("📘 AI Important Question Generator")

st.write(
    "Upload a PDF and generate important exam questions using Groq AI."
)

# Upload PDF
pdf_file = st.file_uploader(
    "📂 Upload PDF File",
    type=["pdf"]
)

# Number of questions
num_questions = st.number_input(
    "🔢 Number of Questions",
    min_value=1,
    max_value=50,
    value=5
)

# Generate Button
if st.button("🎯 Generate Questions"):

    if pdf_file is not None:

        with st.spinner("⏳ Generating questions... Please wait!"):

            questions = generate_questions(
                pdf_file,
                num_questions
            )

        st.subheader("📜 Generated Questions")

        st.write(questions)

    else:
        st.error("❌ Please upload a PDF file first.")
