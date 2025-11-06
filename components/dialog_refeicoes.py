import flet as ft
from app.themes.tema import AppTheme


def criar_dialog_padrao(
    page,
    titulo: str,
    elementos_conteudo: list,
    on_confirm,
    texto_botao: str = "OK",
    altura_dialog=None,
    largura_maxima=420,
    largura_minima=320
):
    """
    🔥 Função padrão para qualquer AlertDialog no app.

    • page ➝ obrigatório (para pegar page.window_width)
    • titulo ➝ string com título do dialog
    • elementos_conteudo ➝ lista de Containers, Rows, Columns ou qualquer controle
    • on_confirm ➝ função callback do botão de ação
    • texto_botao ➝ texto do botão (default "OK")
    • altura_dialog ➝ se não passado, autoajusta
    """

    margem_lateral = 2
    largura_disponivel = page.window_width - (margem_lateral * 2)
    largura_dialog = max(min(largura_disponivel, largura_maxima), largura_minima)

    container_conteudo = ft.Container(
        content=ft.Column(
            controls=elementos_conteudo,
            scroll=ft.ScrollMode.AUTO,
            spacing=2
        ),
        width=largura_dialog,
        height=altura_dialog if altura_dialog else None,
        padding=2
    )

    return ft.AlertDialog(
        modal=False,
        adaptive=True,
        content_padding=8,
        title=ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD),
        content=container_conteudo,
        actions=[
            ft.TextButton(
                texto_botao,
                on_click=on_confirm,
                style=ft.ButtonStyle(
                    padding=2,
                    bgcolor=AppTheme.get_color("PRIMARY_COLOR"),
                    color=AppTheme.get_color("BUTTON_COLOR_TEXT"),
                    shape=ft.RoundedRectangleBorder(radius=6)
                )
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )