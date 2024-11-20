from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

# 기본 DAG 설정
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG 정의
with DAG(
    dag_id='kubernetes_executor_example',
    default_args=default_args,
    description='Example DAG for KubernetesExecutor',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2024, 11, 20),
    catchup=False,
    tags=['example', 'kubernetes_executor'],
) as dag:

    # BashOperator 작업 정의
    task_1 = BashOperator(
        task_id='print_date',
        bash_command='date',
    )

    task_2 = BashOperator(
        task_id='echo_message',
        bash_command='echo "Hello from KubernetesExecutor!"',
    )

    # 작업 순서 정의
    task_1 >> task_2
