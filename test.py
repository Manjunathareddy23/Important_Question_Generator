import streamlit as st
import fitz  # PyMuPDF
from google import genai
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check API key
if not GEMINI_API_KEY:
    st.error("⚠️ Gemini API Key is missing!")
    st.stop()

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

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

# Generate questions
def generate_questions(pdf_file, num_questions):

    text = extract_text_from_pdf(pdf_file)

    if not text:
        return "❌ No text found in PDF."

    # Prevent token overflow
    text = text[:15000]

    prompt = f"""
    Read the following content carefully.

    Generate {num_questions} important exam questions
    from the content below.

    Content:
    {text}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"❌ Error generating questions: {e}"

# ---------------- UI ---------------- #

st.title("📘 AI Important Question Generator")

st.write("Upload a PDF and generate important questions using AI.")

# Upload PDF
pdf_file = st.file_uploader(
    "📂 Upload PDF",
    type=["pdf"]
)

# Number of questions
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
