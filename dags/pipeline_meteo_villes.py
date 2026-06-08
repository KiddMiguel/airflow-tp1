from datetime import datetime
import sys

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator


sys.path.append("/opt/airflow/jobs")

from meteo_job import (
    extraire_meteo,
    valider_meteo,
    transformer_meteo,
    generer_rapport,
)


with DAG(dag_id="pipeline_meteo_villes", start_date=datetime(2026, 1, 1), schedule="*/5 * * * *", catchup=False, tags=["tp", "airflow", "meteo", "data"]) as dag:

    t1 = PythonOperator(
        task_id="extraire_meteo",
        python_callable=extraire_meteo,
    )

    t2 = PythonOperator(
        task_id="valider_meteo",
        python_callable=valider_meteo,
    )

    t3 = PythonOperator(
        task_id="transformer_meteo",
        python_callable=transformer_meteo,
    )

    t4 = PythonOperator(
        task_id="generer_rapport",
        python_callable=generer_rapport,
    )

    t1 >> t2 >> t3 >> t4
