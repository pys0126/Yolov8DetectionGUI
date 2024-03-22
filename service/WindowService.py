"""
界面类
"""
import os
from typing import Optional, Union
from flet import *
from config import GlobalConfig
from service.UserService import login


class WindowService:
    def __init__(self, window_page: Page) -> None:
        self.window_page = window_page
        # 设置窗口标题
        self.window_page.title = GlobalConfig.WINDOW_TITLE
        # 设置窗口大小
        self.window_page.window_width = GlobalConfig.WINDOW_WIDTH
        self.window_page.window_height = GlobalConfig.WINDOW_HEIGHT
        # 设置缓存用户信息的Key
        self.user_key = "user_info"
        # 构建页面
        self.build()
        # 定义一些钩子
        self.hook()

    def build(self) -> None:
        """
        构建页面
        :return:
        """
        if not self.window_page.session.get(self.user_key):
            self.window_page.go("/login")
        else:
            self.index_view()

    def index_view(self) -> None:
        """
        主页
        :return:
        """

        def upload_file(file_picker_result: FilePickerResultEvent) -> None:
            """
            文件上传
            :param file_picker_result:
            :return:
            """
            file_path: str = file_picker_result.files[0].path
            filename: str = os.path.basename(file_path)
            upload_button.content = Image(
                src=file_picker_result.files[0].path,
                fit=ImageFit.CONTAIN,
            )
            upload_button.update()

        # 文件上传按钮
        upload_button: Container = Container(
            content=Text("这里将显示图片"),
            margin=10,
            padding=10,
            alignment=alignment.center,
            width=200,
            height=150,
            border_radius=10
        )
        # 识别结果控件
        result_container: Container = Container(
            content=Text("这里将显示识别结果"),
            margin=10,
            padding=10,
            alignment=alignment.center,
            width=200,
            height=150,
            border_radius=10
        )
        # 添加文件上传
        upload_picker: FilePicker = FilePicker(on_result=upload_file)
        self.window_page.overlay.append(upload_picker)
        self.window_page.update()
        # 绘制页面
        self.window_page.views.append(
            View(
                route="/",
                controls=[
                    AppBar(title=Text("主页"), center_title=True, bgcolor=colors.SURFACE_VARIANT),
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Container(
                                alignment=alignment.top_left,  # 居中
                                content=Text("当前用户：" + self.window_page.session.get(self.user_key).get("username"))
                            ),
                            Container(
                                alignment=alignment.top_right,  # 居中
                                content=FilledTonalButton("查看历史记录",
                                                          on_click=lambda _: self.window_page.go("/history"),
                                                          style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)))
                            )
                        ]
                    ),
                    Divider(),
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            upload_button,
                            result_container
                        ]
                    ),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=FilledTonalButton(text="点击识别图片",
                                                  on_click=upload_picker.pick_files(allow_multiple=False),
                                                  style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)))
                    )
                ]
            )
        )

    def login_view(self) -> None:
        """
        登录页
        :return:
        """

        def login_handler(event: ControlEvent) -> None:
            result: Union[str, dict] = login(username=username.value, password=password.value)
            # 没有返回数据，说明登录成功了
            if isinstance(result, dict):
                self.window_page.session.set(self.user_key, result)
                self.window_page.go("/")
            elif isinstance(result, str):
                self.open_modal(title="提示", content=result)
            else:
                self.open_modal(title="提示", content="未知错误")

        username: TextField = TextField(label="用户名", text_align=TextAlign.LEFT)
        password: TextField = TextField(label="密码", text_align=TextAlign.LEFT, password=True)
        self.window_page.views.append(
            View(
                route="/login",
                controls=[
                    AppBar(title=Text("登录"), center_title=True, bgcolor=colors.SURFACE_VARIANT),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=username
                    ),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=password
                    ),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=FilledTonalButton(text="提交", on_click=login_handler,
                                                  style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)))
                    )
                ],
            )
        )

    def alert_dialog(self, title: str = "提示", content: Optional[str] = None) -> AlertDialog:
        """
        模态框弹窗
        :param title: 标题
        :param content: 内容
        :return:
        """
        return AlertDialog(
            modal=True,
            title=Text(title),
            content=None if content is None else Text(content),
            actions=[
                FilledTonalButton("确定", on_click=self.close_modal,
                                  style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)))
            ],
            actions_alignment=MainAxisAlignment.CENTER
        )

    def close_modal(self, _) -> None:
        """
        关闭弹窗
        :return:
        """
        self.window_page.dialog.open = False
        self.window_page.update()

    def open_modal(self, title: str = "提示", content: Optional[str] = None) -> None:
        """
        打开弹窗
        :return:
        """
        self.window_page.dialog = self.alert_dialog(title, content)
        self.window_page.dialog.open = True
        self.window_page.update()

    def hook(self) -> None:
        """
        定义一些钩子
        :return:
        """
        # 定义一些事件钩子
        self.window_page.on_route_change = self.route_change

    def route_change(self, route_change_event: RouteChangeEvent):
        """
        路由变化时调用
        :param route_change_event: RouteChangeEvent对象
        :return:
        """
        # 清空页面
        self.window_page.views.clear()
        # 根据路由，构建页面
        if self.window_page.route == "/login":
            self.login_view()
        elif self.window_page.route == "/":
            self.index_view()
        # 更新页面
        self.window_page.update()
