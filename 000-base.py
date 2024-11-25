from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG(
    '001-basic_dag',
    default_args=default_args,
    description='A basic DAG',
    schedule_interval='@daily',
    catchup=False,
) as dag:
    start = DummyOperator(task_id='start')
    print_date = BashOperator(
        task_id='print_date',
        bash_command='date'
    )
    run_in_pod = KubernetesPodOperator(
        namespace='default',
        image="ubuntu:20.04",
        cmds=["bash", "-cx"],
        arguments=["echo", "10"],
        labels={"foo": "bar"},
        name="run-in-pod",
        task_id="run_in_pod",
        get_logs=True,
    )
    end = DummyOperator(task_id='end')

    start >> print_date >> run_in_pod >> end
