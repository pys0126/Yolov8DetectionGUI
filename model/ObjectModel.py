from sqlalchemy.orm import Mapped
from util.MysqlUtil import BaseModel
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, Integer, Text
from util.TimeUtil import now_timestamp


class ObjectModel(BaseModel):
    """
    物体模型
    """
    __tablename__: str = "object"
    # 主键
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, unique=True, comment="主键，自增，唯一")
    # 图片名称
    image_name: Mapped[str] = mapped_column(Text, nullable=True, comment="图片名称")
    # 人的数量
    totality: Mapped[str] = mapped_column(Integer, nullable=True, comment="识别到的人数量")
    # 用户ID
    user_id: Mapped[int] = mapped_column(Integer, nullable=True, comment="用户ID")
    # 更新时间，默认为now_timestamp生成，更新时为now_timestamp生成
    update_timestamp: Mapped[int] = mapped_column(Integer, insert_default=now_timestamp(), onupdate=now_timestamp(),
                                                  nullable=True, comment="更新时间戳")
    # 创建时间，默认为now_timestamp生成的
    create_timestamp: Mapped[int] = mapped_column(Integer, insert_default=now_timestamp(), nullable=True,
                                                  comment="创建时间戳")
