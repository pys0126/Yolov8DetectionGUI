from ultralytics.engine.results import Results
from util.StringUtil import is_video_file
from config import DetectionConfig
from mapper.ObjectMapper import *
from service import yolo_model
from typing import Union
from PIL import Image
import time
import cv2
import os


def object_num_detect(file_path: str, user_id: int) -> Union[int, str]:
    """
    物体数量检测（整合）
    :param file_path: 待识别的文件路径
    :param user_id: 当前用户ID
    :return: str（检测出错） 或者 int（物体数量）
    """
    # 检测文件是否正确
    try:
        Image.open(file_path)
        return object_num_detect_by_image(image_path=file_path, user_id=user_id)
    except Exception:
        # 检测视频是否为视频文件
        if not is_video_file(file_path=file_path):
            return "不是有效的图片或者视频文件"
        else:
            return object_num_detect_by_video(video_path=file_path, user_id=user_id)


def object_num_detect_by_image(image_path: str, user_id: int) -> Union[tuple, str]:
    """
    物体数量检测（图片版）
    :param image_path: 待识别的图片路径
    :param user_id: 当前用户ID
    :return: （str（检测出错） 或者 int（物体数量），推理时间）
    """
    # 检测结果列表
    results: list[Results] = yolo_model.predict(source=image_path, conf=DetectionConfig.CONFIDENCE_THRESHOLD,
                                                classes=DetectionConfig.CLASS_NAME_ID)
    object_model: ObjectModel = ObjectModel()
    totality: int = 0  # 初始化数量
    # 定义推理时间
    total_time: float = 0.0
    for result in results:
        # 累加识别到的数量
        totality += len(result.boxes.data)
        # 如果总数大于0，则保存到本地，供UI访问
        if totality > 0:
            # 创建缓存文件夹（如果没有）
            if not os.path.exists(path="cache"):
                os.mkdir(path="cache")
            # 保存识别结果图片，路径为：cache目录下的当前图片文件名
            result.save(filename=os.path.join("cache", os.path.basename(image_path)))
            total_time += result.speed.get("inference")
    # 图片名称
    object_model.image_name = os.path.basename(image_path)
    # 当前用户ID
    object_model.user_id = user_id
    # 识别到的物体数量
    object_model.totality = totality
    # 创建时间戳
    object_model.create_timestamp = int(time.time())
    # 更新时间戳
    object_model.update_timestamp = int(time.time())
    # 插入数据库
    insert(object_model=object_model)
    return totality, round(total_time, 3)  # 保留三位小数


def object_num_detect_by_video(video_path: str, user_id: int) -> Union[tuple, str]:
    """
    物体数量检测（视频版）
    :param video_path: 待识别的视频路径
    :param user_id: 当前用户ID
    :return: （str（检测出错） 或者 int（物体数量），推理时间）
    """
    # 检测视频是否为视频文件
    if not is_video_file(file_path=video_path):
        return "不是有效的视频文件"
    totality_list: list[int] = []  # 初始化数量列表
    # 定义模型
    object_model: ObjectModel = ObjectModel()
    # 读取视频
    capture: cv2.VideoCapture = cv2.VideoCapture(filename=video_path)
    # 视频名称
    video_name: str = os.path.basename(video_path)
    # 定义缓存视频
    out_video: cv2.VideoWriter = cv2.VideoWriter(f"cache/{video_name}",
                                                 cv2.VideoWriter.fourcc(*'mp4v'), 20.0,
                                                 [int(capture.get(3)), int(capture.get(4))])
    # 定义推理时间
    total_time: float = 0.0
    while True:
        ret, frame = capture.read()  # 读取视频的一帧
        # 如果视频结束了，中断循环
        if not ret:
            break
        # 检测结果列表
        results: list[Results] = yolo_model.predict(source=frame, conf=DetectionConfig.CONFIDENCE_THRESHOLD,
                                                    classes=DetectionConfig.CLASS_NAME_ID)
        for result in results:
            # 将识别到的数量添加到totality_list
            totality_list.append(len(result.boxes.data))
            # 将带注释的帧写入视频文件
            out_video.write(result.plot())
            total_time += result.speed.get("inference")
    # 释放资源
    capture.release()
    out_video.release()
    # 视频名称
    object_model.image_name = os.path.basename(video_path)
    # 当前用户ID
    object_model.user_id = user_id
    # 识别到的物体数量，求和
    totality: int = sum(totality_list)
    object_model.totality = totality
    # 创建时间戳
    object_model.create_timestamp = int(time.time())
    # 更新时间戳
    object_model.update_timestamp = int(time.time())
    # 插入数据库
    insert(object_model=object_model)
    return totality, round(total_time, 3)  # 保留三位小数


def list_object_by_user_id(user_id: int) -> list:
    """
    获取当前用户识别的记录
    :param user_id: 当前用户ID
    :return: [
        { "id": 1, "image_name": "1.jpg", "totality": 1, "user_id": 1 },
        { "id": 2, "image_name": "2.jpg", "totality": 2, "user_id": 1 },
        ...
    ]
    """
    object_model_list: list[Optional[ObjectModel]] = find_by_user_id(user_id=user_id)
    return [object_model.to_dict() for object_model in object_model_list if object_model]


def delete_object_by_id(object_id: int) -> None:
    """
    删除当前物体识别记录
    :param object_id: 当前用户ID
    :return: None
    """
    object_model: Optional[ObjectModel] = find_by_id(object_id=object_id)
    delete(object_model=object_model) if object_model else None
