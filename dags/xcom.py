from airflow.sdk import dag, task, Context

@dag
def xcom_dag():

    # @task
    # def task_a(**context: Context):
    #     val = 27
    #     context['ti'].xcom_push(key='return_value', value=val)

    # @task
    # def task_b(**context: Context):
    #     val = context['ti'].xcom_pull(task_ids='task_a', key='my_key')
    #     print(val)

    # task_a >> task_b

    #implicity xcom
    @task
    def task_a():
        val = 27
        return val
    
    @task
    def task_b(val: int):
        print(val)

    val = task_a()
    task_b(val)


xcom_dag()