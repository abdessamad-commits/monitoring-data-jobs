import json
import shutil
import time
from io import StringIO
from typing import Union

import requests
from fastapi import FastAPI, UploadFile
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/resume_parsing")
def resume_parsing(resume: UploadFile):
    # initialize resource manager and text converter
    resource_manager = PDFResourceManager()
    string_io = StringIO()
    text_converter = TextConverter(resource_manager, string_io, laparams=LAParams())

    # create PDF interpreter and process the pdf
    interpreter = PDFPageInterpreter(resource_manager, text_converter)
    with resume.file as f:
        for page in PDFPage.get_pages(f):
            interpreter.process_page(page)

    # get the text from the StringIO and close the text converter
    text = string_io.getvalue()
    text_converter.close()

    # return the full text as a JSON object
    return json.dumps({"text": text})


@app.post("/resume_job_description_similarity_tfidf")
def doc_similarity_tfidf(resume: str, job_description: str):
    tfidf = TfidfVectorizer().fit_transform([resume, job_description])
    return cosine_similarity(tfidf)[0][1]


@app.post("/resume_job_description_similarity_transformers")
def doc_similarity_transformers(resume: str, job_description: str):
    API_URL = "https://api-inference.huggingface.co/models/Sahajtomar/french_semantic"
    headers = {"Authorization": "Bearer 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"}

    def query(payload):
        requests.post(API_URL, headers=headers)
        time.sleep(20)
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    payload = {
        "inputs": {"source_sentence": resume, "sentences": [job_description]},
    }

    output = query(payload)

    return output
