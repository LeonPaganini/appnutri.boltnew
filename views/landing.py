import flet as ft
import threading
import time

from assets.landing_page.elements import (
    header,
    hero_section,
    passo_a_passo_section,
    benefits_section,
    video_section,
    social_proof_section,
    differential_section,
    draw_section,
    final_cta_section,
    footer,
)
from assets.landing_page import content

# --- MediaQuery Responsivo Custom ---
class MediaQueryManager:
    def __init__(self, page: ft.Page):
        self.breakpoints = {}
        self.listeners = {}
        self.current_break_point = None

    def on_resized(self, event: ft.WindowResizeEvent):
        self.check_for_updates(event.width)

    def check_for_updates(self, width):
        for name, (min_width, max_width) in self.breakpoints.items():
            if max_width >= width > min_width:
                if self.current_break_point != name:
                    self.current_break_point = name
                    for func in self.listeners.get(name, []):
                        func()

class MediaQuery:
    def __init__(self, page: ft.Page):
        # Um MediaQueryManager por página
        if not hasattr(page, '_media_query'):
            page._media_query = MediaQueryManager(page)
        self.page = page

    @staticmethod
    def handler(event):
        event.page._media_query.on_resized(event)

    def on(self, point, callback_function):
        self.page._media_query.listeners.setdefault(point, [])
        self.page._media_query.listeners[point].append(callback_function)
        self.page._media_query.check_for_updates(self.page.width)

    def off(self, point, callback_function):
        self.page._media_query.listeners[point].remove(callback_function)

    def register(self, point, min_width, max_width):
        self.page._media_query.breakpoints[point] = (min_width, max_width)
        self.page._media_query.listeners.setdefault(point, [])

# --- Função principal da landing page ---
def main(page: ft.Page, respostas=None, auto_advance=True):
    """
    Landing page independente, pode ser chamada direto na rota '/landing'.
    NÃO depende do restante do app.
    """
    respostas={}
    # Configurações visuais e de scroll
    page.title = content.PAGE_TITLE
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.spacing = 0
    page.scroll = ft.ScrollMode.AUTO

    # --- Responsividade customizada ---
    mq = MediaQuery(page)
    mq.register("mobile", 0, 799)
    mq.register("desktop", 800, 10000)
    state = {"breakpoint": None}

    # --- Animação do título piscante ---
    title_blink_on = [True]
    title_ref = ft.Ref[ft.Text]()

    def blink_title():
        while True:
            title_blink_on[0] = not title_blink_on[0]
            if title_ref.current:
                title_ref.current.color = "#2E7D32" if title_blink_on[0] else "#378c3f"
                title_ref.current.update()
            time.sleep(0.7)
    threading.Thread(target=blink_title, daemon=True).start()

    # --- Build layout (chamado no resize) ---
    def build_layout():
        is_mobile = state["breakpoint"] == "mobile"
        max_width = page.width if is_mobile else min(1000, page.width)
        page.views.clear()
        page.views.append(
            ft.View(
                route="/landing",
                controls=[
                    ft.Column(
                        controls=[
                            header(),
                            hero_section(is_mobile, max_width),
                            passo_a_passo_section(is_mobile, max_width),
                            differential_section(is_mobile, max_width),
                            benefits_section(is_mobile, max_width),
                            video_section(is_mobile, max_width),
                            social_proof_section(is_mobile, max_width),
                            draw_section(is_mobile, max_width, title_ref, title_blink_on[0]),
                            final_cta_section(is_mobile, max_width),
                            footer(is_mobile, max_width),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    )
                ],
                scroll=ft.ScrollMode.AUTO,
            )
        )
        page.update()

    # --- Handlers dos breakpoints ---
    def on_mobile():
        state["breakpoint"] = "mobile"
        build_layout()

    def on_desktop():
        state["breakpoint"] = "desktop"
        build_layout()

    mq.on("mobile", on_mobile)
    mq.on("desktop", on_desktop)

    # --- Inicialização responsiva ---
    state["breakpoint"] = "mobile" if page.width < 800 else "desktop"
    build_layout()
    page.on_resize = MediaQuery.handler

# --- Fim do arquivo ---
