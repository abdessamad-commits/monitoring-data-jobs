import base64
import json
import os
import sys

import streamlit as st

sys.path.append(os.path.abspath(".."))
import pandas as pd
import plotly.express as px
import requests

from pipeline.etl import ExtractTransformLoad


def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


st.header("Analysis of my resume")

st.write(
    """This is the analysis of my resume. I have my resume uploaded so I can track 
         automatically how my resume is doing compared to job descriptions. It also helps me to do a sort of A/B testing of different versions of my resume."""
)

if st.checkbox("View my resume"):
    show_pdf("/streamlit_app/pages/abdessamad_cv_french-9.pdf")

headers = {
    "accept": "application/json",
    # requests won't add a boundary if this header is set when you pass files=
    # 'Content-Type': 'multipart/form-data',
}

files = {
    "resume": open("/streamlit_app/pages/abdessamad_cv_french-9.pdf", "rb"),
}

parsed_resume = requests.post(
    "http://resume_analysis_server:4200/resume_parsing", headers=headers, files=files
)
parsed_resume = json.loads(parsed_resume.json())
parsed_resume = parsed_resume["text"]

etl = ExtractTransformLoad()

job = st.selectbox(
    "Choose a data profession",
    (
        "Data Engineer",
        "Data Scientist",
        "Machine Learning Engineer",
        "Data Analyst",
        "Business Analyst",
    ),
)

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
