# vertex-ai-job
GCPのvertex aiへjobを投げるコード

## docker build and push
### ローカル
```bash
uv run inv docker-build
uv run inv docker-push
```

### Cloud Build
```bash
PROJECT=プロジェクト名
REGION=asia-northeast1
IMAGE=$REGION-docker.pkg.dev/$PROJECT/パス/名前
TAG=`date +"%Y%m%d%H%M%S"`
gcloud builds submit --config cloudbuild.yaml --project=$PROJECT --async --substitutions=_IMAGE=$IMAGE,_TAG=$TAG
```

## jobを投げる
### pythonライブラリで投げる
```bash
uv run inv submit-job
```

### gcloudコマンドで投げる
```bash
PROJECT=プロジェクト名
REGION=asia-northeast1
IMAGE=$REGION-docker.pkg.dev/$PROJECT/パス/名前
DISPLAY_NAME=ジョブ名`date +"%Y%m%d%H%M%S"`
CONFIG_FILE_PATH=custom-job-config.json

cat << EOF > $CONFIG_FILE_PATH
{
  "workerPoolSpecs": [
    {
      "machineSpec": {
        "machineType": "n1-standard-4",
        "acceleratorType": "NVIDIA_TESLA_T4",
        "acceleratorCount": 1
      },
      "replicaCount": "1",
      "diskSpec": {
        "bootDiskType": "pd-ssd",
        "bootDiskSizeGb": 100
      },
      "containerSpec": {
        "imageUri": "$IMAGE",
        "command": ["uv", "run", "inv", "train"]
      }
    }
  ]
}
EOF

gcloud ai custom-jobs create --project=$PROJECT --region=$REGION --display-name=$DISPLAY_NAME --config=$CONFIG_FILE_PATH
```
