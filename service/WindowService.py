"""
界面类
"""
from flet import *
from typing import Optional, Union
from config import GlobalConfig
from service.UserService import login
from service.ObjectService import object_num_detect, list_object_by_user_id, delete_object_by_id
from util.TimeUtil import timestamp_to_str


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
        def file_picker_handler(file_picker_result: FilePickerResultEvent) -> None:
            """
            文件选择器钩子
            :param file_picker_result:
            :return:
            """
            if file_picker_result.files:
                file_path = file_picker_result.files[0].path
                # 设置上传图片的路径
                self.window_page.session.set("file_path", file_path)
                # 将图片显示在视图左侧
                image_container.content = Image(
                    src=file_path,
                    fit=ImageFit.CONTAIN,
                )
                image_container.update()

        def detection_image(event: ControlEvent) -> None:
            """
            识别图片
            :param event: 点击事件类
            :return:
            """
            # 获取上传图片的路径
            file_path: str = self.window_page.session.get("file_path")
            # 判断是否选择了图片
            if not file_path:
                self.open_modal(title="提示", content="未选择图片")
            else:
                # 先显示进度环
                result_container.content = Column(
                    [ProgressRing(), Text("正在识别中...")],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                )
                result_container.update()
                # 识别图片
                result: Union[str, int] = object_num_detect(image_path=file_path,
                                                            user_id=self.window_page.session.get(
                                                                self.user_key).get("id"))
                # 如果识别为str类型，则显示提示信息
                if isinstance(result, str):
                    self.open_modal(title="提示", content=result)
                    # 还原图片显示控件
                    image_container.content = Text("选择待识别图片...")
                else:
                    # 将识别结果显示在视图右侧
                    result_container.content = Text(f"识别到的人数：{result}")
                    result_container.update()
        # 添加文件上传
        files_picker: FilePicker = FilePicker(on_result=file_picker_handler)
        self.window_page.overlay.append(files_picker)
        self.window_page.update()
        # 图片显示控件
        image_container: Container = Container(
            content=Text("选择待识别图片..."),
            ink=True,
            margin=10,
            width=200,
            height=150,
            padding=10,
            border_radius=10,
            alignment=alignment.center,
            border=border.all(2, colors.SURFACE_VARIANT),
            on_click=lambda _: files_picker.pick_files(allow_multiple=False)
        )
        # 识别结果控件
        result_container: Container = Container(
            content=Text("这里将显示识别结果"),
            margin=10,
            width=200,
            height=150,
            padding=10,
            border_radius=10,
            alignment=alignment.center,
            border=border.all(2, colors.SURFACE_VARIANT)
        )
        # 绘制页面
        self.window_page.views.append(
            View(
                route="/",
                controls=[
                    AppBar(title=Text("人员数量识别器"), center_title=True, bgcolor=colors.SURFACE_VARIANT),
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Container(
                                alignment=alignment.top_left,  # 居中
                                content=Text("当前用户：" + self.window_page.session.get(self.user_key).get("username"))
                            ),
                            Container(
                                alignment=alignment.top_right,  # 居中
                                content=FilledTonalButton("查看识别记录",
                                                          on_click=lambda _: self.window_page.go("/history"),
                                                          style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)))
                            )
                        ]
                    ),
                    Divider(),
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            image_container,
                            result_container
                        ]
                    ),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=FilledTonalButton(text="点击识别图片", on_click=detection_image,
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
            """
            登录钩子
            :param event: 点击事件类
            :return:
            """
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

    def history_view(self) -> None:
        """
        历史记录页面
        :return:
        """
        # 获取用户信息
        user_info: dict = self.window_page.session.get(self.user_key)
        # 构造列表元素的控件
        list_view_data: list = []
        for object_dict in list_object_by_user_id(user_info.get("id")):
            # 转换时间戳为字符串
            object_dict["create_time"] = timestamp_to_str(timestamp=object_dict.get("create_timestamp"))
            list_view_data.append(
                Container(
                    alignment=alignment.top_left,
                    border=border.all(2, colors.SURFACE_VARIANT),
                    padding=10,
                    content=Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Text(f"图片名称：{object_dict.get('image_name')}\n识别到的人数：{object_dict.get('totality')}"),
                            Text(f"识别时间：{object_dict.get('create_time')}"),
                            FilledTonalButton(
                                text="删除",
                                on_click=lambda _: delete_object_by_id(object_id=object_dict.get("id")),
                                style=ButtonStyle(shape=RoundedRectangleBorder(radius=10), color=colors.RED_ACCENT)
                            )
                        ]
                    )
                )
            )
        self.window_page.views.append(
            View(
                route="/history",
                controls=[
                    AppBar(title=Text("识别历史记录"), center_title=True, bgcolor=colors.SURFACE_VARIANT),
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Container(
                                alignment=alignment.top_left,  # 居中
                                content=Text(f"当前用户：{user_info.get('username')}")
                            ),
                            Container(
                                alignment=alignment.top_right,  # 居中
                                content=FilledTonalButton("返回首页",
                                                          on_click=lambda _: self.window_page.go("/"),
                                                          style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)))
                            )
                        ]
                    ),
                    Divider(),
                    ListView(
                        data=list_object_by_user_id(user_info.get("id")),
                        spacing=10,
                        padding=10,
                        auto_scroll=True,
                        controls=list_view_data
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
        elif self.window_page.route == "/history":
            self.history_view()
        # 更新页面
        self.window_page.update()
