# Python 人数识别 GUI 程序 

本项目使用 [Yolov8](https://docs.ultralytics.com/) 模型库进行人数识别，使用 [Flet](https://flet.dev/) 构建 GUI，使用 [SQLAlchemy](https://www.sqlalchemy.org/) 操作数据库；当前支持图片和视频，功能扩展性极高。

本项目采用的技术栈：
- 语言：`Python3.9`
- 图形界面框架：`Flet`
- 数据库驱动：`pymysql`
- 数据库对象映射ORM框架：`SQLAlchemy`
- 图像识别用到的库：`opencv-python`、`pillow`、`ultralytics`

# 实用效果截图

<img src="./images/2.png" width="400"  alt=""/>
<img src="./images/3.png" width="400"  alt=""/>

# 使用说明

**安装依赖**

```shell
pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple
```

**修改配置项**

参考配置文件：[`config.py`](./config.py)，修改对应项即可。

**运行程序**

```shell
python main.py
```
