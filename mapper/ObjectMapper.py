from typing import Optional
from model.ObjectModel import ObjectModel
from util.MysqlUtil import mysql_session, auto_close_session


@auto_close_session
def insert(object_model: ObjectModel) -> None:
    """
    插入物体
    """
    mysql_session.add(instance=object_model)
    mysql_session.commit()


@auto_close_session
def update(object_model: ObjectModel) -> None:
    """
    更新物体
    """
    mysql_session.merge(instance=object_model)
    mysql_session.commit()


@auto_close_session
def delete(object_model: ObjectModel) -> None:
    """
    删除物体
    """
    mysql_session.delete(instance=object_model)
    mysql_session.commit()


@auto_close_session
def find_by_id(object_id: int) -> Optional[ObjectModel]:
    """
    根据ID查询物体
    :param object_id: 物体ID
    :return:
    """
    return mysql_session.query(ObjectModel).filter(ObjectModel.id == object_id).first()


@auto_close_session
def find_by_user_id(user_id: int) -> list[Optional[ObjectModel]]:
    """
    根据用户ID查询物体列表
    :param user_id: 用户ID
    :return: [
        { ObjectModel-01 },
        { ObjectModel-02 },
        ...
    ]
    """
    return mysql_session.query(ObjectModel).filter_by(user_id=user_id).all()
