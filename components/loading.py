import flet as ft

def show_loading(page, mensagem="Carregando..."):
    # Cria um AlertDialog com animação de carregamento
    loading_dialog = ft.AlertDialog(
        modal=True,
        content=ft.Row([
            ft.ProgressRing(),
            ft.Text(mensagem, size=14, weight=ft.FontWeight.BOLD)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.CENTER,
        bgcolor=ft.Colors.WHITE70,
    )
    page.overlay.append(loading_dialog)
    loading_dialog.open = True
    page.update()
    return loading_dialog

def hide_loading(page):
    if page.dialog:
        page.dialog.open = False
        page.update()
