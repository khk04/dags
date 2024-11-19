from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.bash import BashOperator
from datetime import datetime

# DAG 정의
default_args = {
    'owner': 'your_name',
    'start_date': datetime(2023, 10, 5),
    'retries': 1,
}

dag = DAG(
    'bash_operator_example_dag',
    default_args=default_args,
    schedule_interval=None,  # DAG를 수동으로 실행하려면 None으로 설정합니다.
    catchup=False,  # 이전 실행을 실행하지 않도록 설정합니다.
    description='BashOperator를 사용한 간단한 Airflow DAG 예제',
)

# Task 정의
start_task = DummyOperator(task_id='start_task', dag=dag)

# BashOperator를 사용하여 'echo' 명령어를 실행합니다.
echo_task = BashOperator(
    task_id='echo_task',
    bash_command='echo "Hello, Airflow!"',
    dag=dag,
)

end_task = DummyOperator(task_id='end_task', dag=dag)

# Task 간의 의존성 설정
start_task >> echo_task >> end_task
