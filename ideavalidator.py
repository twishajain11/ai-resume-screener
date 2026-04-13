import streamlit as st
from groq import Groq

# --- Page Setup ---
st.set_page_config(page_title="AI Business Idea Validator", page_icon="💡", layout="centered")

st.title("💡 AI Business Idea Validator")
st.write("Enter any business idea and AI will analyze its potential!")
st.caption("Made by Twisha Jain")

# --- API Key ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- Input ---
st.header("Enter Your Business Idea")
idea = st.text_area("Business Idea", height=150,
        placeholder="Example: A subscription box for Indian street food snacks delivered monthly...")

industry = st.selectbox("Select Industry", [
    "Food & Beverage",
    "Technology",
    "Education",
    "Healthcare",
    "Fashion & Retail",
    "Finance",
    "Entertainment",
    "Real Estate",
    "Other"
])

target_market = st.selectbox("Target Market", [
    "India",
    "Global",
    "USA",
    "Europe",
    "Southeast Asia"
])

# --- Validate Button ---
if st.button("🚀 Validate My Idea"):
    if not idea:
        st.warning("Please enter a business idea first!")
    else:
        with st.spinner("AI is analyzing your idea..."):
            prompt = f"""
            You are an expert business analyst and startup mentor.
            Analyze this business idea thoroughly:
            
            IDEA: {idea}
            INDUSTRY: {industry}
            TARGET MARKET: {target_market}
            
            Respond in this exact format:
            
            VIABILITY SCORE: [0-100]
            
            MARKET OPPORTUNITY:
            [2-3 sentences about market size and opportunity]
            
            TARGET AUDIENCE:
            [Who exactly would buy this]
            
            TOP 3 COMPETITORS:
            1. [Competitor name and what they do]
            2. [Competitor name and what they do]
            3. [Competitor name and what they do]
            
            KEY STRENGTHS:
            • [strength 1]
            • [strength 2]
            • [strength 3]
            
            BIGGEST RISKS:
            • [risk 1]
            • [risk 2]
            • [risk 3]
            
            FIRST ACTION STEP:
            [One concrete thing to do in the next 7 days to start this business]
            
            VERDICT:
            [2 sentences summarizing if this is a good idea or not]
            """

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.choices[0].message.content

        # --- Display Results ---
        import re

        score_match = re.search(r"VIABILITY SCORE:\s*(\d+)", result)
        score = int(score_match.group(1)) if score_match else 0

        # Score color
        if score >= 75:
            color = "green"
            emoji = "🟢"
        elif score >= 50:
            color = "orange"
            emoji = "🟡"
        else:
            color = "red"
            emoji = "🔴"

        st.markdown("---")
        st.markdown(f"## {emoji} Viability Score: :{color}[{score}/100]")
        st.markdown("---")
        st.markdown(result)

        # --- Download Button ---
        st.download_button(
            label="📥 Download Analysis",
            data=result,
            file_name="business_idea_analysis.txt",
            mime="text/plain"
        )

st.markdown("---")
st.markdown("<center>Made with ❤️ by Twisha Jain</center>", unsafe_allow_html=True)