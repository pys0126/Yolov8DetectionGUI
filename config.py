
class DatabaseConfig:
    """
    数据库配置
    """
    DB_HOST: str = "127.0.0.1"  # 数据库主机
    DB_PORT: int = 3306  # 数据库端口
    DB_USER: str = "root"  # 数据库用户名
    DB_PASSWORD: str = "root"  # 数据库密码
    DB_NAME: str = "detection_system"  # 数据库名
    DB_ECHO: bool = False  # 是否打印日志


class GlobalConfig:
    """
    全局配置
    """
    WINDOW_WIDTH: int = 800  # 窗口宽度
    WINDOW_HEIGHT: int = 600  # 窗口高度
    WINDOW_TITLE: str = "目标检测程序"  # 窗口标题
    # 初始用户信息
    INIT_USERNAME: str = "admin"  # 初始用户名
    INIT_PASSWORD: str = "123456"  # 初始密码


class DetectionConfig:
    """
    检测配置
    """
    # Yolo模型路径
    YOLO_MODEL_PATH: str = "yolov8n.pt"
    # 检测分类名称ID，全部分类名称请查看：https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml
    CLASS_NAME_ID: int = 0  # 对应 person
    # 检测阈值（置信度）
    CONFIDENCE_THRESHOLD: float = 0.7
    # 非最大抑制 (NMS) 的交叉重叠 (IoU) 阈值。较低的数值可以消除重叠的方框，从而减少检测次数，这对减少重复检测非常有用。
    IOU: float = 0.7

    @staticmethod
    def set_confidence_threshold(confidence_threshold: float) -> None:
        """
        设置置信度阈值
        :param confidence_threshold: 置信度阈值
        :return: None
        """
        DetectionConfig.CONFIDENCE_THRESHOLD = confidence_threshold

    @staticmethod
    def set_iou(iou: float) -> None:
        """
        设置非最大抑制 (NMS) 的交叉重叠 (IoU) 阈值。较低的数值可以消除重叠的方框，从而减少检测次数，这对减少重复检测非常有用。
        :param iou: 非最大抑制 (NMS) 的交叉重叠 (IoU) 阈值
        :return: None
        """
        DetectionConfig.IOU = iou
