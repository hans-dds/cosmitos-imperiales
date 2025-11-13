import streamlit as st


def config_page():
    """Sets Streamlit page configuration."""
    st.set_page_config(page_title="GSSP", layout="wide")
    st.markdown("""
        <style>
            .stAppDeployButton { visibility: hidden; }
            #stDecoration {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
