# 基于U-Net的遥感图像语义分割系统
本系统基于U-Net模型，使用[LoveDA](https://arxiv.org/abs/2110.08733)数据集训练后，
可以根据输入的遥感图像输出语义分割后的结果。

## 环境配置
- python 3.8
- CUDA 11.8
- cudnn 8
- pytorch 2.2.2

### 使用Anaconda安装
首先，创建虚拟环境

控制台输入
```
conda create -n unet python=3.8     # 创建名为unet的conda虚拟环境
conda activate unet                 # 激活unet虚拟环境
```
之后，安装CUDA和cudnn，使用
```
conda install cudatoolkit=11.8
conda install cudnn
```
安装pytorch
```
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```
最后安装依赖，在项目文件目录下
```
pip install -r requirements.txt
```

## 使用方法
### 文件目录介绍
#### 模型训练相关文件
- `data`文件夹存放数据集及测试集文件
- `unet`文件夹为U-Net模型结构定义
- `utils`文件夹包含了模型训练必要的函数，如数据加载、DICE分数计算等
- `dataprocess.py`用于数据集图片过大时，裁剪为多张小图
- `evaluate.py`用于训练过程中进行验证评估
- `rename.py`用于给mask文件添加后缀，也可在`utils/data_loading.py`中修改suffix，可忽略
- `train.py`用于模型训练

#### 系统相关文件
- `imgs`文件夹存放系统必要图片，其中`Log`文件夹包括模型训练过程记录
- `models`文件夹存放训练好的模型文件，其中含有`-m`后缀的为多分类模型，不含`-m`的为二分类模型
- `output`文件夹用于保存系统输出图像
- `labels.py`用于生成图例
- `main.py`为系统启动主文件
- `main_tk.py`为无背景系统，可忽略
- `predict.py`用于模型输出

### 运行
直接运行`main.py`即可启动系统，默认用户名为admin，密码为admin