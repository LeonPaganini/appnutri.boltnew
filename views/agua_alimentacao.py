import flet as ft
from app.themes.tema import AppTheme
from app.components.progress import progress_bar2
from app.components.icons import ICONSS
from app.components.layout import pagina_base_responsivo, configure_page
from app.components.buttons import back_button, create_continue_button
from app.components.chips import criar_chip_padrao2
from app.nutri.feedback import frases_feedback
from app.components.loading import show_loading, hide_loading  # NOVO
import asyncio

def main(page: ft.Page, respostas: dict, auto_advance=True):
    hide_loading(page)
    configure_page(page)
    current_page = 5
    pb, update_progress = progress_bar2(page, current_page)
    back_btn = back_button(page, "/exercicios", current_page, update_progress)

    # Feedback dinâmico
    txt_consumo_container = ft.Container(
        content=ft.Text("\n", size=12, color=AppTheme.AMARELO_COLOR, text_align=ft.TextAlign.CENTER),
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(vertical=4),
        visible=True
    )

    # Opções de consumo de água
    consumo_agua = [
        ("2 Copos", "Tenho dificuldade para beber água", "Consumo baixo de Água", ICONSS["agua_pouca"],1),
        ("2 a 6 Copos", "Bebo água com facilidade", "Consumo Moderado de Água", ICONSS["agua_moderado"],1),
        ("6 ou mais Copos", "Bebo água com MUITA facilidade", "Consumo ideal de Água", ICONSS["agua_otima"],1),
        ("Outras Bebidas", "Preferência por outras bebidas", "Consumo Ruim de Água", ICONSS["agua_nao"], 1),
    ]

    # Controle de seleção única
    grupo_chips = []

    def ir_para_habitos_alimentares():
        async def next_page():
            show_loading(page, "Carregando...")
            await asyncio.sleep(0.5)
            hide_loading(page)
            page.go("/habitos_alimentares")
        page.run_task(next_page)

    # Registrar resposta
    def registrar_consumo_agua(e, valor):
        respostas["Consumo de Água"] = valor
        txt_consumo_container.content.value = frases_feedback.get(valor, "")
        botao_continuar.update_state()
        page.update()

    # Criar chips padronizados
    def criar_botoes_consumo_agua(niveis, on_select):
        return [
            criar_chip_padrao2(
                texto=nivel,
                descricao=descricao,
                valor=valor,
                icone=imagem_url,  # Ícone do tipo imagem
                tipo_icone="imagem",
                quantidade_icones=quantidade_icones,
                on_select=on_select,
                grupo=grupo_chips,
                selecionar_unico=True,
                chip_width=50,
                icon_size=45,
                chip_padding=ft.padding.symmetric(vertical=10, horizontal=2),
                show_checkmark=False
            )
            for nivel, descricao, valor, imagem_url, quantidade_icones in niveis
        ]

    consumo_agua_container = ft.Container(
        content=ft.Column(
            controls=criar_botoes_consumo_agua(consumo_agua, registrar_consumo_agua),
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(10),
        width=360
    )

    # Validação
    def is_valid():
        return respostas.get("Consumo de Água") is not None

    def continuar(e):
        ir_para_habitos_alimentares()

    # Botão padronizado
    botao_continuar = create_continue_button("Continuar", is_valid, continuar)

    botao_continuar_container = ft.Container(
                                    content=botao_continuar,
                                    alignment=ft.alignment.center,
                                    padding=ft.padding.only(bottom=20)
                                )

    # Montagem final da view
    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/agua_alimentacao",
            titulo="Consumo diário de Água",
            progresso=pb,
            back_btn=back_btn,
            conteudo=[
                consumo_agua_container,
                txt_consumo_container,
                botao_continuar_container
            ],
        )
    )

    page.update()
