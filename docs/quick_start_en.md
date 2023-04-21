[简体中文](quick_start_cn.md) | English

# Quick Start

## Prerequisites

1. [Install PaddlePaddle](https://www.paddlepaddle.org.cn/install/quick)
  - Version requirements: PaddlePaddle>=2.2.0

2. Install PaddleRS

Check out releases of PaddleRS [here](https://github.com/PaddlePaddle/PaddleRS/releases). Download and extract the source code and run:

```shell
pip install -r requirements.txt
pip install .
```

The PaddleRS code will be updated as the development progresses. You can also install the develop branch to use the latest features as follows:

```shell
git clone https://github.com/PaddlePaddle/PaddleRS
cd PaddleRS
git checkout develop
pip install -r requirements.txt
pip install .
```

3. (Optional) Install GDAL

PaddleRS supports reading of various types of satellite data. To use the full data reading functionality of PaddleRS, you need to install GDAL as follows:

  - Linux / MacOS

conda is recommended for installation:

```shell
conda install gdal
```

  - Windows

Windows users can download GDAL wheels from [this site](https://www.lfd.uci.edu/~gohlke/pythonlibs/#gdal). Please choose the wheel according to the Python version and the platform. Take *GDAL‑3.3.3‑cp39‑cp39‑win_amd64.whl* as an example, run the following command to install:

```shell
pip install GDAL‑3.3.3‑cp39‑cp39‑win_amd64.whl
```

We also provide a docker image for installation:

1. Pull from dockerhub:

```shell
docker pull paddlepaddle/paddlers:1.0.0
```

Optionally, you can build the image from scratch. You can change the base images for different PaddlePaddle versions by setting `PPTAG` in `Dockerfile`.

```shell
git clone https://github.com/PaddlePaddle/PaddleRS
cd PaddleRS
docker build -t <imageName> .  # Default is PaddlePaddle-2.4.1-CPU
# docker build -t <imageName> . --build-arg PPTAG=2.4.1-gpu-cuda10.2-cudnn7.6-trt7.0  # Use a GPU version of PaddlePaddle
# For more tags, please refer to: https://hub.docker.com/r/paddlepaddle/paddle/tags
```

2. Start a container

```shell
docker images  # View the ID of the image
docker run -it <imageID>
```

## Model Training

See [here](../tutorials/train/README_EN.md).

## Model Evaluation

After the model training is completed, you can evaluate the model by executing the following snippet (take DeepLab V3+ as an example):

```python
import paddlers as pdrs
from paddlers import transforms as T

# Load the trained model
model = pdrs.load_model('output/deeplabv3p/best_model')

# Combine data transformation operators
eval_transforms = [
    T.Resize(target_size=512),
    T.Normalize(
        mean=[0.5] * NUM_BANDS, std=[0.5] * NUM_BANDS),
    T.ReloadMask()
]

# Load the validation dataset
dataset = pdrs.datasets.SegDataset(
    data_dir='dataset',
    file_list='dataset/val/list.txt',
    label_list='dataset/labels.txt',
    transforms=eval_transforms)

# Do the evaluation
result = model.evaluate(dataset)

print(result)
```

## Model Deployment

### Model Exporting

Please refer to [this document](../deploy/export/README.md).

### Deployment Using Python

Please refer to [this document](../deploy/README.md).