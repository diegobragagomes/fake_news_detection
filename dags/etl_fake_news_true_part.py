from datetime import datetime
from http import client
import pandas as pd
import numpy as np
from minio import Minio
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.models import Variable

default_args = {"owner" : "airflow",
                "start_date" : datetime(2021,5,1),
                "depends_on_past" : False}

dag = DAG(dag_id= "etl_fake_news_true_part_project",
        description="Processo de ETL do Projeto focado em Fake News",
        schedule_interval= "@once",
        default_args = default_args)

data_lake_server = Variable.get("data_lake_server")
data_lake_login = Variable.get("data_lake_login")
data_lake_password = Variable.get("data_lake_password")

client = Minio(data_lake_server,
            access_key= data_lake_login,
            secret_key= data_lake_password,
            secure= False)

def _extract_true():

    df_true = pd.DataFrame(data = None)

    objects = client.list_objects("bruto", prefix = "True",recursive = True)

    for object in objects:

        object = client.get_object(object.bucket_name,
                object.object_name.encode('utf-8'))

        df_true= pd.read_csv(object)

    df_true.to_parquet("/tmp/etl_true_fakenews.parquet")

def _transform_true():

    df_true = pd.read_parquet("/tmp/etl_true_fakenews.parquet")

    df_true["Status"] = "True"

    df_true.to_parquet("/tmp/etl_true_fakenews.parquet")


extract_true = PythonOperator(task_id = "extract_true",
                            python_callable= _extract_true,
                            provide_context = True,
                            dag = dag)

transform_true = PythonOperator(task_id = "transform_true",
                            python_callable= _transform_true,
                            provide_context = True,
                            dag = dag)

extract_true >> transform_true










