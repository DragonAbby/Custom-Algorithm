# Yolov11

## 环境安装

1. Clone repo and install [requirements.txt](requirements.txt) in a python=3.10 environment
   ```
   git clone https://github.com/AIDrive-Research/Custom-Algorithm.git
   cd Custom-Algorithm/01_ModelTraining/01_Detection/Yolov8
   ```

2. 根据 `cuda` 版本安装 [`Pytorch-v2.5.1`](https://pytorch.org/get-started/previous-versions/)  
   以 `cuda 11.8` 为例：
   ```
   pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu118 
   ```

3. 安装依赖
   ```
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   ```

## 模型导出
1. 修改配置文件 `./ultralytics/cfg/default.yaml`  
```
model: yolo8n.pt  # 将 yolo8n.pt 修改为需要转换的模型路径
```

2. `onnx` 导出  
```
export PYTHONPATH=./
python ./ultralytics/engine/exporter.py

# 如果待转换模型是 "yolo8n.pt"， 执行后生成 "yolo8n.onnx" 模型。
```

## 模型量化
**注意**：该操作适用于ks968产品，ks988无需执行。

1. [**环境安装**](../../README.md)

2. 在训练集中随机选取图片进行模型量化，精度校准，数量在80-120之间，目录结构如下：

   ```
    images:
      xxx.jpg
   ```

3. 把图片路径保存至xxx.txt

   ```
    find ./images/ -name "*.jpg">custom.txt
   ```

4. 模型量化

   修改convert.py：

   - DATASET_PATH：量化图片路径

   运行：

   ```
    python convert.py onnx_model_path platform i8/fp output_rknn_path
   ```

   其中：

   - onnx_model_path：训练后导出的onnx模型文件位置
   - platform：rk3588
   - i8/fp：i8代表使用图片量化；fp代表不量化
   - output_rknn_path：量化后模型的保存路径

