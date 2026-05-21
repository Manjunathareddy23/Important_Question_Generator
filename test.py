import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Check API key
if not GROQ_API_KEY:
    st.error("⚠️ Groq API Key is missing!")
    st.stop()

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Extract text from PDF
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

# Generate questions using Groq
def generate_questions(pdf_file, num_questions):

    text = extract_text_from_pdf(pdf_file)

    if not text:
        return "❌ No text found in PDF."

    # Reduce token usage
    text = text[:5000]

    prompt = f"""
    Read the following study material carefully.

    Generate {num_questions} important exam questions.

    Keep the questions concise and meaningful.

    Study Material:
    {text}
    """

    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
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

# ---------------- UI ---------------- #

st.title("📘 AI Important Question Generator")

st.write("Upload a PDF and generate important questions using Groq AI.")

# Upload PDF
pdf_file = st.file_uploader(
    "📂 Upload PDF",
    type=["pdf"]
)

# Number input
num_questions = st.number_input(
    "🔢 Number of Questions",
    min_value=1,
    max_value=50,
    value=5
)

# Generate button
if st.button("🎯 Generate Questions"):

    if pdf_file is not None:

        with st.spinner("⏳ Generating questions..."):

            questions = generate_questions(
                pdf_file,
                num_questions
            )

        st.subheader("📜 Generated Questions")

        st.write(questions)

    else:
        st.error("❌ Please upload a PDF first.")
