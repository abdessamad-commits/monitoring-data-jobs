import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to my resume analysis app")

st.sidebar.success("Select a service above.")

st.markdown(
    """
    This app was built to help me track my resume performance. I have my resume uploaded so I can track 
    automatically how my resume is doing compared to job descriptions that are produced everyday on Indeed.com.\n
    It also helps me to do a sort of A/B testing of different versions of my resume.
    You can also upload your resume and compare it with job descriptions for different data professions.\n
    This app is built based on a micro-service architecture with mainly the following technologies: streamlit, fastapi, airflow, mongodb, docker and docker-compose. The code is available on [github]().
    you can download the code and run it locally on your machine. you can also easily modify the code to fit your needs if you are looking 
    for a job in a different field. 
"""
)
