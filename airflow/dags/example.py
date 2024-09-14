from __future__ import annotations

import logging
from datetime import timedelta

from airflow.decorators import dag
from airflow.decorators import task
from airflow.utils.dates import days_ago


@dag(
    dag_id="dsp_example",
    description="DSP Example DAG",
    tags=["dsp"],
    schedule=timedelta(minutes=2),
    start_date=days_ago(n=0, hour=1),  # sets the starting point of the DAG
    max_active_runs=1,  # Ensure only one active run at a time
)
def my_dag_example():
    @task
    def task_1() -> int:
        logging.info("Task one")
        return 1

    @task
    def task_2(x: int) -> int:
        logging.info("test")
        return x + 1

    # Task relationships
    x = task_1()
    y = task_2(x=x)
    print(y)


# Run dag
example_dag = my_dag_example()
