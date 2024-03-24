import flet as ft


def main(page: ft.Page):
    cl = ft.Column(
        spacing=10,
        scroll=ft.ScrollMode.ALWAYS,
        on_scroll_interval=0
    )
    for i in range(0, 50):
        cl.controls.append(ft.Text(f"Text line {i}"))

    page.add(ft.Container(cl, border=ft.border.all(1)))


ft.app(main)
