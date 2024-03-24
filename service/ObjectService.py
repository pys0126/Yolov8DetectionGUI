from ultralytics.engine.results import Results
from config import DetectionConfig
from mapper.ObjectMapper import *
from ultralytics import YOLO
from pathlib import Path
from typing import Union
from PIL import Image
import time
import os


def object_num_detect(image_path: str, user_id: int) -> Union[int, str]:
    """
    物体数量检测
    :param image_path: 待识别的图片名
    :param user_id: 当前用户ID
    :return: str（检测出错） 或者 int（物体数量）
    """
    # 检测图片是否为图片文件
    try:
        Image.open(image_path)
    except Exception:
        return "不是图片文件"
    # 初始化模型
    yolo_model: YOLO = YOLO(model=Path(DetectionConfig.YOLO_MODEL_PATH))
    # 检测结果列表
    results: list[Results] = yolo_model.predict(source=image_path, conf=DetectionConfig.CONFIDENCE_THRESHOLD,
                                                classes=DetectionConfig.CLASS_NAME_ID)
    object_model: ObjectModel = ObjectModel()
    totality: int = 0  # 初始化数量
    for result in results:
        # 累加识别到的数量
        totality += len(result.boxes.data)
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
    return totality


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
