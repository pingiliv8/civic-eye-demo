import streamlit as st
from google import genai
from PIL import Image
import hashlib
import datetime
import pandas as pd
import numpy as np
import time
import urllib.parse


MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=MY_API_KEY)

st.set_page_config(
    page_title="CivicEye AI",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .stButton>button { background: linear-gradient(45deg, #00C9FF, #92FE9D); color: black; font-weight: bold; }
    div[data-testid="stMetricValue"] { color: #00C9FF; }
    </style>
""", unsafe_allow_html=True)


def analyze_image_real(uploaded_file):
    """
    This does your teammate's job.
    It sends the image to Gemini Vision to see what is wrong.
    """
    try:
        
        image = Image.open(uploaded_file)
        
        
        prompt = """
        Analyze this image. 
        1. Identify the civic issue (e.g., Pothole, Garbage Dump, Broken Streetlight, Water Leak).
        2. Estimate the severity (Low, Medium, High).
        3. Return a short, 1-sentence description.
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[prompt, image]
        )
        return response.text
    except Exception as e:
        return f"Error analyzing image: {e}"

def generate_complaint(issue_description, location, language):
    """
    Writes the official letter based on what the Vision AI saw.
    """
    prompt = f"""
    You are an expert citizen activist in India.
    CONTEXT: The AI Vision system detected: "{issue_description}" at "{location}".
    
    OUTPUT 1: A formal complaint letter to the Municipal Commissioner (GHMC).
    LANGUAGE: Write this letter in {language}.
    
    OUTPUT 2: A viral tweet text (English + {language} mixed).
    
    Format:
    [LETTER START]
    (Letter content)
    [LETTER END]
    
    [TWEET START]
    (Tweet content)
    [TWEET END]
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error: {e}"

def create_blockchain_id(complaint_text):
    """
    Generates a fake Ethereum-style transaction hash.
    """
    timestamp = str(datetime.datetime.now())
    data = complaint_text + timestamp
    full_hash = hashlib.sha256(data.encode()).hexdigest()
    return "0x" + full_hash  # Make it look like a real crypto tx


with st.sidebar:
    st.title("CivicEye Control")
    st.info("Upload evidence to auto-generate a legal complaint.")
    
    language = st.selectbox("🌐 Document Language", ["English", "Telugu", "Hindi"])
    uploaded_file = st.file_uploader("📸 Upload Evidence", type=["jpg", "png", "jpeg"])
    location = st.text_input("📍 Location", placeholder="e.g. ECIL X Roads")
    
    st.divider()
    st.caption("System Status: Online 🟢")

st.title("👁️ CivicEye: AI Grievance System")
st.markdown("### From Photo to Filed Complaint in 10 Seconds.")

if uploaded_file and location:
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📷 Evidence")
        st.image(uploaded_file, caption="Input Feed", use_container_width=True)
    with col2:
        st.subheader("📍 Geotagged Map")
        st.map(pd.DataFrame(np.random.randn(1, 2) / [50, 50] + [17.46, 78.56], columns=['lat', 'lon']))

    if st.button("🚀 Analyze & Generate Complaint", type="primary"):
        
       
        with st.status("🔍 AI Vision Analysis Running...", expanded=True) as status:
            st.write("Extracting image features...")
            time.sleep(1)
            
            
            issue_text = analyze_image_real(uploaded_file)
            
            st.write("Classifying severity...")
            status.update(label="Analysis Complete!", state="complete", expanded=False)
        
        
        st.subheader("📊 AI Analysis Report")
        st.info(f"**DETECTED:** {issue_text}")
        
        
        full_text = generate_complaint(issue_text, location, language)
        
        
        try:
            letter = full_text.split("[LETTER END]")[0].replace("[LETTER START]", "")
            tweet = full_text.split("[TWEET START]")[1].replace("[TWEET END]", "")
        except:
            letter = full_text
            tweet = "Fix this issue immediately! #CivicEye"

       
        c1, c2 = st.columns(2)
        with c1:
            st.success("✅ Formal Letter Ready")
            with st.expander("📄 View Letter", expanded=True):
                st.markdown(letter)
        
        with c2:
            st.success("✅ Blockchain Proof Generated")
            b_id = create_blockchain_id(letter)
            st.code(b_id, language="text")
            st.caption("Immutable Transaction Hash (Simulated)")

       
        st.subheader("📢 Take Action")
        tweet_encoded = urllib.parse.quote(tweet)
        st.link_button("🐦 Post to Twitter (X)", f"https://twitter.com/intent/tweet?text={tweet_encoded}")

else:
    st.warning("👈 Please upload an image from the Sidebar to start.")