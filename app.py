import streamlit as st
import tempfile
import os
from google import genai
from google.genai import types

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TenderAI - Executive RFP Intelligence Engine",
    page_icon="📑",
    layout="wide"
)

# --- SIDEBAR & API KEY ---
st.sidebar.title("⚙️ Engine Settings")
api_key = st.sidebar.text_input("Gemini API Key", type="password", placeholder="Paste API Key here...")

# Alternatively, fallback to hardcoded/environment key if preferred
if not api_key:
    api_key = os.environ.get("GEMINI_API_KEY", "")

st.sidebar.markdown("---")
st.sidebar.info("🚀 **TenderAI Engine** analyzes 50-100+ page RFP documents to extract eligibility criteria, penalty clauses, and bid feasibility scores.")

# --- MAIN HEADER ---
st.title("📑 TenderAI: RFP & Tender Intelligence Engine")
st.markdown("Upload any commercial or government tender PDF to generate a structured **2-Page Executive Risk & Compliance Matrix** in seconds.")

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Drop Tender / RFP PDF here", type=["pdf"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    with col1:
        st.success(f"✅ Loaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
    
    if st.button("🚀 Analyze Tender Document", type="primary"):
        if not api_key:
            st.error("Please enter a valid Gemini API Key in the sidebar to proceed.")
        else:
            with st.spinner("Uploading and analyzing contract clauses via Gemini 3.6 Flash..."):
                try:
                    # 1. Initialize Gemini Client
                    client = genai.Client(api_key=api_key)

                    # 2. Save uploaded buffer to a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_path = tmp_file.name

                    # 3. Upload file via Gemini File API
                    gemini_file = client.files.upload(file=tmp_path)

                    # 4. Specialized Tender Prompt
                    prompt = """
                    You are an elite Government Tender & Commercial Contract Analyst. 
                    Analyze this complete RFP/Tender document and generate a structured, executive-level intelligence brief.

                    Structure the output strictly in the following format:

                    # 1. EXECUTIVE TENDER SNAPSHOT
                    - Tender/RFP Title:
                    - Issuing Authority/Client:
                    - Submission Deadline & Time:
                    - Estimated Tender Value / EMD (Earnest Money Deposit) Amount:
                    - Contract Duration:

                    # 2. ELIGIBILITY & CRITICAL QUALIFICATIONS (Pass/Fail Criteria)
                    List the non-negotiable criteria required to bid:
                    - Minimum Annual Turnover / Financial Net Worth:
                    - Past Experience / Similar Project Credentials Required:
                    - Mandatory Certifications / Licenses:

                    # 3. HIGH-RISK & RED FLAG CLAUSES (Penalty & SLA Matrix)
                    - Liquidated Damages / Penalties (Rate per day/week of delay):
                    - Termination Conditions:
                    - Payment Terms & Retention Money:
                    - Major Compliance Bottlenecks or Unfavorable Legal Clauses:

                    # 4. SCOPE OF WORK & DELIVERABLES SUMMARY
                    - 4-6 bullet point summary of core deliverables.

                    # 5. BID / NO-BID RECOMMENDATION SCORE
                    - Feasibility Rating (High / Medium / High Risk):
                    - Top 3 reasons why bidder should or should not bid.
                    """

                    # 5. Generate content
                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=[gemini_file, prompt],
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                        )
                    )

                    # Clean up temp file
                    os.remove(tmp_path)

                    # 6. Display Output
                    st.markdown("---")
                    st.header("📊 Executive Bid Intelligence Report")
                    st.markdown(response.text)

                    # Download button for the output report
                    st.download_button(
                        label="📥 Download Analysis Report (Markdown)",
                        data=response.text,
                        file_name=f"Tender_Analysis_{uploaded_file.name.replace('.pdf', '')}.md",
                        mime="text/markdown"
                    )

                except Exception as e:
                    st.error(f"Error processing RFP: {e}")