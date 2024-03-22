from util.StringUtil import *
from mapper.UserMapper import *
from typing import Optional, Union


def register(username: str, password: str) -> Optional[str]:
    """
    注册
    :param username:
    :param password:
    :return:
    """
    # 判断用户名是否存在
    if find_by_username(username=username):
        return "该用户名已存在"
    # 新增用户
    insert(user_model=UserModel(
        username=username,
        password=md5_encode(text=password)
    ))


def login(username: str, password: str) -> Union[str, dict]:
    """
    登录
    :param username:
    :param password:
    :return:
    """
    user_model: Optional[UserModel] = find_by_username(username=username)
    # 进行验证
    if not user_model:
        return "该用户不存在"
    if user_model.password != md5_encode(text=password):
        return "密码错误"
    # 返回用户信息
    result: dict = user_model.to_dict()
    result.pop("password")  # 删除密码
    return result
