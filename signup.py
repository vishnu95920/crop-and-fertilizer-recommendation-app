import streamlit as st
import pandas as pd
import numpy as np
import joblib

# Streamlit App Setup
st.set_page_config(page_title="Crop & Fertilizer Recommendation", page_icon="🌾", layout="wide")

# CSS Theme (Same as before)
st.markdown("""
    <style>
    /* Main background - Force gradient */
    [data-testid="stAppViewContainer"] > div:first-child {
        background: linear-gradient(to bottom right, #E8F5E9, #F5F6E1) !important;
    }
    .stApp {
        background: linear-gradient(to bottom right, #E8F5E9, #F5F6E1) !important;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #43A047;
        color: #FFFFFF;
        border-right: 2px solid #2E7D32;
    }
    /* Header styling */
    h1 {
        color: #1B5E20;
        font-family: 'Georgia', serif;
        text-shadow: 1px 1px 2px #A5D6A7;
    }
    h2 {
        color: #388E3C;
        font-family: 'Arial', sans-serif;
    }
    /* Input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        color: #5D4037;
        font-weight: bold;
        font-family: 'Verdana', sans-serif;
    }
    /* Button styling */
    .stButton>button {
        background-color: #66BB6A;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #4CAF50;
        box-shadow: 4px 4px 8px rgba(0, 0, 0, 0.3);
    }
    /* Success/Error message */
    div[data-testid="stMarkdownContainer"] > .stSuccess {
        background-color: #DCEDC8;
        color: #1B5E20;
        border: 2px dashed #81C784;
        border-radius: 8px;
        padding: 10px;
    }
    div[data-testid="stMarkdownContainer"] > .stError {
        background-color: #FFCDD2;
        color: #B71C1C;
        border: 2px dashed #EF5350;
        border-radius: 8px;
        padding: 10px;
    }
    /* Input boxes */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFDE7;
        border: 1px solid #AED581;
        border-radius: 5px;
    }
    /* Ensure content area is transparent */
    [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# Dummy user database (for testing, tu baad mein real database use kar sakta hai)
if 'users' not in st.session_state:
    st.session_state.users = {"admin": "password123"}  # Default user

# Sidebar Navigation
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Login", "Sign Up"])

# Login Page
if page == "Login":
    st.title("🌾 Login to Your Account")
    st.markdown("Enter your credentials below to access the recommendation system.", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])  # Center the form
    with col1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.success("Login successful! Welcome, {}".format(username))
                # Yeh jagah tu apne main app (Crop & Fertilizer) ke code se replace kar sakta hai
                st.session_state.logged_in = True
            else:
                st.error("Invalid username or password!")
    
    st.markdown("New user? Switch to **Sign Up** from the sidebar.", unsafe_allow_html=True)

# Sign Up Page
elif page == "Sign Up":
    st.title("🌾 Sign Up for an Account")
    st.markdown("Create a new account to start using the recommendation system.", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])  # Center the form
    with col1:
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("Sign Up"):
            if new_username in st.session_state.users:
                st.error("Username already exists! Try a different one.")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            elif not new_username or not new_password:
                st.error("Please fill in all fields!")
            else:
                st.session_state.users[new_username] = new_password
                st.success("Sign up successful! Please go to Login page.")
    
    st.markdown("Already have an account? Switch to **Login** from the sidebar.", unsafe_allow_html=True)

# Main App Access (After Login)
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.title("🌾 Crop & Fertilizer Recommendation System")
    st.markdown("Get personalized crop and fertilizer recommendations based on your soil and environmental conditions!", unsafe_allow_html=True)

    # Yeh jagah pe tu apna original Crop & Fertilizer code daal sakta hai
    st.write("Welcome to the main app! Add your Crop & Fertilizer logic here.")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ by [Vishnu]", unsafe_allow_html=True)