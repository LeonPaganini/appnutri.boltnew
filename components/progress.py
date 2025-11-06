import flet as ft
import time
import threading
from app.themes.tema import AppTheme

def progress_bar2(page: ft.Page, current_page: int):
    total_pages = 7
    pb = ft.ProgressBar(
        width=400,
        value=current_page / total_pages,
        color=AppTheme.get_color("PRIMARY_COLOR")
    )

    def animate_progress(new_page: int):
        target_value = new_page / total_pages
        while pb.value < target_value:
            pb.value = min(pb.value + 0.01, target_value)
            time.sleep(0.02)
            page.update()

    def update_progress(new_page: int):
        threading.Thread(target=animate_progress, args=(new_page,)).start()

    return pb, update_progress


def progress_bar(step: int):
    progress_colors = ["blue" if i < step else "lightblue" for i in range(7)]
    return ft.Row(
        controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE, color=progress_colors[i], size=24)
            if i == step - 1 else ft.Container(width=20, height=2, bgcolor=progress_colors[i])
            for i in range(7)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=4,
    )