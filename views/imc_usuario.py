import flet as ft
from app.themes.tema import AppTheme
from app.components.icons import ICONSS
from app.components.progress import progress_bar2
from app.components.layout import *
from app.components.buttons import back_button
from app.components.chips import criar_chip_padrao2
from app.nutri.imc import *
from app.components.loading import show_loading, hide_loading  # NOVO
import asyncio




def main(page: ft.Page, respostas: dict, auto_advance=True):
    configure_page(page)
    hide_loading(page)

    

    current_page = 2
    pb, update_progress = progress_bar2(page, current_page)
    back_btn = back_button(page, "/dados_pessoais", current_page, update_progress)

    # --- Cálculo do IMC ---
    altura = float(respostas.get("altura", 0)) / 100
    peso_atual = float(respostas.get("peso_atual", "0").replace(",", "."))
    # peso_atual = float(respostas.get("peso_atual", 0))
    imc = round(peso_atual / (altura ** 2), 1) if altura > 0 else 0
    imc_condicao = determinar_categoria(imc)

    respostas["imc"] = imc
    respostas["imc_condicao"] = imc_condicao

    categoria = determinar_categoria(imc)
    cor_imc = imc_colors.get(categoria, ft.Colors.GREY)
    frase_motivacional_texto = frases_motivacionais.get(categoria, "")

    resultado_imc_text = ft.Text(f"{imc} - {imc_condicao}", size=20, weight=ft.FontWeight.BOLD, color=cor_imc, visible=False)
    carregando_text = ft.Text("Carregando", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY, visible=True)
    frase_motivacional = ft.Text(frase_motivacional_texto, size=12, color=AppTheme.get_color("AMARELO_COLOR"),text_align= ft.TextAlign.CENTER, visible=False)


    def ir_para_saude_sono():
        async def next_page():
            show_loading(page, "Carregando...")
            await asyncio.sleep(0.5)
            hide_loading(page)
            await asyncio.sleep(0.1)  # <-- Importante!
            page.go("/saude_sono")
        page.run_task(next_page)

    # --- Seção de Objetivo ---
    objetivo_selecionado = ""

    def selecionar_objetivo(e, objetivo):
        nonlocal objetivo_selecionado
        objetivo_selecionado = objetivo
        respostas["objetivo"] = objetivo_selecionado
        page.update()
        ir_para_saude_sono()


    objetivos_info_chip = [
        ("Perder Peso", "Meu desejo é perder peso", "Perder Peso", ICONSS["perder_peso"], 1),
        ("Manter Peso", "Desejo manter meu peso atual", "Manter Peso", ICONSS["manter_peso"], 1),
        ("Ganhar Peso", "Meu desejo é ganhar peso", "Ganhar Peso", ICONSS["ganhar_peso"], 1),
    ]

    def criar_botoes_objetivo(niveis, on_select):
        grupo = []  # Lista de controle de seleção única
        chips = []

        def selecionar_chip(e, valor):
            on_select(e, valor)

        for nivel, descricao, valor, imagem_url, quantidade_imagens in niveis:
            chip = criar_chip_padrao2(
                texto=nivel,
                descricao=descricao,
                valor=valor,
                on_select=selecionar_chip,
                grupo=grupo,
                selecionar_unico=True,
                icone=imagem_url,  # Ícone do tipo imagem
                tipo_icone="imagem",
                quantidade_icones=quantidade_imagens,
                chip_width=50,
                icon_size=45,
                chip_padding=ft.padding.symmetric(vertical=8, horizontal=2),
                layout_em_coluna=False  # Para manter o layout em linha
            )
            chips.append(chip)
            chips.append(ft.Container(height=2))  # Espaçamento entre os chips

        return chips

    # --- Container com os chips de objetivo ---
    objetivo_usuario_container = ft.Container(
        content=ft.Column(
            controls=criar_botoes_objetivo(objetivos_info_chip, selecionar_objetivo),
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(8),
        width=370,
    )



    # --- Conteúdo central da página ---

    # --- Container com o texto de carregamento e resultado do IMC ---
    container_resultado_imc = ft.Container(
        content=ft.Column(
            controls=[
                carregando_text,
                resultado_imc_text,
                criar_barra(imc, resultado_imc_text, carregando_text, page, frase_motivacional),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
    )

    # --- Container com a frase motivacional ---
    container_frase_motivacional = ft.Container(
        content=frase_motivacional,
        alignment=ft.alignment.center,
        padding=ft.padding.all(2),
    )

    # --- Divisor entre seções ---
    divisor_intermediario = ft.Divider(height=1, color=ft.Colors.GREY_300, thickness=1)

    # --- Container com o título da seção de objetivo ---
    container_titulo_objetivo = ft.Container(
        content=ft.Text("Selecione seu Objetivo", size=20, weight=ft.FontWeight.BOLD),
        alignment=ft.alignment.center,
    )

    # --- Container com a descrição da seção de objetivo ---
    container_descricao_objetivo = ft.Container(
        content=ft.Text(
            "Por favor, escolha um objetivo para continuar.",
            size=12,
            weight=ft.FontWeight.NORMAL,
            color=AppTheme.get_color("AMARELO_COLOR"),
            text_align=ft.TextAlign.CENTER,
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(1),
    )

    # --- Divisor inferior ---
    divisor_inferior = ft.Divider(height=1, color=ft.Colors.GREY_300, thickness=1)


    # --- Conteúdo central da página ---
    conteudo = [

        container_resultado_imc,
        container_frase_motivacional,
        divisor_intermediario,
        container_titulo_objetivo,
        container_descricao_objetivo,
        divisor_inferior,
        objetivo_usuario_container,
    ]

    

    # --- Aplicar layout padronizado ---
    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/imc_usuario",
            titulo="Seu IMC é:",
            progresso=pb,
            back_btn=back_btn,
            conteudo=conteudo
        )
    )
    page.update()
