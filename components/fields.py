import flet as ft
from app.themes.tema import AppTheme

def create_text_field(
    label: str,
    border_color: str,
    fill_color: str,
    page: ft.Page = None,
    alignment: ft.Alignment = None,
    width: int = 400,  # ✅ Largura padrão ajustável
    cache_key: str = None,
    keyboard_type: ft.KeyboardType = ft.KeyboardType.TEXT,
    on_blur=None,
    on_change=None,
    on_focus=None,
    padding=5,
    with_button=False,     # ✅ Adiciona botão lateral
    on_button_click=None   # ✅ Callback opcional do botão
):
    """
    Campo de texto customizado com adaptação de tema, cache no client_storage e botão opcional "✓".

    - width: controla largura do TextField.
    - with_button: se True, adiciona botão ao lado.
    - on_button_click: função extra ao clicar no botão.
    """
    is_dark = page.theme_mode == ft.ThemeMode.DARK if page else False

    text_color = AppTheme.get_color_by_mode("TEXT_COLOR", is_dark_mode=is_dark)
    bg_color = AppTheme.get_color_by_mode("TEXT_FIELD_COLOR", is_dark_mode=is_dark)
    primary_color = AppTheme.get_color_by_mode("PRIMARY_COLOR", is_dark_mode=is_dark)

    # Recupera valor salvo no client_storage
    value = ""
    if page is not None and cache_key:
        value = page.client_storage.get(cache_key) or ""

    def _on_change(e):
        if page is not None and cache_key:
            page.client_storage.set(cache_key, e.control.value)
        if on_change:
            on_change(e)

    campo = ft.TextField(
        label=label,
        value=value,
        border_color=border_color,
        border_radius=8,
        bgcolor=bg_color,
        color=text_color,
        width=width,  # ✅ Controla largura
        keyboard_type=keyboard_type,
        label_style=ft.TextStyle(
            color=text_color,
            size=11
        ),
        dense=True,
        height=40,
        on_blur=on_blur,
        on_change=_on_change,
    )

    # AJUSTE: Foco seguro (não quebra se controle ainda não foi adicionado)
    if page is not None:
        def focar(e):
            try:
                # Só tenta scrollar se a view já foi adicionada à página e o campo está na árvore
                if page.views and hasattr(campo, "offset") and hasattr(page, "scroll_to"):
                    page.scroll_to(offset=campo.offset, duration=150)
                if on_focus:
                    on_focus(e)
            except AssertionError as err:
                print(f"[DEBUG] Foco/scroll ignorado (campo não está na árvore): {err}")
            except Exception as err:
                print(f"[DEBUG] Erro ao tentar focar/scrollar campo: {err}")
        campo.on_focus = focar
    else:
        campo.on_focus = on_focus

    if with_button:
        def _button_click(e):
            if page is not None and cache_key:
                page.client_storage.set(cache_key, campo.value)
            if on_button_click:
                on_button_click(e, campo)
            campo.blur()
            page.snack_bar = ft.SnackBar(content=ft.Text("Informação salva!"))
            page.snack_bar.open = True
            page.update()

        botao = ft.ElevatedButton(
            icon=ft.Icon(ft.icons.CHECK, color=primary_color),
            height=40,
            width=50,
            style=ft.ButtonStyle(
                bgcolor=primary_color,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=0,
            ),
            on_click=_button_click
        )

        # ✅ TextField com largura controlada + botão colado
        return ft.Row(
            controls=[
                campo,
                botao
            ],
            alignment=ft.MainAxisAlignment.CENTER,  # ✅ Força centralização horizontal
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
    else:
        return ft.Container(
            content=campo,
            padding=padding,
            alignment=alignment
        )
