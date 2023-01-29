import contextlib
import logging
import time
from collections import Counter

import pandas as pd
import plotly.express as px
import pymongo
import spacy
from selenium import webdriver
from selenium.webdriver.common.by import By
from spacy.lang.fr.stop_words import STOP_WORDS

# import sys
# sys.path.append("pipeline/etl.py")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    filename="logs.log",
    filemode="a",
)


class ExtractTransformLoad:
    def __init__(self, remote_url=None, path=None):
        """
         This function initialize the webdriver and the mongo client

        :param remote_url: url of the remote webdriver (if you want to use a remote webdriver)
        :param path: path of the webdriver (if you want to use a local webdriver)

         :return: None
        """
        if remote_url:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-notifications")
            options.add_argument("--incognito")
            options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
            )
            self.webdriver = webdriver.Remote(
                command_executor=remote_url, options=options
            )
        elif path:
            self.webdriver = webdriver.Chrome(path)
        self.mongodb_client = pymongo.MongoClient(
            "mongodb://mongo_db:27017/", username="abdessamad", password="abdessamad"
        )

    def fill_search_bar(self, job, location):
        """
        This function fill the search bar of indeed.com

        :param job: job to search
        :param location: location of the job

        :return: None
        """
        self.webdriver.get("https://fr.indeed.com/")
        self.webdriver.find_element(By.ID, "text-input-what").send_keys(job)
        self.webdriver.find_element(By.ID, "text-input-where").send_keys(location)
        self.webdriver.find_element(
            By.CLASS_NAME, "yosegi-InlineWhatWhere-primaryButton"
        ).click()

    def fill_search_bar_by_link(self, job, location, from_last_days):
        """
        This function fill the search bar of indeed.com directly by the link

        :param job: job to search
        :param location: location of the job
        :param from_last_days: number of days since the job was posted

        :return: None
        """
        self.webdriver.get(
            f"https://fr.indeed.com/jobs?q={job}&l={location}&fromage={from_last_days}&vjk=f25fd64c4d687de6"
        )

    def remove_pop_up(self):
        """
        This function remove the pop up of indeed.com

        :param: None

        :return: None
        """
        with contextlib.suppress(Exception):
            self.webdriver.find_element(By.ID, "onetrust-reject-all-handler").click()

    def get_job_descriptions(self):
        """
        This function get the job descriptions of the jobs offers of indeed.com

        :param: None

        :return: list of job descriptions
        """
        data = []
        jobs_offers = self.webdriver.find_elements(
            By.CLASS_NAME, "slider_container css-g7s71f eu4oa1w0".replace(" ", ".")
        )
        for job_offer in jobs_offers:
            try:
                data.append(
                    {
                        "description": self.webdriver.find_element(
                            By.ID, "jobDescriptionText"
                        ).text
                    }
                )
                job_offer.click()
                time.sleep(2)
            except Exception:
                logging.error("Error")
        return data

    def technologies_used(self, description):
        """
        This function check if a skill exists in a job description

        :param skills: list of skills
        :param description: job description

        :return: list of skills that exist in the job description
        """

        # sourcery skip: dict-comprehension, inline-immediately-returned-variable
        technologies = [
            "python",
            "r",
            "sql",
            "apprentissage automatique",
            "visualisation de données",
            "big data",
            "nettoyage de données",
            "analyse de données",
            "statistiques",
            "apprentissage profond",
            "airflow",
            "mlops",
            "scikit-learn",
            "tensorflow",
            "keras",
            "pandas",
            "numpy",
            "scipy",
            "matplotlib",
            "seaborn",
            "statsmodels",
            "power bi",
            "tableau",
            "mlflow",
            "spark",
            "flink",
            "kafka",
            "hadoop",
            "apache storm",
            "apache beam",
        ]

        count = {}
        for technology in technologies:
            count[technology] = description.lower().split(" ").count(technology)
        return count

    def store_data_in_mongo(
        self,
        data,
        database_name="data_jobs",
        collection_name="data_science_jobs",
        bulk=False,
    ):
        # sourcery skip: class-extract-method
        """
        Store data in a mongo database

        :param data: data to store
        :param database_name: name of the database
        :param collection_name: name of the collection
        :param bulk: if True, the data will be stored in bulk

        :return: None
        """
        db = self.mongodb_client[database_name]
        collection = db[collection_name]
        if bulk:
            collection.insert_many(data, ordered=False)
        else:
            for document in data:
                try:
                    collection.insert_one(document)
                except Exception as e:
                    print(e)

    def view_docs(self, collection_name, database_name="data_jobs"):
        """
        This function view the documents of a collection

        :param database_name: name of the database
        :param collection_name: name of the collection

        :return: list of documents
        """
        database = self.mongodb_client[database_name]
        collection = database[collection_name]
        return list(collection.find())

    def delete_collection(self, collection_name, database_name="data_jobs"):
        """
        This function delete a collection from a database in mongo

        :param database_name: name of the database
        :param collection_name: name of the collection

        :return: None
        """
        database = self.mongodb_client[database_name]
        database.drop_collection(collection_name)

    def number_of_documents(self, database_name, collection_name):
        """
        This function return the number of documents of a collection

        :param database_name: name of the database
        :param collection_name: name of the collection

        :return: number of documents
        """
        database = self.mongodb_client[database_name]
        collection = database[collection_name]
        return collection.count_documents({})

    def close(self):
        """
        This function close the webdriver

        :param: None

        :param: None
        """
        with contextlib.suppress(Exception):
            self.webdriver.close()
            self.webdriver.quit()

    def create_wordcloud_bar_chart(self, data):
        """
        The function create a bar chart of the most common words in the job descriptions

        :param data: list of jobs' data

        :return: bar chart
        """

        # load spaCy's French language model
        nlp = spacy.load("fr_core_news_sm")

        # join all documents into one string
        temp = [doc["description"].lower() for doc in data]
        text = " ".join(temp)

        # tokenize the document using spaCy
        tokens = [
            token.text.lower()
            for token in nlp(text)
            if not token.is_punct | token.is_space | token.is_stop
        ]

        # count the occurrences of each token
        counter = Counter(tokens)

        # get the top 30 tokens
        top_tokens = counter.most_common(30)

        # get the token names and counts
        token_names = [token[0] for token in top_tokens]
        token_counts = [token[1] for token in top_tokens]

        # create the bar chart
        return px.bar(
            x=token_names,
            y=token_counts,
            title="Most used words in job descriptions",
            labels={"x": "Word", "y": "Count"},
        )

    def vizualize_data(self, data):
        """
        This function takes the data from the mongo database and vizualize it

        :param data: list of jobs' data

        :return: a plotly figure
        """
        df = pd.DataFrame(data)
        dict_count = {}
        for data in df["technologies_used"]:
            for key, value in data.items():
                if key in dict_count:
                    dict_count[key] += value
                else:
                    dict_count[key] = value
        # display the data
        df = pd.DataFrame(dict_count, index=[0]).T
        df.columns = ["count"]
        df = df.sort_values(by="count", ascending=False)
        df = df.reset_index()
        df.columns = ["technology", "count"]
        return px.bar(
            df,
            x="technology",
            y="count",
            title="Most used Technologies used in data science jobs",
        )
