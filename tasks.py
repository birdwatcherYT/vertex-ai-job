import os
import subprocess
import invoke

from google.cloud import aiplatform, storage
from pathlib import Path
import datetime

ROOT_DIR = Path(__file__).parent


@invoke.task
def submit_job(c: invoke.Context):
    """Vertext AIにジョブを投げる"""
    dt_now = datetime.datetime.now()
    display_name = c.config.display_name_prefix + dt_now.strftime("%Y%m%d%H%M%S")

    client_options = {"api_endpoint": f"{c.config.location}-aiplatform.googleapis.com"}
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)
    custom_job = {
        "display_name": display_name,
        "job_spec": {
            "worker_pool_specs": [
                {
                    "machine_spec": {
                        "machine_type": c.config.machine_spec.machine_type,
                        "accelerator_type": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_T4,
                        "accelerator_count": c.config.machine_spec.accelerator_count,
                    }
                    if c.config.machine_spec.accelerator_count
                    else {"machine_type": c.config.machine_spec.machine_type},
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": c.config.image,
                        "command": [],
                        "args": [],
                    },
                }
            ]
        },
    }
    parent = f"projects/{c.config.project}/locations/{c.config.location}"
    response = client.create_custom_job(parent=parent, custom_job=custom_job)
    print(response)
    job_id = response.name.split("/")[-1]
    print(
        f"https://console.cloud.google.com/vertex-ai/locations/{c.config.location}/training/{job_id}/cpu?project={c.config.project}"
    )


@invoke.task
def upload_to_gcs(c: invoke.Context, src_file: str):
    """ファイルをGCSへアップロードする"""
    client = storage.Client(project=c.config.project)
    bucket = client.bucket(c.config.gcs.bucket_name)

    blob_name = os.path.join(c.config.gcs.blob_dir, os.path.basename(src_file))
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(src_file)


@invoke.task
def train(c: invoke.Context):
    """学習する"""
    print("train start")
    # dummy
    upload_to_gcs(c, "invoke.yaml")
    print("train end")


@invoke.task
def docker_build(c):
    """Dockerビルド"""
    subprocess.run(
        f"docker build --tag {c.config.image} .", cwd=ROOT_DIR, shell=True, check=True
    )


@invoke.task
def docker_run(c):
    """Docker起動"""
    credentials = "-v ~/.config/gcloud:/root/.config/gcloud"
    subprocess.run(
        f"docker run -p {c.config.port}:{c.config.port} --rm -it {credentials} {c.config.image}",
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )


@invoke.task
def docker_push(c):
    """DockerをArtifact Registry/Container Registryへpush"""
    dt_now = datetime.datetime.now()
    tag = dt_now.strftime("%Y%m%d%H%M%S")
    subprocess.run(
        f'docker image tag "{c.config.image}:latest" "{c.config.image}:{tag}"',
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )
    subprocess.run(
        f'docker push "{c.config.image}:latest"',
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )
    subprocess.run(
        f'docker push "{c.config.image}:{tag}"',
        cwd=ROOT_DIR,
        shell=True,
        check=True,
    )
