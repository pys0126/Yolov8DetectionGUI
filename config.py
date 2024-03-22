class DatabaseConfig:
    """
    数据库配置
    """
    DB_HOST: str = "127.0.0.1"  # 数据库主机
    DB_PORT: int = 3306  # 数据库端口
    DB_USER: str = "root"  # 数据库用户名
    DB_PASSWORD: str = "root"  # 数据库密码
    DB_NAME: str = "detection_system"  # 数据库名
    DB_ECHO: bool = True  # 是否打印日志


class GlobalConfig:
    """
    全局配置
    """
    WINDOW_WIDTH: int = 600  # 窗口宽度
    WINDOW_HEIGHT: int = 500  # 窗口高度
    WINDOW_TITLE: str = "目标检测程序"  # 窗口标题
    # 初始用户信息
    INIT_USERNAME: str = "admin"  # 初始用户名
    INIT_PASSWORD: str = "123456"  # 初始密码
    # Yolo模型路径
    YOLO_MODEL_PATH: str = "yolov8n.pt"
