from config import DetectionConfig
from ultralytics import YOLO
from pathlib import Path

# 初始化模型
yolo_model: YOLO = YOLO(model=Path(DetectionConfig.YOLO_MODEL_PATH))

