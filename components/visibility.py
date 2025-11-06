import flet as ft

# Funções
def visibilidade(page: ft.Page, element, is_visible=True):
    element.visible = is_visible
    page.update()

def atualizar_visibilidade(page: ft.Page, config: dict):
    """Atualiza a visibilidade dos elementos com base na configuração atual."""
    for element, visible in config.items():
        visibilidade(page, element, visible)