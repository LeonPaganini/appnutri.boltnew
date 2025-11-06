import flet as ft
import time
from app.themes.tema import AppTheme

def criar_chip_padrao2(
    texto: str,
    descricao: str,
    valor,
    on_select,
    grupo: list = None,
    selecionar_unico: bool = True,
    icone=None,
    quantidade_icones: int = 1,
    chip_width: int = 60,
    chip_height=None,
    icon_size: int = 40,
    chip_padding=ft.padding.symmetric(vertical=8, horizontal=8),
    layout_em_coluna: bool = False,
    show_checkmark: bool = False,
    tipo_icone: str = "icone",
    controle_externo: bool = False,
    cor_gradiente_1: str = None,
    cor_gradiente_2: str = None,
    cor_texto: str = None,
    cor_icon: str = None
):
    def get_gradient(selecionado):
        cor1 = cor_gradiente_1 or (AppTheme.get_color("CHIP_GRADIENT_SELECTED_1") if selecionado else AppTheme.get_color("CHIP_GRADIENT_UNSELECTED_1"))
        cor2 = cor_gradiente_2 or (AppTheme.get_color("CHIP_GRADIENT_SELECTED_2") if selecionado else AppTheme.get_color("CHIP_GRADIENT_UNSELECTED_2"))
        return ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[cor1, cor2]
        )

    layout_chip = ft.Column if layout_em_coluna else ft.Row
    alinhamento_layout = ft.MainAxisAlignment.CENTER if layout_em_coluna else ft.MainAxisAlignment.START

    if icone is None:
        # ✅ Versão texto puro reativada
        chip = ft.Container(
            content=ft.Text(
                texto,
                size=14,
                weight=ft.FontWeight.BOLD,
                color=cor_texto or AppTheme.get_color("CHIP_TEXT_COLOR"),
                text_align=ft.TextAlign.CENTER
            ),
            alignment=ft.alignment.center,
            width=chip_width,
            height=chip_height or 46,
            border_radius=AppTheme.BORDER_RADIUS,
            padding=chip_padding,
            gradient=get_gradient(False),
            scale=1,
            animate=ft.animation.Animation(200, "easeInOut"),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color="rgba(0, 0, 0, 0.25)",
                offset=ft.Offset(2, 3)
            )
        )
    else:
        icones = [
            ft.Image(src=icone, width=icon_size, height=icon_size, fit=ft.ImageFit.CONTAIN)
            if tipo_icone == "imagem"
            else ft.Icon(icone, size=icon_size, color=cor_icon or AppTheme.get_color("CHIP_ICON_COLOR"))
            for _ in range(quantidade_icones)
        ]

        chip = ft.Container(
            content=layout_chip(
                controls=[
                    ft.Container(
                        content=ft.Row(
                            controls=icones,
                            spacing=10,
                            alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        ),
                        width=chip_width,
                        alignment=ft.alignment.center
                    ),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    texto,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    text_align=ft.TextAlign.CENTER,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    color=cor_texto or AppTheme.get_color("CHIP_TEXT_COLOR")
                                ),
                                ft.Text(
                                    descricao,
                                    size=12,
                                    text_align=ft.TextAlign.CENTER,
                                    no_wrap=False,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.CLIP,
                                    color=cor_texto or AppTheme.get_color("CHIP_TEXT_COLOR"),
                                    selectable=False
                                )
                            ],
                            spacing=3,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        alignment=ft.alignment.center_left
                    )
                ],
                alignment=alinhamento_layout
            ),
            gradient=get_gradient(False),
            padding=chip_padding,
            height=chip_height or 56,
            border_radius=AppTheme.BORDER_RADIUS,
            alignment=ft.alignment.center,
            scale=1,
            animate=ft.animation.Animation(200, "easeInOut"),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color="rgba(0, 0, 0, 0.25)",
                offset=ft.Offset(2, 3)
            )
        )

    chip.selected = False
    if grupo is not None:
        grupo.append(chip)

    def ao_clicar(e):
        chip.scale = 1.05
        chip.gradient = get_gradient(chip.selected)
        chip.update()
        time.sleep(0.08)
        chip.scale = 1.0
        chip.update()

        if not controle_externo:
            if selecionar_unico and grupo:
                for outro_chip in grupo:
                    if outro_chip != chip and outro_chip.selected:
                        outro_chip.selected = False
                        outro_chip.gradient = get_gradient(False)
                        outro_chip.update()

            chip.selected = not chip.selected
            chip.gradient = get_gradient(chip.selected)
            chip.update()

        if on_select:
            on_select(e, valor)

    chip.on_click = ao_clicar

    def apply_selected_state(selected: bool):
        chip.selected = selected
        chip.gradient = get_gradient(selected)
        # Evitar update quando o chip ainda não foi adicionado à página
        try:
            chip.update()
        except AssertionError:
            # Silenciosamente ignora se ainda não estiver na árvore.
            # Quem chamou deve fazer page.update() depois.
            pass

    chip.apply_selected_state = apply_selected_state

    return chip



# -----------------
# 💬 Código antigo apenas para histórico
# def get_gradient(selecionado):
#     return ft.LinearGradient(
#         begin=ft.alignment.top_left,
#         end=ft.alignment.bottom_right,
#         colors=[
#             AppTheme.get_color("CHIP_GRADIENT_SELECTED_1") if selecionado else AppTheme.get_color("CHIP_GRADIENT_UNSELECTED_1"),
#             AppTheme.get_color("CHIP_GRADIENT_SELECTED_2") if selecionado else AppTheme.get_color("CHIP_GRADIENT_UNSELECTED_2"),
#         ]
#     )