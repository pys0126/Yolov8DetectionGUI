from typing import Optional
from model.UserModel import UserModel
from util.MysqlUtil import mysql_session, auto_close_session


@auto_close_session
def insert(user_model: UserModel) -> None:
    """
    插入用户
    """
    mysql_session.add(instance=user_model)
    mysql_session.commit()


@auto_close_session
def update(user_model: UserModel) -> None:
    """
    更新用户
    """
    mysql_session.merge(instance=user_model)
    mysql_session.commit()


@auto_close_session
def delete(user_model: UserModel) -> None:
    """
    删除用户
    """
    mysql_session.delete(instance=user_model)
    mysql_session.commit()


@auto_close_session
def find_by_id(user_id: int) -> Optional[UserModel]:
    return mysql_session.query(UserModel).filter_by(id=user_id).first()


@auto_close_session
def find_by_username(username: str) -> Optional[UserModel]:
    return mysql_session.query(UserModel).filter_by(username=username).first()
