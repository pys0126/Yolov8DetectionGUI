from service.WindowService import WindowService
from service.UserService import register
from util.MysqlUtil import create_tables
from config import GlobalConfig
import flet

if __name__ == "__main__":
    # 创建所有表（如果不存在）
    create_tables()
    # 创建初始用户
    register(username=GlobalConfig.INIT_USERNAME, password=GlobalConfig.INIT_PASSWORD)
    # 启动窗口
    flet.app(target=WindowService)
