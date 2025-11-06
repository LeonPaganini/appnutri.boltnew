import flet as ft
import asyncio
from app.themes.tema import AppTheme
from app.components.visibility import *

# Botão continuar com condição
#CRIA BOTÃO COM CONDICIONAIS
def create_button_with_condition(text: str, color: str, on_click, condition, width: int = 150, height: int = 50):
    """Cria um botão estilizado com uma condição para a ação."""
    def on_click_with_condition(e):
        if condition():
            on_click(e)
        else:
            e.page.snack_bar = ft.SnackBar(ft.Text("Por favor, preencha todos os campos."), open=True)
            e.page.update()

    return ft.Container(
        content=ft.Text(text, color=ft.Colors.WHITE),
        on_click=on_click_with_condition,
        width=width,
        height=height,
        bgcolor=color,
        border_radius=10,
        alignment=ft.alignment.center,
        padding=10,
    )



def create_continue_button(text: str, is_valid: callable, on_click: callable):
    btn = ft.ElevatedButton(
        text=text,
        on_click=lambda e: on_click(e) if not btn.disabled else None,
        bgcolor=AppTheme.get_color("BUTTON_BG_COLOR_DISABLED"),
        color=AppTheme.get_color("TEXT_COLOR"),
        width=200,
        height=50,
        style=AppTheme.button_style(AppTheme.get_color("BUTTON_BG_COLOR")),
        disabled=True,
    )

    def update_state():
        if is_valid():
            btn.disabled = False
            btn.bgcolor = AppTheme.get_color("BUTTON_BG_COLOR")
            btn.color = ft.colors.WHITE
        else:
            btn.disabled = True
            btn.bgcolor = AppTheme.get_color("BUTTON_BG_COLOR_DISABLED")
            btn.color = AppTheme.get_color("TEXT_COLOR")
        return btn

    btn.update_state = update_state
    return btn

# Botão voltar
def back_button(page: ft.Page, route: str, current_page: int, update_progress):
    def back_button_action(e):
        nonlocal current_page
        if current_page > 1:
            current_page -= 1
            update_progress(current_page)
        page.go(route)

    return ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color=AppTheme.get_color("VOLTAR_COLLOR_BUTTON"),
        on_click=back_button_action,
        bgcolor=AppTheme.get_color("FIELD_BG_COLOR"),
        icon_size=18,
    )

# Botão gênero antigo
def create_button_genere(text: str, icon: ft.Icons, color: str, on_click, condition, width: int = 150, height: int = 50, bg_color_key: str = None):
    def on_click_with_condition(e):
        if condition():
            on_click(e)
        else:
            e.page.snack_bar = ft.SnackBar(ft.Text("Por favor, preencha todos os campos."), open=True)
            e.page.update()

    background_color = AppTheme.get_color(bg_color_key) if bg_color_key else color

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, color=AppTheme.get_color("ICON_COLOR"), size=24),
                ft.Text(text, color=AppTheme.get_color("TEXT_COLOR"))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        on_click=on_click_with_condition,
        width=width,
        height=height,
        bgcolor=background_color,
        border_radius=10,
        alignment=ft.alignment.center,
        padding=10,
    )

# Botão voltar condicional
def back_button_conditional(page: ft.Page, route: str, elemento_visivel1, elemento_visivel2, page_history, current_page: int, update_progress):
    def back_button_action(e):
        nonlocal current_page
        if elemento_visivel1.visible and elemento_visivel2.visible:
            page.go(route)
        else:
            if current_page > 1:
                current_page -= 1
                update_progress(current_page)
            voltar(e, page_history, page)

    return ft.IconButton(
        icon=ft.Icons.ARROW_BACK,
        icon_color=AppTheme.get_color("VOLTAR_COLLOR_BUTTON"),
        on_click=back_button_action,
        bgcolor=AppTheme.get_color("FIELD_BG_COLOR"),
        icon_size=18,
    )

def voltar(e, page_history, page):
    if page_history:
        last_state = page_history.pop()
        atualizar_visibilidade(page, last_state)