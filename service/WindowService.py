"""
界面类
"""
import flet
from flet import *
from config import GlobalConfig
from typing import Optional, Union
from service.ObjectService import *
from util.TimeUtil import timestamp_to_str
from util.StringUtil import is_image_file, is_video_file, video_extensions, image_extensions
from service.UserService import login, register


class WindowService:
    def __init__(self, window_page: Page) -> None:
        self.window_page: Page = window_page
        # 设置窗口标题
        self.window_page.title = GlobalConfig.WINDOW_TITLE
        # 设置窗口大小
        self.window_page.window_width = GlobalConfig.WINDOW_WIDTH
        self.window_page.window_height = GlobalConfig.WINDOW_HEIGHT
        # 设置缓存用户信息的Key
        self.user_key: str = "user_info"
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
            # 先还原各控件
            result_container.content = Text("这里将显示识别结果")
            # 如果结果控件大于2个，说明有文字结果，给干掉
            if len(result_view.controls) > 2:
                result_view.controls.pop(-1)
            # 更新页面
            self.window_page.update()
            if file_picker_result.files:
                file_path = file_picker_result.files[0].path
                # 设置上传图片的路径
                self.window_page.session.set("file_path", file_path)
                # 默认显示文件名
                image_container.content = Text(value=file_path)
                video_container.content = Text(value=file_path)
                # 如果是图片文件，将显示它
                if is_image_file(file_path=file_path):
                    # 将图片显示在视图左侧
                    image_container.content = flet.Image(
                        src=file_path,
                        fit=ImageFit.CONTAIN,
                    )
                    video_container.content = Text("选择视频...")
                elif is_video_file(file_path=file_path):
                    # 将视频显示在视图左侧
                    video_container.content = flet.Video(
                        volume=0,
                        expand=False,
                        show_controls=False,  # 隐藏控制栏
                        playlist=[VideoMedia(file_path)],
                        playlist_mode=PlaylistMode.LOOP,
                        autoplay=True
                    )
                    image_container.content = Text("选择图片...")
                # 各控件点击事件清空，不能点击
                image_container.on_click = None
                video_container.on_click = None
                # 更新页面
                self.window_page.update()

        def detection_object(event: ControlEvent) -> None:
            """
            识别物体
            :param event: 点击事件类
            :return:
            """
            # 先还原各控件
            result_container.content = Text("这里将显示识别结果")
            # 如果结果控件大于2个，说明有文字结果，给干掉
            if len(result_view.controls) > 2:
                result_view.controls.pop(-1)
            result_view.update()
            # 获取上传文件的路径
            file_path: str = self.window_page.session.get("file_path")
            # 判断是否选择了图片
            if not file_path:
                self.open_modal(title="提示", content="未选择文件")
            else:
                # 显示进度环
                detection_container.content = Column(
                    [ProgressRing(), Text("正在识别中...")],
                    horizontal_alignment=CrossAxisAlignment.CENTER,
                )
                detection_container.update()
                # 识别物体
                result: Union[str, tuple] = object_num_detect(file_path=file_path,
                                                              user_id=self.window_page.session.get(
                                                                  self.user_key).get("id"))
                # 如果识别为str类型，则显示提示信息
                if isinstance(result, str):
                    self.open_modal(title="提示", content=result)
                    # 还原各控件
                    image_container.content = Text("选择待识别图片/视频...")
                    result_container.content = Text("这里将显示识别结果")
                    detection_container.content = detection_button
                else:
                    # 定义结果文件路径
                    result_file_path: str = os.path.join("cache", os.path.basename(file_path))
                    # 如果是图片文件，则显示识别结果图片
                    if is_image_file(file_path=file_path):
                        result_container.content = flet.Image(
                            src=result_file_path,  # 识别结果图片路径
                            fit=ImageFit.CONTAIN,
                        )
                    elif is_video_file(file_path=file_path):
                        # 将识别结果显示在视图右侧
                        result_container.content = flet.Video(
                            expand=False,
                            volume=0,
                            show_controls=False,  # 隐藏控制栏
                            playlist=[VideoMedia(result_file_path)],  # 识别结果视频路径
                            playlist_mode=PlaylistMode.LOOP,
                            autoplay=True
                        )
                    # 将识别结果添加到结果视图中
                    result_view.controls.append(Column(
                        spacing=10,
                        controls=[
                            Text(f"识别到的人数：{result[0]}"),
                            Text(f"总推理耗时：{result[1]} ms")
                        ]
                    ))
                    # 文件选择启动点击
                    image_container.on_click = lambda _: files_picker.pick_files(allow_multiple=False,
                                                                                 allowed_extensions=image_extensions)
                    video_container.on_click = lambda _: files_picker.pick_files(allow_multiple=False,
                                                                                 allowed_extensions=video_extensions)
                    # 还原点击识别按钮控件
                    detection_container.content = detection_button
                # 更新页面
                self.window_page.update()

        def logout() -> None:
            """
            退出登录
            :return:
            """
            self.window_page.session.clear()  # 清空Session
            self.window_page.go("/login")  # 返回登录页

        # 添加文件上传
        files_picker: FilePicker = FilePicker(on_result=file_picker_handler)
        self.window_page.overlay.append(files_picker)
        self.window_page.update()
        # 构造点击识别按钮控件
        detection_button: FilledTonalButton = FilledTonalButton(text="点击识别", on_click=detection_object,
                                                                style=ButtonStyle(
                                                                    shape=RoundedRectangleBorder(radius=10)))
        detection_container: Container = Container(
            alignment=alignment.center,  # 居中
            content=detection_button
        )
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
            on_click=lambda _: files_picker.pick_files(allow_multiple=False,
                                                       allowed_extensions=image_extensions)
        )
        # 视频显示控件
        video_container: Container = Container(
            content=Text("选择待识别视频..."),
            ink=True,
            margin=10,
            width=200,
            height=150,
            padding=10,
            border_radius=10,
            alignment=alignment.center,
            border=border.all(2, colors.SURFACE_VARIANT),
            on_click=lambda _: files_picker.pick_files(allow_multiple=False,
                                                       allowed_extensions=video_extensions)
        )
        # 识别结果控件
        result_container: Container = Container(
            content=Text("这里将显示识别结果"),
            margin=10,
            width=300,
            height=250,
            padding=10,
            border_radius=10,
            alignment=alignment.center,
            border=border.all(2, colors.SURFACE_VARIANT),
            ink=True,
            on_click=lambda _: os.system(f"explorer {os.getcwd()}\\cache") if os.path.exists("cache") else None
        )
        # 结果板块
        result_view: Row = Row(
            alignment=MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                Column(
                    controls=[
                        image_container,
                        video_container
                    ]
                ),
                result_container
            ]
        )
        # 绘制页面
        self.window_page.window_height = 800  # 增加窗口高度
        self.window_page.views.append(
            View(
                route="/",
                controls=[
                    AppBar(title=Text("人员数量识别器"), center_title=True, bgcolor=colors.SURFACE_VARIANT),
                    Row(
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            Container(
                                alignment=alignment.center,  # 居中
                                content=Text("当前用户：" + self.window_page.session.get(self.user_key).get("username"))
                            ),
                            Row(
                                alignment=MainAxisAlignment.END,
                                controls=[
                                    Container(
                                        alignment=alignment.center,  # 居中靠右
                                        content=FilledTonalButton(text="查看识别记录",
                                                                  on_click=lambda _: self.window_page.go("/history"),
                                                                  style=ButtonStyle(
                                                                      shape=RoundedRectangleBorder(radius=10)))
                                    ),
                                    Container(
                                        alignment=alignment.center,  # 居中靠右
                                        content=FilledTonalButton(text="退出登录",
                                                                  on_click=lambda _: logout(),
                                                                  style=ButtonStyle(
                                                                      shape=RoundedRectangleBorder(radius=10),
                                                                      bgcolor=colors.RED_400))
                                    )
                                ]
                            )
                        ]
                    ),
                    Divider(),
                    Container(
                        padding=10,
                        content=Column(
                            controls=[
                                Row(
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        Text("设置置信度："),
                                        Slider(
                                            min=0,
                                            max=10,
                                            divisions=10,
                                            value=DetectionConfig.CONFIDENCE_THRESHOLD * 10,  # 默认为当前设置的置信度
                                            label="{value}",
                                            on_change=lambda event: DetectionConfig.set_confidence_threshold(
                                                confidence_threshold=event.control.value / 10)
                                        )
                                    ]
                                ),
                                Row(
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        Text("设置IOU："),
                                        Slider(
                                            min=0,
                                            max=10,
                                            divisions=10,
                                            value=DetectionConfig.IOU * 10,  # 默认为当前设置的IOU
                                            label="{value}",
                                            on_change=lambda event: DetectionConfig.set_iou(
                                                iou=event.control.value / 10)
                                        )
                                    ]
                                )
                            ]
                        )
                    ),
                    result_view,
                    detection_container
                ]
            )
        )

    def register_view(self) -> None:
        """
        注册页
        :return:
        """

        def reg_handler(event: ControlEvent) -> None:
            """
            注册钩子
            :param event: 点击事件类
            :return:
            """
            result: Optional[str] = register(username=username.value, password=password.value)
            # 没有返回数据，说明注册成功了
            if not result:
                self.open_modal(title="提示", content="注册成功，跳转到登录页")
                self.window_page.go("/login")
            else:
                self.open_modal(title="提示", content=result)

        username: TextField = TextField(label="用户名", text_align=TextAlign.LEFT)
        password: TextField = TextField(label="密码", text_align=TextAlign.LEFT, password=True)
        self.window_page.views.append(
            View(
                route="/register",
                controls=[
                    AppBar(title=Text("注册"), center_title=True, bgcolor=colors.SURFACE_VARIANT),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=username
                    ),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=password
                    ),
                    Container(
                        alignment=alignment.center_left,  # 居中向左
                        content=TextButton(
                            text="已有账号，去登录...",
                            on_click=lambda _: self.window_page.go("/login")
                        )
                    ),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=FilledTonalButton(text="提交", on_click=reg_handler,
                                                  style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)))
                    )
                ],
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
            # 返回dict数据，说明登录成功了
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
                        alignment=alignment.center_left,  # 居中向左
                        content=TextButton(
                            text="还没有账号，去注册...",
                            on_click=lambda _: self.window_page.go("/register")
                        )
                    ),
                    Container(
                        alignment=alignment.center,  # 居中
                        content=FilledTonalButton(text="提交", on_click=login_handler,
                                                  style=ButtonStyle(shape=RoundedRectangleBorder(radius=10)))
                    )
                ]
            )
        )

    def history_view(self) -> None:
        """
        历史记录页面
        :return:
        """

        def delete_handler(object_id: int) -> None:
            """
            删除物体记录
            :param object_id: 物体记录ID
            :return:
            """
            delete_object_by_id(object_id=object_id)
            # 重新加载物体记录
            set_object_column_data()

        def set_object_column_data() -> None:
            """
            填充物体记录的列控件
            :return:
            """
            # 先清除物体记录的列控件所有元素
            object_column.controls.clear()
            object_list: list = []
            for object_dict in list_object_by_user_id(user_id=user_info.get("id")):
                # 转换时间戳为字符串
                object_dict["create_time"] = timestamp_to_str(timestamp=object_dict.get("create_timestamp"))
                object_list.append(
                    Container(
                        alignment=alignment.top_left,
                        border=border.all(2, colors.SURFACE_VARIANT),
                        padding=10,
                        content=Row(
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                # 限制图片名称长度
                                Text(
                                    value=f"图片名称：{object_dict.get('image_name')[:28] + '...' if len(object_dict.get('image_name')) > 32 else object_dict.get('image_name')}\n"
                                          f"识别到的人数：{object_dict.get('totality')}\n"
                                          f"识别时间：{object_dict.get('create_time')}",
                                    tooltip=object_dict.get("image_name")),
                                FilledTonalButton(
                                    text="删除",
                                    on_click=lambda event: delete_handler(object_id=event.control.key),
                                    key=object_dict.get("id"),
                                    style=ButtonStyle(shape=RoundedRectangleBorder(radius=10), bgcolor=colors.RED_400)
                                )
                            ]
                        )
                    )
                )
            # 添加当前记录的控件，默认为暂无历史记录控件
            object_column.controls.append(
                Container(
                    alignment=alignment.center,
                    content=Text("暂无历史记录")
                )
            )
            # 如果有记录，则列出记录
            if object_list:
                object_column.controls = object_list
            self.window_page.window_height = 600
            self.window_page.update()

        # 获取用户信息
        user_info: dict = self.window_page.session.get(self.user_key)
        # 定义物体记录的列控件
        object_column: Column = Column(
            alignment=MainAxisAlignment.CENTER,
            spacing=10,
            width=GlobalConfig.WINDOW_WIDTH,
            height=400,
            scroll=ScrollMode.ALWAYS,
            on_scroll_interval=0
        )
        # 填充物体记录的列控件
        set_object_column_data()
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
                    Container(
                        content=object_column,
                        border=border.all(width=2),
                        padding=5
                    )
                ]
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
        elif self.window_page.route == "/register":
            self.register_view()
        elif self.window_page.route == "/":
            self.index_view()
        elif self.window_page.route == "/history":
            self.history_view()
        # 更新页面
        self.window_page.update()
