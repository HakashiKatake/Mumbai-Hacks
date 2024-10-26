import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from PIL import Image
from datetime import datetime
import json

# Initialize Streamlit configuration
st.set_page_config(
    page_title="FreshScanner",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define theme colors
COLORS = {
    "primary": "#1E88E5",
    "secondary": "#FFC107",
    "success": "#4CAF50",
    "danger": "#f44336",
    "background": "#f0f2f6"
}

# Custom CSS with improved styling
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #1a1a1a !important;
        color: #ffffff;
    }

    /* Chat Messages */
    .chat-container {
        max-width: 800px;
        margin: auto;
    }

    .user-message {
        background-color: #2d2d2d;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        color: #ffffff;
    }

    .bot-message {
        background-color: #3d3d3d;
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        color: #ffffff;
    }

    /* Cards */
    .news-card {
        background-color: #2d2d2d;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 40px;
        background-color: #2d2d2d;
        border-radius: 10px;
    }

    /* Hide Streamlit elements we don't want */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'selected_page' not in st.session_state:
    st.session_state.selected_page = "Chatbot"
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'saved_responses' not in st.session_state:
    st.session_state.saved_responses = []

# Sidebar for navigation
st.sidebar.title("🍲 Food Safety Hub")
nav_links = ["Chatbot", "News", "Image Recognition", "Saved Responses", "Food Adulteration"]
selected_page = st.sidebar.selectbox("Select a page:", nav_links)

# Update selected page
st.session_state.selected_page = selected_page

# Initialize Llama2 Model
@st.cache_resource
def get_llm():
    return OllamaLLM(model="llama2")

llm = get_llm()

# Enhanced prompt template with more context
SYSTEM_PROMPT = """You are an expert food safety advisor with extensive knowledge of:
- Food storage and handling
- Temperature control
- Cross-contamination prevention
- Food-borne illness prevention
- Kitchen hygiene
- Restaurant safety standards
- Food adulteration detection methods and tips

Provide detailed, accurate responses with specific examples and measurements when relevant.
If discussing critical safety issues, emphasize important warnings.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}")
])

def save_response(response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.saved_responses.append({
        "timestamp": timestamp,
        "response": response
    })

def handle_chat_input():
    if st.session_state.user_input:
        user_message = st.session_state.user_input
        st.session_state.chat_history.append({"role": "user", "message": user_message})

        with st.spinner("Processing your question..."):
            full_prompt = prompt.format(question=user_message)
            response = llm.invoke(full_prompt)

        st.session_state.chat_history.append({"role": "bot", "message": response})
        st.session_state.user_input = ""

# Page Content
if st.session_state.selected_page == "Chatbot":
    st.title("🍽️ Food Safety Assistant")
    
    # Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Sample questions
    st.markdown("### Sample Questions")
    cols = st.columns(3)
    sample_questions = [
        "How long can I keep leftovers?",
        "What's the safe cooking temperature for chicken?",
        "How do I prevent cross-contamination?"
    ]
    for col, question in zip(cols, sample_questions):
        if col.button(question):
            st.session_state.user_input = question
            handle_chat_input()
    
    # Chat input
    st.text_input(
        "💬 Ask your food safety question:",
        key="user_input",
        on_change=handle_chat_input
    )
    
    # Display chat history
    for chat in reversed(st.session_state.chat_history):
        role, message = chat['role'], chat['message']
        st.markdown(
            f'<div class="{role}-message">'
            f'<strong>{role.upper()}</strong>: {message}'
            f'</div>',
            unsafe_allow_html=True
        )
        if role == "bot":
            if st.button("Save Response", key=f"save_{len(st.session_state.chat_history)}"):
                save_response(message)
    
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.selected_page == "News":
    st.title("📰 Food Safety News & Alerts")
    
    # News filters
    col1, col2 = st.columns([2, 1])
    with col1:
        category = st.selectbox(
            "Filter by category:",
            ["All", "Recalls", "Advisories", "Guidelines", "Research"]
        )
    with col2:
        st.markdown("### Latest Updates")
    
    # Example news data (replace with API or database in production)
    news_articles = [
        {
            "category": "Recalls",
            "title": "Spinach Recall Due to Contamination",
            "date": "2024-10-25",
            "summary": "A major spinach supplier has recalled their products due to contamination."
        },
        {
            "category": "Advisories",
            "title": "New Guidelines on Food Storage",
            "date": "2024-10-24",
            "summary": "The USDA has released new guidelines for safe food storage."
        }
    ]

    for article in news_articles:
        if category == "All" or article['category'] == category:
            severity_class = "alert-info" if article['category'] == "info" else "alert-warning"
            st.markdown(f'<div class="alert {severity_class}"><strong>{article["title"]}</strong><br>{article["summary"]} <em>({article["date"]})</em></div>', unsafe_allow_html=True)

elif st.session_state.selected_page == "Image Recognition":
    st.title("📷 Food Safety Image Recognition")
    
    # Image upload functionality
    uploaded_file = st.file_uploader("Upload an image for analysis", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.write("Analyzing the image... (simulate analysis with a placeholder)")
        st.markdown("<strong>Analysis Result:</strong> Safe to consume!", unsafe_allow_html=True)

elif st.session_state.selected_page == "Saved Responses":
    st.title("💾 Saved Responses")
    
    if st.session_state.saved_responses:
        for item in st.session_state.saved_responses:
            st.markdown(f'**{item["timestamp"]}**: {item["response"]}')
    else:
        st.write("No saved responses yet.")

elif st.session_state.selected_page == "Food Adulteration":
    st.title("🔍 Food Adulteration Detection")

    # User input for specific food item or adulteration checks
    st.write("Ask about food adulteration detection or select a food item for common checks.")
    user_question = st.text_input("💬 Ask your question about food adulteration:", key="adulteration_input")

    if st.button("Submit"):
        if user_question:
            with st.spinner("Processing your question..."):
                full_prompt = prompt.format(question=user_question)
                response = llm.invoke(full_prompt)
                st.markdown(f"<strong>Bot:</strong> {response}", unsafe_allow_html=True)
        else:
            st.error("Please enter a question.")

# Footer
st.markdown(
    '<div class="footer">© 2024 Food Safety Hub. All rights reserved.</div>',
    unsafe_allow_html=True
)
