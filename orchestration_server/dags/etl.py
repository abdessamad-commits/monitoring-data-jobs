import contextlib
import time

import pymongo
from selenium import webdriver
from selenium.webdriver.common.by import By


class ExtractTransformLoad:
    def __init__(self, stage="extract", remote_url=None, path=None):
        """
        This function initialize the webdriver and the mongo client

        :param navigator: navigator to use (chrome or firefox)
        :param remote_url: url of the remote webdriver (if you want to use a remote webdriver)
        :param path: path of the webdriver (if you want to use a local webdriver)

        :return: None
        """
        if stage == "extract":
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
            else:
                self.webdriver = webdriver.Chrome(path)
        self.mongodb_client = pymongo.MongoClient(
            "mongodb://20.224.70.229:27017/",
            username="abdessamad",
            password="abdessamad",
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
                print("Error")
        return data

    def technologies_used(self, description):
        """
        This function check if a skill exists in a job description

        :param skills: list of skills
        :param description: job description

        :return: list of skills that exist in the job description
        """
        technologies = [
            "python",
            "r",
            "sql",
            "tableau",
            "excel",
            "sas",
            "spark",
            "hadoop",
            "tensorflow",
            "keras",
            "pytorch",
            "scikit-learn",
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",
            "plotly",
            "dash",
            "bokeh",
            "scipy",
            "statsmodels",
            "scrapy",
            "nltk",
            "spacy",
            "gensim",
            "tensorflow",
            "keras",
            "pytorch",
            "scikit-learn",
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",
            "plotly",
            "dash",
            "bokeh",
            "scipy",
            "statsmodels",
            "scrapy",
            "nltk",
            "spacy",
            "gensim",
            "tensorflow",
            "keras",
            "pytorch",
            "scikit-learn",
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",
            "plotly",
            "dash",
            "bokeh",
            "scipy",
            "statsmodels",
            "scrapy",
            "nltk",
            "spacy",
            "gensim",
            "tensorflow",
            "keras",
            "pytorch",
            "scikit-learn",
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",
            "plotly",
            "dash",
            "bokeh",
            "scipy",
            "statsmodels",
            "scrapy",
            "nltk",
            "spacy",
            "gensim",
            "tensorflow",
            "keras",
            "pytorch",
            "scikit-learn",
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",
            "plotly",
            "dash",
            "bokeh",
            "scipy",
            "statsmodels",
            "scrapy",
            "nltk",
            "spacy",
            "gensim",
            "tensorflow",
            "keras",
            "pytorch",
            "scikit-learn",
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",
            "plotly",
            "dash",
            "bokeh",
            "scipy",
            "statsmodels",
            "scrapy",
            "nltk",
            "spacy",
            "gensim",
            "tensorflow",
            "keras",
            "pytorch",
            "scikit-learn",
            "numpy",
            "pandas",
            "matplotlib",
            "seaborn",
            "plotly",
            "dash",
            "bokeh",
            "scipy",
            "statsmodels",
            "scrapy",
            "nltk",
            "spacy",
            "gensim",
        ]
        # sourcery skip: dict-comprehension, inline-immediately-returned-variable
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
        self.webdriver.close()
        self.webdriver.quit()
