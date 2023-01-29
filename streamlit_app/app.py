import sys
import os
import streamlit as st
import pymongo
import pandas as pd
import plotly.express as px
import uuid
import logging
import time
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath('..'))
from orchestration_server.dags.etl import ExtractTransformLoad
#from wordcloud import WordCloud
#import matplotlib.pyplot as plt


st.title("Data Jobs Market Analysis")
st.write("This project is a system that utilizes web scraping to collect job descriptions for data positions from Indeed.com. The system then analyses the collected data and displays the most in-demand technologies for that specific position in the form of interactive visuals.")

tab1, tab2 = st.tabs(["Analyze The Job Market", "Analyzing your CV"])

with tab1:

    job = st.selectbox(
    'What is the position you are interested in?',
    ('Data Engineer', 'Data Science', 'Data Analyst', 'Business Analyst', 'Machine Learning Engineer'))
    st.write('You selected: ', job)

    from_last_days = st.selectbox(
        'How many days back do you want to the system to look for jobs?',
        ('1', '3'))

    st.write("Due to the fact that the data collection is quite intensive the system only collects data from the last 3 days maximum, the data is stored in mogoDB constitung a database for more insights, you can vizualize all of the data stored in the database by selecting the option")

    if st.button('Find the most in-demand technologies'):
        # initializing the pipeline instance
        with st.spinner('The system is collecting the data and analyzing it, this might take a while...'):
            etl = ExtractTransformLoad(remote_url="http://20.224.70.229:4444")
            logging.info("Starting the pipeline")
            # fill the search bar with the job and location
            etl.fill_search_bar_by_link(job=job, location="France", from_last_days=3)
            logging.info("Filling the search bar")
            # remove the pop up
            etl.remove_pop_up()
            logging.info("Removing the pop up")
            # get the job descriptions
            data_from_days = etl.get_job_descriptions()
            logging.info("Getting the job descriptions")
            # transform the data by adding the technologies present in the job description
            for doc in data_from_days:
                doc["technologies_used"] = etl.technologies_used(doc["description"]) 
            # store the data into the temporary collection
            etl.store_data_in_mongo(data=data_from_days, collection_name=job)
            logging.info("Storing the data in the temporary collection")
            # close the connection with selenium grid
            etl.close()
            logging.info("Closing the connection with selenium grid")
            logging.info("Vizualizing the data")
            st.subheader(f"The system has collected the data and analyzed it, here are the results from the last {from_last_days} days:")
            st.write(etl.vizualize_data(data_from_days))
            st.write(etl.create_wordcloud_bar_chart(data_from_days)) 
            st.subheader("This is the insight from all the data stored in the database:")
            data_from_mongo = etl.view_docs(collection_name=job)
            st.write(etl.vizualize_data(data_from_mongo))
            st.write(etl.create_wordcloud_bar_chart(data_from_mongo))



with tab2:
    st.header("Data Science Jobs")
    st.write("This tab shows the data science jobs scraped from Indeed.com, the data is collected daily by an Airflow DAG.")
    #st.write(vizualize_data_from_mongo(data))