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
    '005-ioncell',
    default_args=default_args,
    schedule_interval=None,  # 필요에 따라 이 값을 설정하세요
)

pvc_name = 'biotools-pvc'

# PVC 볼륨 정의
pvc_volume = k8s.V1Volume(
    name='my-pv',
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)
)

# PVC 볼륨 마운트 정의
pvc_volume_mount = k8s.V1VolumeMount(
    name='my-pv', mount_path='/usr/local/sbin/biotools/', sub_path=None, read_only=False
)

# 새로운 PVC 이름 정의
pvc_name_2 = 'colo829-pvc'

# 새로운 PVC 볼륨 정의
pvc_volume_2 = k8s.V1Volume(
    name='my-pv-2',
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name_2)
)

# 새로운 PVC 볼륨 마운트 정의
pvc_volume_mount_2 = k8s.V1VolumeMount(
    name='my-pv-2', mount_path='/mnt/colo829/', sub_path=None, read_only=False
)

# 새로운 PVC 이름 정의
pvc_name_output = 'output-pvc'

# 새로운 PVC 볼륨 정의
pvc_volume_output = k8s.V1Volume(
    name='my-pv-output',
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name_output)
)

# 새로운 PVC 볼륨 마운트 정의
pvc_volume_mount_output = k8s.V1VolumeMount(
    name='my-pv-output', mount_path='/mnt/output/', sub_path=None, read_only=False
)

# 환경 변수 정의
env_vars = [
    k8s.V1EnvVar(name='BIOTOOLS_HOME', value='/usr/local/sbin/biotools'),
    k8s.V1EnvVar(name='COLO829', value='/mnt/colo829'),
    k8s.V1EnvVar(name='OUTPUT', value='/mnt/output')
]

# 이미지 풀 시크릿 정의
image_pull_secrets = [k8s.V1LocalObjectReference("juxtagene-docker-registry")]

# 작업 1: 볼륨의 내용 목록을 나열합니다
task1 = KubernetesPodOperator(
    task_id='list_pv_contents',
    name='list_pv_contents',
    namespace='airflow',
    image='ubuntu:20.04',  # Ubuntu 20.04 이미지를 사용합니다.
    cmds=["sh", "-c", "ls -l $BIOTOOLS_HOME && sleep 3"],
    volume_mounts=[pvc_volume_mount],
    volumes=[pvc_volume],
    env_vars=env_vars,
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
    cmds=["sh", "-c", "ls -l $COLO829 && $BIOTOOLS_HOME && sleep 3"],
    volume_mounts=[pvc_volume_mount, pvc_volume_mount_2],
    volumes=[pvc_volume, pvc_volume_2],
    dag=dag,
)

# 작업 3: dorado 커맨드 실행
task3 = KubernetesPodOperator(
    task_id='execute_dorado_basecaller',
    name='execute_dorado_basecaller',
    namespace='airflow',
    image='ubuntu:20.04',  # Ubuntu 20.04 이미지를 사용합니다.
    env_vars=env_vars,
    image_pull_secrets=image_pull_secrets,
    cmds=["sh", "-c", "apt update && apt install -y curl && $BIOTOOLS_HOME/dorado/bin/dorado basecaller --emit-fastq -x 'cpu' hac $COLO829/PAU61426_pass_4ddb6960_908efd09_0.pod5 > $OUTPUT/PAU61426_pass_4ddb6960_908efd09_0.fastq "],
    volume_mounts=[pvc_volume_mount, pvc_volume_mount_2, pvc_volume_mount_output],
    volumes=[pvc_volume, pvc_volume_2, pvc_volume_output],
    dag=dag,
)

# 작업 4: minimap2 명령 실행
task4 = KubernetesPodOperator(
    task_id='execute_minimap2',
    name='execute_minimap2',
    namespace='airflow',
    image='ubuntu:20.04',  # Ubuntu 20.04 이미지를 사용합니다.
    env_vars=env_vars,
    image_pull_secrets=image_pull_secrets,
    cmds=["sh", "-c", "$BIOTOOLS_HOME/minimap2 -ax map-ont $COLO829/chm13v2.0.fa $OUTPUT/PAU61426_pass_4ddb6960_908efd09_0.fastq -t 1000 | $BIOTOOLS_HOME/samtools view -Sb - | $BIOTOOLS_HOME/samtools sort > $OUTPUT/minimap2_out.sorted.bam"],
    volume_mounts=[pvc_volume_mount, pvc_volume_mount_2, pvc_volume_mount_output],
    volumes=[pvc_volume, pvc_volume_2, pvc_volume_output],
    dag=dag,
)

# 작업 순서 정의
task1 >> task2 >> task4
