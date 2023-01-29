import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from selenium.webdriver.common.by import By

from etl import ExtractTransformLoad


# Task to extract the data
def extract_data(**kwargs):
    data_extractor = ExtractTransformLoad(remote_url="http://20.224.70.229:4444")
    data_extractor.fill_search_bar_by_link(
        job=kwargs["job"], location="France", from_last_days=1
    )
    data_extractor.remove_pop_up()
    data = data_extractor.get_job_descriptions()
    # temporary collection where the data will be stored before being transformed
    temp_collection_name_1, temp_collection_name_2 = (
        str(uuid.uuid4()),
        str(uuid.uuid4()),
    )
    # store the data into the temporary collection
    data_extractor.store_data_in_mongo(data, collection_name=temp_collection_name_1)
    # close the connection with selenium grid
    data_extractor.close()
    # store the name of the temporary collection in the XCom
    kwargs["ti"].xcom_push(
        key="temp_collection",
        value={
            "collection_name_1": temp_collection_name_1,
            "collection_name_2": temp_collection_name_2,
        },
    )


def transform_data(**kwargs):
    # retrieve the temporary collection names from the XCom
    temp_collection_names = kwargs["ti"].xcom_pull(
        key="temp_collection", task_ids=kwargs["task_id"]
    )
    temp_collection_name_1 = temp_collection_names["collection_name_1"]
    temp_collection_name_2 = temp_collection_names["collection_name_2"]
    # initialize the data extractor
    data_extractor = ExtractTransformLoad()
    # get the data from the temporary collection
    raw_data = data_extractor.view_docs(collection_name=temp_collection_name_1)
    # transform the data by adding the technologies present in the job description
    for doc in raw_data:
        doc["technologies_used"] = data_extractor.technologies_used(doc["description"])
    # store the data into the temporary collection
    data_extractor.store_data_in_mongo(raw_data, collection_name=temp_collection_name_2)


# Task to load the data
def load_data(**kwargs):
    # retrieve the temporary collection names from the XCom
    temp_collection_names = kwargs["ti"].xcom_pull(
        key="temp_collection", task_ids=kwargs["task_id"]
    )
    temp_collection_name_1 = temp_collection_names["collection_name_1"]
    temp_collection_name_2 = temp_collection_names["collection_name_2"]
    # initialize the data extractor
    data_extractor = ExtractTransformLoad()
    # get the data from the temporary collection
    raw_data = data_extractor.view_docs(collection_name=temp_collection_name_2)
    # store the data into the final collection
    data_extractor.store_data_in_mongo(raw_data, collection_name=kwargs["job"])
    # drop the temporary collections
    data_extractor.delete_collection(temp_collection_name_1)
    data_extractor.delete_collection(temp_collection_name_2)


# define the default arguments for the DAG
default_args = {
    "owner": "abdessamad",  # the owner of the DAG
    "start_date": datetime.now(),  # the start date of the DAG
    "depends_on_past": True,  # the DAG depends on the past
    "retries": 2,  # the number of retries
    "retry_delay": timedelta(hours=1),  # the delay between retries
    "catchup": False,  # the DAG does not catch up with the past
    "schedule_interval": "@daily",  # the schedule interval of the DAG
}


# extract_data_task_data_scientist = PythonOperator(
#    task_id="extract_data_task_data_scientist",
#    python_callable=extract_data,
#    provide_context=True,
#    dag=dag,
#    op_kwargs={"job": "Data Scientist"},
# )

# extract_data_task_business_analyst = PythonOperator(
#    task_id="extract_data_task_business_analyst",
#    python_callable=extract_data,
#    provide_context=True,
#    dag=dag,
#    op_kwargs={"job": "Business Analyst"},
# )

# Instantiate the DAG
dag_1 = DAG("data_pipeline_1", default_args=default_args,)

dag_2 = DAG("data_pipeline_2", default_args=default_args,)

# Instantiate the extract task
extract_data_task_data_engineer = PythonOperator(
    task_id="extract_data_task_data_engineer",
    python_callable=extract_data,
    provide_context=True,
    dag=dag_1,
    op_kwargs={"job": "Data Engineer"},
)

extract_data_task_ml_engineer = PythonOperator(
    task_id="extract_data_task_ml_engineer",
    python_callable=extract_data,
    provide_context=True,
    dag=dag_1,
    op_kwargs={"job": "Machine Learning Engineer"},
)

extract_data_task_data_scientist = PythonOperator(
    task_id="extract_data_task_data_scientist",
    python_callable=extract_data,
    provide_context=True,
    dag=dag_2,
    op_kwargs={"job": "Data Scientist"},
)

extract_data_task_business_analyst = PythonOperator(
    task_id="extract_data_task_business_analyst",
    python_callable=extract_data,
    provide_context=True,
    dag=dag_2,
    op_kwargs={"job": "Business Analyst"},
)

# Instantiate the load task
transform_data_task_data_engineer = PythonOperator(
    task_id="transform_data_task_data_engineer",
    python_callable=transform_data,
    provide_context=True,
    trigger_rule="all_success",
    op_kwargs={"task_id": "extract_data_task_data_engineer"},
    dag=dag_1,
)

# Instantiate the load task
transform_data_task_ml_engineer = PythonOperator(
    task_id="transform_data_task_ml_engineer",
    python_callable=transform_data,
    provide_context=True,
    trigger_rule="all_success",
    op_kwargs={"task_id": "extract_data_task_ml_engineer"},
    dag=dag_1,
)

transform_data_task_data_scientist = PythonOperator(
    task_id="transform_data_task_data_scientist",
    python_callable=transform_data,
    provide_context=True,
    trigger_rule="all_success",
    op_kwargs={"task_id": "extract_data_task_data_scientist"},
    dag=dag_2,
)

transform_data_task_business_analyst = PythonOperator(
    task_id="transform_data_task_business_analyst",
    python_callable=transform_data,
    provide_context=True,
    trigger_rule="all_success",
    op_kwargs={"task_id": "extract_data_task_business_analyst"},
    dag=dag_2,
)

load_data_task_data_engineer = PythonOperator(
    task_id="load_data_task_data_engineer",
    python_callable=load_data,
    provide_context=True,
    trigger_rule="all_success",
    dag=dag_1,
    op_kwargs={"job": "Data Engineer", "task_id": "extract_data_task_data_engineer"},
)

load_data_task_ml_engineer = PythonOperator(
    task_id="load_data_task_ml_engineer",
    python_callable=load_data,
    provide_context=True,
    trigger_rule="all_success",
    dag=dag_1,
    op_kwargs={"job": "Data Engineer", "task_id": "extract_data_task_ml_engineer"},
)

load_data_task_data_scientist = PythonOperator(
    task_id="load_data_task_data_scientist",
    python_callable=load_data,
    provide_context=True,
    trigger_rule="all_success",
    dag=dag_2,
    op_kwargs={"job": "Data Scientist", "task_id": "extract_data_task_data_scientist"},
)

load_data_task_business_analyst = PythonOperator(
    task_id="load_data_task_business_analyst",
    python_callable=load_data,
    provide_context=True,
    trigger_rule="all_success",
    dag=dag_2,
    op_kwargs={
        "job": "Business Analyst",
        "task_id": "extract_data_task_business_analyst",
    },
)

# The dags are separated into two groups of tasks in order not use the selenium nodes at the same time
extract_data_task_data_engineer >> transform_data_task_data_engineer >> load_data_task_data_engineer
extract_data_task_ml_engineer >> transform_data_task_ml_engineer >> load_data_task_ml_engineer
extract_data_task_data_scientist >> transform_data_task_data_scientist >> load_data_task_data_scientist
extract_data_task_business_analyst >> transform_data_task_business_analyst >> load_data_task_business_analyst

