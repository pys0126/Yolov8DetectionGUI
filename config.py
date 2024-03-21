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
