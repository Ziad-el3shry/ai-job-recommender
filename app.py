from groq import Groq
import streamlit as st
import os
from dotenv import load_dotenv
import pandas as pd
from PyPDF2 import PdfReader
import re
from groq_helper import analyze_resume_and_job
import matplotlib.pyplot as plt
from fpdf import FPDF

# Load environment variables
load_dotenv()
st.set_page_config(page_title="AI Job Recommender & Resume Analyzer", page_icon="🧠", layout="centered")

# App title and intro
st.title("🧠 AI Job Recommender & Resume Analyzer")
st.markdown("Upload your resume and get personalized job analysis and job recommendations powered by AI.")

# Upload resume and input job description
uploaded_file = st.file_uploader("📄 Upload your Resume (PDF)", type=["pdf"])
job_description = st.text_area("📝 Enter Job Description", height=200)

# Load job dataset
@st.cache_data
def load_job_dataset():
    return pd.read_csv("job_dataset.csv")

job_dataset = load_job_dataset()
selected_field = st.selectbox("📂 Select Job Field for Recommendations", sorted(job_dataset["field"].unique()))

# Extract text from PDF
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return "".join([page.extract_text() or "" for page in reader.pages])

# Recommend jobs
def recommend_jobs(field):
    recs = job_dataset[job_dataset["field"] == field].head(5)
    return "\n\n".join([f"{row['title']}\n- {row['description']}" for _, row in recs.iterrows()])

# Draw pie chart for match percentage
def draw_match_chart(percent):
    fig, ax = plt.subplots()
    sizes = [percent, 100 - percent]
    labels = ['Match', 'Remaining']
    colors = ['#4CAF50', '#D3D3D3']
    explode = (0.1, 0)

    ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
           startangle=90, explode=explode, shadow=True)
    ax.axis('equal')
    st.pyplot(fig)

# Remove emojis and symbols for clean text
def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002700-\U000027BF"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

# Generate PDF report
def generate_pdf(result_text, match_percent, recommendations, pdf_path="resume_analysis.pdf"):
    result_text = remove_emojis(result_text)
    recommendations = remove_emojis(recommendations)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="AI Resume Analysis Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(200, 10, txt=f"Match Percentage: {match_percent}%", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", style="", size=12)
    pdf.multi_cell(0, 10, txt="Resume Analysis:")
    pdf.multi_cell(0, 10, txt=result_text)
    pdf.ln(5)

    pdf.multi_cell(0, 10, txt="Recommended Jobs:")
    pdf.multi_cell(0, 10, txt=recommendations)

    pdf.output(pdf_path)
    return pdf_path

# Main logic
if st.button("🔍 Analyze & Recommend"):
    if not uploaded_file or not job_description.strip():
        st.warning("⚠️ Please upload a resume and provide a job description.")
    else:
        with st.spinner("Analyzing..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            result = analyze_resume_and_job(resume_text, job_description)

            st.success("✅ Analysis Complete")
            st.markdown("### 📊 Resume Analysis")

            # Extract and remove match percentage
            match = re.search(r"\*\*Match Percentage:\*\*\s*(\d+)", result)
            percent = int(match.group(1)) if match else None
            result = re.sub(r"\*\*Match Percentage:\*\*\s*\d+", "", result)

            if percent is not None:
                st.metric("✅ Match Percentage", f"{percent}%")
                st.progress(percent / 100)
                draw_match_chart(percent)
            else:
                st.warning("⚠️ Match percentage not detected.")

            st.markdown(result)
            st.markdown("---")

            # Job recommendations
            st.markdown(f"### 💼 Job Recommendations for **{selected_field}**")
            rec_text = recommend_jobs(selected_field)
            st.markdown(rec_text)

            # PDF download
            pdf_path = generate_pdf(result, percent or 0, rec_text)
            with open(pdf_path, "rb") as f:
                st.download_button("📥 Download Report as PDF", f, file_name="Resume_Report.pdf")
