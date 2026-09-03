import datetime
from airflow.sdk import dag, task
from airflow.providers.standard.operators.empty import EmptyOperator

@dag (start_date=datetime.datetime(2021, 1, 1),schedule="@daily")
def parent_dag_2():
    @task.python
    def first_task():
        EmptyOperator(task_id="first_task")

    @task.python
    def second_task():
        EmptyOperator(task_id="second_task")

    @task.python
    def third_task():
        EmptyOperator(task_id="third_task")

    first_task() >> second_task() >> third_task()

parent_dag_2()