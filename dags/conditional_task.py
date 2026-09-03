import pendulum
from airflow.sdk import dag, task
from airflow.providers.standard.operators.empty import EmptyOperator

@dag(start_date=pendulum.datetime(2021, 1, 1, tz='America/Sao_Paulo'),schedule="@daily", catchup=False, )
def conditional_dag():
    @task.python
    def first_task():
        EmptyOperator(task_id="first_task")

    @task.python
    def second_task():
        EmptyOperator(task_id="second_task")

    @task.python
    def third_task():
        EmptyOperator(task_id="third_task")

    @task.python
    def fourth_task():
        EmptyOperator(task_id="fourth_task")

    @task.branch
    def if_task():
        today_is_weekend = True 
        if today_is_weekend:
            return "weekend_task"
        return "weekday_task"

    @task.python
    def weekday_task():
        EmptyOperator(task_id="weekday_task")

    @task.python
    def weekend_task():
        EmptyOperator(task_id="weekend_task")

    first_task() >> [second_task(), third_task()] >> fourth_task() >> if_task() >> [weekday_task(), weekend_task()]

conditional_dag()