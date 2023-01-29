import base64
import os
import sys
from io import StringIO

import streamlit as st

sys.path.append(os.path.abspath(".."))
import json

import pandas as pd
import plotly.express as px
import requests

from orchestration_server.dags.etl import ExtractTransformLoad


def show_pdf(pdf_data):
    base64_pdf = base64.b64encode(pdf_data).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


st.header("Analyze your resume")

st.write("""
         Once you have uploaded your resume, you can choose a data profession and compare your resume with job descriptions.
         Your resume will be compared with job descriptions stored in a database using TF-IDF and cosine similarity and the results will be displayed as a box plot and a histogram.
         The database contains job descriptions for the following data professions:
            - Data Engineer
            - Data Science
            - Machine Learning Engineer
            - Data Analyst
            - Business Analyst.\n
        Data is collected every day from Indeed automatically by airflow, for now only job descriptions from France are stored in the database.   
         """)

uploaded_file = st.file_uploader("Upload your resume (PDF only)", type="pdf")

job = st.selectbox(
        "Choose a data profession",
        (
            "Data Engineer",
            "Data Science",
            "Machine Learning Engineer",
            "Data Analyst",
            "Business Analyst",
        ),
    )

if uploaded_file is not None:
    pdf_data = uploaded_file.getbuffer()
    
    if st.checkbox("View your resume"):
        show_pdf(pdf_data)

    if st.button("Analyze your resume"):
        
        headers = {
            "accept": "application/json",
            # requests won't add a boundary if this header is set when you pass files=
            # 'Content-Type': 'multipart/form-data',
        }

        files = {
            "resume": pdf_data,
        }

        parsed_resume = requests.post(
            "http://resume_analysis_server:4200/resume_parsing",
            headers=headers,
            files=files,
        )
        parsed_resume = json.loads(parsed_resume.json())
        parsed_resume = parsed_resume["text"]

        etl = ExtractTransformLoad()

        st.write("You selected:", job)

        data = etl.view_docs(collection_name=job)

        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
        }

        similarities = []
        for i in range(len(data)):
            params = {
                "resume": parsed_resume,
                "job_description": data[i]["description"],
            }
            response = requests.post(
                "http://resume_analysis_server:4200/resume_job_description_similarity_tfidf",
                params=params,
                headers=headers,
            )
            similarities.append(response.json())

        # create a dataframe with the similarities
        similarities = pd.DataFrame(similarities, columns=["similarity score"])

        # plot the results as box plot
        fig = px.box(
            similarities,
            y="similarity score",
            title="Similarity score distribution between my resume and job descriptions",
        )
        st.plotly_chart(fig)

        # plot histogram of the similarities
        fig = px.histogram(
            similarities,
            x="similarity score",
            title="Similarity score distribution between my resume and job descriptions",
        )
        st.plotly_chart(fig)
