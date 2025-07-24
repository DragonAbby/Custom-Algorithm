# ModelTraining

## 🌟环境安装

### 训练环境
- 训练环境安装请参考选定模型的文件夹内部说明文档，如Yolov5/README.md。

### 量化环境
注意：该流程适用于晓知精灵**ks968**产品，ks988无需执行。

- 系统要求
    - 操作系统：Ubuntu

- Tools/rknn-toolkit2中提供了python3.8的量化环境whl文件

  ```bash
    cd Tools/rknn-toolkit2
    conda create -n py38-rk2.2 python=3.8
    conda activate py38-rk2.2
    pip3 install rknn_toolkit2-2.2.0-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
  ```