# my_kubernetes_dag.py

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
}

dag = DAG(
    'my_kubernetes_dag',
    default_args=default_args,
    schedule_interval=None,  # 필요에 따라 설정
)

# KubernetesPodOperator를 사용하여 Ubuntu 20.04 이미지를 실행합니다.
task1 = KubernetesPodOperator(
    task_id='task1',
    name='task1',
    namespace='airflow',
    image='ubuntu:20.04',  # Ubuntu 20.04 이미지를 사용합니다.
    cmds=['echo', 'Hello, Ubuntu from task1!'],
    dag=dag,
)

# 다른 작업을 추가합니다.
task2 = KubernetesPodOperator(
    task_id='task2',
    name='task2',
    namespace='airflow',
    image='ubuntu:20.04',  # Ubuntu 20.04 이미지를 사용합니다.
    cmds=['echo', 'Hello, Ubuntu from task2!'],
    dag=dag,
)

# task1 다음에 task2가 실행되도록 설정합니다.
task1 >> task2
