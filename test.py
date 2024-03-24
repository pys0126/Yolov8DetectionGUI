import flet as ft

def main(page: ft.Page):
    page.title = "图片示例"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 50
    page.update()

    img = ft.Image(
        src=r"C:\Users\uodrad\Pictures\640.jpg",
        width=100,
        height=100,
        fit=ft.ImageFit.CONTAIN,
    )
    images = ft.Row(expand=1, wrap=False, scroll="always")

    page.add(img, images)
    page.update()

ft.app(target=main)