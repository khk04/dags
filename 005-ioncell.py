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
    schedule_interval=None,  # 필요에 따라 이 값을 설정하세요
)

pvc_name = 'dorado-pvc'

# PVC 볼륨 정의
pvc_volume = k8s.V1Volume(
    name='my-pv',
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)
)

# PVC 볼륨 마운트 정의
pvc_volume_mount = k8s.V1VolumeMount(
    name='my-pv', mount_path='/usr/local/dorado/', sub_path=None, read_only=False
)

# 환경 변수 정의
env_vars = [
    k8s.V1EnvVar(name='DORADO_HOME', value='/usr/local/dorado')
]

# 이미지 풀 시크릿 정의
image_pull_secrets = [k8s.V1LocalObjectReference("juxtagene-docker-registry")]

# 작업 1: 볼륨의 내용 목록을 나열합니다
task1 = KubernetesPodOperator(
    task_id='list_pv_contents',
    name='list_pv_contents',
    namespace='airflow',
    image='ubuntu:20.04',  # Ubuntu 20.04 이미지를 사용합니다.
    cmds=["sh", "-c", "ls -l /usr/local/dorado && sleep 3"],
    volume_mounts=[pvc_volume_mount],
    volumes=[pvc_volume],
    dag=dag,
)

# 작업 2: dorado 파일 실행
task2 = KubernetesPodOperator(
    task_id='execute_dorado',
    name='execute_dorado',
    namespace='airflow',
    image='ubuntu:20.04',  # Ubuntu 20.04 이미지를 사용합니다.
    env_vars=env_vars,
    image_pull_secrets=image_pull_secrets,
    # dorado 실행 명령어
    cmd=["sh", "-c", "dorado && sleep 10"],
    volume_mounts=[pvc_volume_mount],
    volumes=[pvc_volume],
    dag=dag,
)

# 작업 순서 정의
task1 >> task2
