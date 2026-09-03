from airflow.sdk import dag, task
from parent_dag_1 import parent_dag_1
from parent_dag_2 import parent_dag_2
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

@dag
def orchestrator():

    trigger_first_dag = TriggerDagRunOperator(
        task_id='trigger_first_dag',
        trigger_dag_id='parent_dag_1'
    )

    trigger_second_dag = TriggerDagRunOperator(
            task_id='trigger_second_dag',
            trigger_dag_id='parent_dag_2'
        )

    trigger_first_dag >> trigger_second_dag

orchestrator()