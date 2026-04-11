import streamlit as st
import pdfplumber
import pandas as pd
import matplotlib.pyplot as plt
from groq import Groq
import re

# --- Page Setup ---
st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="centered")

st.title("🤖 AI Resume Screener")
st.write("Upload resumes and paste any job description — AI will rank the best candidates!")
st.caption("Made by Twisha Jain")

# --- API Key ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])  # define GROQ_API_KEY in .streamlit/secrets.toml

# --- Helper Functions ---
def extract_text(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.strip()

def score_resume(resume_text, job_description):
    prompt = f"""
    You are an expert HR recruiter. Analyze this resume against the job description.
    
    JOB DESCRIPTION:
    {job_description}
    
    RESUME:
    {resume_text}
    
    Respond in this exact format:
    SCORE: [0-100]
    STRENGTHS: [2-3 bullet points]
    WEAKNESSES: [2-3 bullet points]
    VERDICT: [1 sentence summary]
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# --- Job Description Input ---
st.header("Step 1: Paste Any Job Description")
job_desc = st.text_area("Job Description", height=200,
            placeholder="Paste any job description here!")

# --- Resume Upload ---
st.header("Step 2: Upload Resumes (PDF)")
uploaded_files = st.file_uploader("Upload one or more resumes",
                  type="pdf", accept_multiple_files=True)

# --- Run Button ---
if st.button("🚀 Screen Resumes"):
    if not job_desc:
        st.warning("Please paste a job description first!")
    elif not uploaded_files:
        st.warning("Please upload at least one resume!")
    else:
        results = []
        for file in uploaded_files:
            with st.spinner(f"Analyzing {file.name}..."):
                resume_text = extract_text(file)
                ai_response = score_resume(resume_text, job_desc)
                match = re.search(r"SCORE:\s*(\d+)", ai_response)
                score = int(match.group(1)) if match else 0
                results.append({
                    "Resume": file.name,
                    "Score": score,
                    "Analysis": ai_response
                })

        results = sorted(results, key=lambda x: x["Score"], reverse=True)

        st.header("📊 Results")
        df = pd.DataFrame([{"Resume": r["Resume"],
                            "Score": r["Score"]} for r in results])
        st.dataframe(df, use_container_width=True)

        st.header("📈 Visual Rankings")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh(df["Resume"], df["Score"], color="steelblue")
        ax.set_xlabel("Score (out of 100)")
        ax.set_title("Resume Rankings")
        ax.invert_yaxis()
        plt.tight_layout()
        st.pyplot(fig)

        st.header("🔍 Detailed Analysis")
        for i, r in enumerate(results):
            with st.expander(f"#{i+1} {r['Resume']} — Score: {r['Score']}/100"):
                st.text(r["Analysis"])
            