from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import scoped_session, sessionmaker
from config import DatabaseConfig


class BaseModel(DeclarativeBase):
    """
    模型基类
    """
    def to_dict(self) -> dict:
        """
        转为字典
        :return:
        """
        # 去除_sa_instance_state字段
        self.__dict__.pop("_sa_instance_state")
        return self.__dict__


# 连接信息
connect_uri: str = f"mysql+pymysql://" \
                   f"{DatabaseConfig.DB_USER}:{DatabaseConfig.DB_PASSWORD}@" \
                   f"{DatabaseConfig.DB_HOST}:{DatabaseConfig.DB_PORT}/" \
                   f"{DatabaseConfig.DB_NAME}"
# 创建连接池
engine: Engine = create_engine(url=connect_uri, echo=DatabaseConfig.DB_ECHO, pool_recycle=7200, pool_pre_ping=True,
                               pool_size=10, max_overflow=20)
# 创建会话
mysql_session: scoped_session = scoped_session(sessionmaker(bind=engine))


def create_tables():
    """
    创建数据表（如果不存在）
    :return:
    """
    # 创建数据表，一方面通过engine来连接数据库，另一方面根据哪些类继承了Base来决定创建哪些表
    # checkfirst=True，表示创建表前先检查该表是否存在，如同名表已存在则不再创建。其实默认就是True
    from model.UserModel import UserModel
    BaseModel.metadata.create_all(bind=engine, checkfirst=True)
