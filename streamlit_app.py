import streamlit as st
import os
from templates.home import home_page
from templates.pandas_page import pandas_page
from templates.news_api import news_api_page  # Importing the news API page

# Page layout settings
st.set_page_config(page_title="Home Page", layout="wide")

# Function to load custom CSS
def load_css():
    css_path = "assets/main.css"
    if os.path.exists(css_path):
        with open(css_path) as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.error("CSS file not found.")

# Load custom CSS
load_css()

# Sidebar menu for navigation
menu = st.sidebar.radio("Select a Page", ["Home", "State Results", "News"])

# Container to manage the layout
with st.container():
    # Render the selected page based on the user's choice
    if menu == "Home":
        home_page()  # Render the home page
    elif menu == "State Results":
        pandas_page()  # Render the page for state results (using Pandas)
    elif menu == "News":
        news_api_page()  # Render the page for the news using your API
