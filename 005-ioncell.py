from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime
from kubernetes.client import models as k8s

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'depends_on_past': False,
    'retries': 1,
}

dag = DAG(
    'ncbi_data_download',
    default_args=default_args,
    schedule_interval=None,  # Set this according to your requirements
)

pvc_name = 'airflow-dags'


pvc_volume = k8s.V1Volume(
    name='my-pv',
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)
)


pvc_volume_mount = k8s.V1VolumeMount(
    name='my-pv', mount_path='/usr/local/airflow/dags/', sub_path=None, read_only=False
)


image_pull_secrets = [k8s.V1LocalObjectReference("juxtagene-docker-registry")]


# Task 1: List contents of the volume
task1 = KubernetesPodOperator(
    task_id='list_pv_contents',
    name='list_pv_contents',
    namespace='airflow',
    image='busybox',
    cmds=["sh", "-c", "ls -l /usr/local/airflow/dags && sleep 10"],
    volume_mounts=[pvc_volume_mount],
    volumes=[pvc_volume],
    dag=dag,
)

# Task 2: Execute dorado file
task2 = KubernetesPodOperator(
    task_id='execute_dorado',
    name='execute_dorado',
    namespace='airflow',
    image='busybox',
    cmds=["sh", "-c", "/usr/local/airflow/dags/dorado/bin/dorado && sleep 10"],
    volume_mounts=[pvc_volume_mount],
    volumes=[pvc_volume],
    dag=dag,
)

task1 >> task2
