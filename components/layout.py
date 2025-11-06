import flet as ft
from app.themes.tema import AppTheme


def configure_page(page: ft.Page):
    """Configurações globais da página."""
    page.title = "Anamnese"
    page.padding = 0
    # 🔥 Antes: SYSTEM, agora pode fixar LIGHT se quiser
    page.theme_mode = ft.ThemeMode.LIGHT
    page.expand = True
    page.window.min_width = 390
    page.window.min_height = 600

    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=AppTheme.get_color("PRIMARY_COLOR"),
            background=AppTheme.get_color("BACKGROUND_COLOR"),
            surface=AppTheme.get_color("CARD_COLOR"),
            on_primary=AppTheme.get_color("BUTTON_COLOR_TEXT"),
            on_background=AppTheme.get_color("TEXT_COLOR"),
        )
    )

    # 🔥 Comentado tema escuro, pois não será mais usado
    # page.dark_theme = ft.Theme(
    #     color_scheme=ft.ColorScheme(
    #         primary=AppTheme.get_color("PRIMARY_COLOR"),
    #         background=AppTheme.get_color("DARK_BACKGROUND_COLOR"),
    #         surface=AppTheme.get_color("DARK_CARD_COLOR"),
    #         on_primary=AppTheme.get_color("DARK_BUTTON_TEXT_COLOR"),
    #         on_background=AppTheme.get_color("DARK_TEXT_COLOR"),
    #     )
    # )

    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.START

def background_container(dark_mode=False):
    """Retorna um Container expandido com cor ou imagem de fundo."""
    # 🔥 Modo escuro comentado
    # if dark_mode:
    #     return ft.Container(bgcolor=ft.Colors.BLACK, expand=True)
    return ft.Container(
        alignment=ft.alignment.center,
        content=ft.Image(
            src="https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fnutri_0001%2Fbackground_image2.jpeg?alt=media&token=7afff63b-e63e-46a7-bca1-c1c10a149fad",
            fit=ft.ImageFit.COVER,
        ),
        expand=True,
    )

def background_container2(dark_mode=False):
    # 🔥 Modo escuro comentado
    # if dark_mode:
    #     return ft.Container(bgcolor=ft.Colors.BLACK, expand=True)
    return ft.Container(
        content=ft.Image(
            src="https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fnutri_0001%2Fbackground_image2.jpeg?alt=media&token=7afff63b-e63e-46a7-bca1-c1c10a149fad",
            fit=ft.ImageFit.COVER,
        ),
        expand=True,
    )

def header_bar(page, titulo, back_btn=None, progresso=None):
    return ft.Container(
        content=ft.Row(
            controls=[
                back_btn if back_btn else ft.Container(width=40),  # ou None para vazar espaço
                ft.Container(expand=1),  # espaço para centralizar o título
                ft.Text(titulo, size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, expand=10),
                ft.Container(expand=1),  # espaço à direita, se precisar
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.START,
        ),
        padding=ft.padding.symmetric(vertical=10, horizontal=16),
        bgcolor=None,
    )

def pagina_base(page, route, titulo, conteudo: list,
                progresso=None, back_btn=None,
                exibir_botao_continuar=False, botao_continuar=None,
                scroll_ativo=False):

    dark_mode_ativo = page.theme_mode == ft.ThemeMode.DARK

    # 🔥 Conteúdo da página
    col_conteudo = [
        ft.Container(
            content=ft.Text(
                titulo, size=20, weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.all(4)
        ),
        ft.Divider(height=1, color=ft.Colors.GREY_300, thickness=1),
        *conteudo,
    ]

    if back_btn:
        col_conteudo.insert(0, ft.Row([back_btn], alignment=ft.MainAxisAlignment.START))
    if progresso:
        col_conteudo.insert(1, progresso)
    if exibir_botao_continuar and botao_continuar:
        col_conteudo.append(
            ft.Container(
                content=ft.Row(
                    controls=[botao_continuar],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(0)
            )
        )

    return ft.View(
        route=route,
        controls=[
            ft.Container(  # 🔥 Controla altura total da página
                expand=True,
                content=ft.Stack([
                    # 🔥 Background
                    background_container(dark_mode=dark_mode_ativo),

                    # 🔥 Conteúdo com scroll
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.top_center,
                        padding=ft.padding.symmetric(horizontal=0),
                        content=ft.Container(
                            width=page.window_width if page.window_width else 350,
                            content=ft.Column(
                            controls=col_conteudo,
                            alignment=ft.MainAxisAlignment.START,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            scroll=ft.ScrollMode.HIDDEN if scroll_ativo else None,
                            expand=True  # 🔥 Obrigatório para preencher altura e permitir scroll
                        )
                        
                        )
                    )
                ])
            )
        ]
    )


def pagina_base_responsivo(
    page: ft.Page,
    route: str,
    titulo: str,
    conteudo: list,
    progresso=None,
    back_btn=None,
    exibir_botao_continuar=False,
    botao_continuar=None,
    altura_dinamica=False,  # ✅ Novo argumento
):
    page.title = titulo
    page.bgcolor = ft.Colors.TRANSPARENT
    page.padding = 0
    page.scroll = ft.ScrollMode.ALWAYS
    dark_mode_ativo = page.theme_mode == ft.ThemeMode.DARK

    def on_resize(e):
        page.update()
    page.on_resized = on_resize

    largura = page.window_width or 390
    max_width = min(390, largura)
    padding = 12

    # 🔥 Conteúdo
    col_conteudo = []

    if back_btn:
        col_conteudo.append(ft.Row([back_btn], alignment=ft.MainAxisAlignment.START))
    if progresso:
        col_conteudo.append(progresso)

    col_conteudo.append(
        ft.Container(
            content=ft.Text(
                titulo,
                size=20,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=ft.padding.all(4),
        )
    )
    col_conteudo.append(ft.Divider(height=1, color=ft.Colors.GREY_300, thickness=1))
    col_conteudo.extend(conteudo)

    if exibir_botao_continuar and botao_continuar:
        col_conteudo.append(
            ft.Container(
                content=ft.Row(controls=[botao_continuar], alignment=ft.MainAxisAlignment.CENTER),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=10),
            )
        )

    # ✅ Definir altura do container conforme argumento
    if altura_dinamica:
        altura_container = None  # altura dinâmica
        expand_container = True
    else:
        altura_container = page.height * 0.95
        expand_container = False

    background_image_url = "https://i.ibb.co/JW6j1Cy8/background-nutri-0003.jpg"

    return ft.View(
        route=route,
        controls=[
            ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        alignment=ft.alignment.center,
                        expand=True,
                        content=ft.Image(
                            src=background_image_url,
                            fit=ft.ImageFit.COVER,
                            width=page.width,
                            height=page.height,
                        ),
                    ),
                    ft.Container(
                        bgcolor=ft.Colors.with_opacity(0.4, ft.Colors.BLACK),
                        expand=True,
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.alignment.top_center,
                        padding=padding,
                        content=ft.SafeArea(
                            ft.Column(
                                scroll=ft.ScrollMode.ALWAYS,
                                controls=[
                                    ft.Container(
                                        width=max_width,
                                        height=altura_container,
                                        expand=expand_container,
                                        bgcolor=ft.Colors.with_opacity(0.50, ft.Colors.WHITE)
                                        if not dark_mode_ativo
                                        else ft.Colors.with_opacity(0.50, ft.Colors.BLACK),
                                        border_radius=12,
                                        padding=padding,
                                        content=ft.Column(
                                            controls=col_conteudo,
                                            alignment=ft.MainAxisAlignment.START,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=18,
                                        ),
                                        shadow=ft.BoxShadow(
                                            spread_radius=0,
                                            blur_radius=12,
                                            color="#11111122",
                                            offset=ft.Offset(0, 4),
                                        ),
                                    )
                                ],
                            )
                        )
                    )
                ]
            )
        ],
        padding=0,
        horizontal_alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


divider = ft.Divider(height=1, color=ft.Colors.GREY_300, thickness=1)
