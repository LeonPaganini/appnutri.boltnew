import flet as ft
from app.themes.tema import AppTheme
from app.components.icons import ICONSS
from app.components.progress import progress_bar2
from app.components.layout import *
from app.components.buttons import back_button_conditional, create_continue_button
from app.components.visibility import *
from app.components.chips import criar_chip_padrao2
from app.components.fields import create_text_field
import time
from app.components.loading import show_loading, hide_loading  # NOVO
import asyncio

def main(page: ft.Page, respostas: dict, auto_advance=True):
    hide_loading(page)
    configure_page(page)

    current_page = 3  # Página inicial
    pb, update_progress = progress_bar2(page, current_page)

    def ir_para_exercicios():
        async def next_page():
            show_loading(page, "Carregando...")
            await asyncio.sleep(0.5)
            hide_loading(page)
            page.go("/exercicios")
        page.run_task(next_page)

    def botao_continuar_click(e):
        page.go("/exercicios")

    botao_continuar = create_continue_button(
        text="Pular",
        on_click=botao_continuar_click,
        is_valid=lambda: True
    )
    visibilidade(page, botao_continuar, False)  # Esconde inicialmente

    def registrar_historico_saude(e, hist_saude):
        respostas["Histórico de Saúde"] = hist_saude
        page_history.append({
            historico_saude: True,
            historico_saude_opcoes: True,
            patologia: False,
            historico_medicacao: False,
            historico_medicacao_opcoes: False,
            pergunta_qualidade_sono: False,
            qualidade_sono: False,
            pergunta_horas_sono: False,
            horas_sono_container: False
        })
        if hist_saude == "Sim":
            visibilidade(page, patologia, True)
        elif hist_saude == "Não":
            visibilidade(page, patologia, False)
            visibilidade(page, historico_medicacao, True)
            visibilidade(page, historico_medicacao_opcoes, True)

    # 🔥 NOVO callback para botão "✓" da patologia
    def on_patologia_button(e, campo):
        if len(campo.value) >= 3:
            respostas["Patologia"] = campo.value
            visibilidade(page, historico_medicacao, True)
            visibilidade(page, historico_medicacao_opcoes, True)
            page.update()

    # 🔥 NOVO callback para botão "✓" de medicamentos
    def on_medicamentos_button(e, campo):
        if len(campo.value) >= 3:
            respostas["Medicação"] = campo.value
            visibilidade(page, pergunta_qualidade_sono, True)
            visibilidade(page, qualidade_sono, True)
            visibilidade(page, historico_saude, False)
            visibilidade(page, historico_saude_opcoes, False)
            visibilidade(page, patologia, False)
            visibilidade(page, historico_medicacao, False)
            visibilidade(page, historico_medicacao_opcoes, False)
            visibilidade(page, medicamentos, False)
            page.update()

    # Funções on_blur antigas — não serão mais usadas
    # def verificar_patologia(e):
    #     ...
    # def verificar_medicacao(e):
    #     ...

    def registrar_medicacao(e, hist_medicamento):
        respostas["Histórico de Medicamentos"] = hist_medicamento
        page_history.append({
            historico_saude: True,
            historico_saude_opcoes: True,
            patologia: True,
            historico_medicacao: True,
            historico_medicacao_opcoes: True,
            medicamentos: True,
            pergunta_qualidade_sono: False,
            qualidade_sono: False,
            pergunta_horas_sono: False,
            horas_sono_container: False
        })
        if hist_medicamento == "Sim":
            visibilidade(page, medicamentos, True)
            visibilidade(page, botao_continuar, True)
        elif hist_medicamento == "Não":
            visibilidade(page, pergunta_qualidade_sono, True)
            visibilidade(page, qualidade_sono, True)
            visibilidade(page, historico_saude, False)
            visibilidade(page, historico_saude_opcoes, False)
            visibilidade(page, patologia, False)
            visibilidade(page, historico_medicacao, False)
            visibilidade(page, historico_medicacao_opcoes, False)
            visibilidade(page, medicamentos, False)
            visibilidade(page, patologia, False)

    def selecionar_classificacao_sono(e, classificacao):
        respostas["Qualidade Sono"] = classificacao
        page_history.append({
            historico_saude: False,
            historico_saude_opcoes: False,
            patologia: False,
            historico_medicacao: False,
            historico_medicacao_opcoes: False,
            pergunta_qualidade_sono: True,
            qualidade_sono: True,
            pergunta_horas_sono: False,
            horas_sono_container: False
        })
        visibilidade(page, pergunta_horas_sono, True)
        visibilidade(page, horas_sono_container, True)
        visibilidade(page, pergunta_qualidade_sono, False)
        visibilidade(page, qualidade_sono, False)

    def selecionar_horas_sono(e, horas_sono):
        respostas["horas sono"] = horas_sono
        page_history.append({
            historico_saude: False,
            historico_saude_opcoes: False,
            patologia: False,
            historico_medicacao: False,
            historico_medicacao_opcoes: False,
            pergunta_qualidade_sono: True,
            qualidade_sono: True,
            pergunta_horas_sono: True,
            horas_sono_container: True
        })
        visibilidade(page, pergunta_horas_sono, True)
        visibilidade(page, horas_sono_container, True)
        page.update()
        ir_para_exercicios()

    ### VARIÁVEIS ###

    patologia = create_text_field(
        "Se sim, qual?",
        AppTheme.get_color("SECONDARY_COLOR"),
        AppTheme.get_color("FIELD_BG_COLOR"),
        alignment=ft.alignment.center,
        cache_key="patologia",
        with_button=True,
        on_button_click=on_patologia_button,
        width=200
    )

    medicamentos = create_text_field(
        "Se sim, qual?",
        AppTheme.get_color("SECONDARY_COLOR"),
        AppTheme.get_color("FIELD_BG_COLOR"),
        alignment=ft.alignment.center,
        cache_key="medicamentos",
        with_button=True,
        on_button_click=on_medicamentos_button,
        width=200
    )

    historico_saude = ft.Container(
        content=ft.Text("Possui alguma condição de saúde diagnosticada?", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        alignment=ft.alignment.center,
        padding=ft.padding.all(2)
    )

    historico_medicacao = ft.Container(
        content=ft.Text("Está tomando alguma medicação atualmente?", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        alignment=ft.alignment.center,
        padding=ft.padding.all(2)
    )

    pergunta_qualidade_sono = ft.Container(
        content=ft.Text("Como você avalia a qualidade do seu sono?", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        alignment=ft.alignment.center,
        padding=ft.padding.all(2)
    )

    pergunta_horas_sono = ft.Container(
        content=ft.Text("Quantas horas costuma dormir por noite?", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        alignment=ft.alignment.center,
        padding=ft.padding.all(2)
    )

    page_history = []

    selecao_sim_nao = [("Sim", None, "Sim", ft.Icons.WATER_DROP_OUTLINED, 1), ("Não", None, "Não", ft.Icons.WATER_DROP_OUTLINED, 1)]

    def criar_botoes_sim_nao(niveis, on_select):
        grupo = []
        botoes = []
        for i, (nivel, descricao, valor, icone, quantidade_icones) in enumerate(niveis):
            chip = criar_chip_padrao2(
                texto=nivel,
                descricao=descricao or "",
                valor=valor,
                on_select=on_select,
                grupo=grupo,
                selecionar_unico=True,
                icone=None,
                quantidade_icones=0,
                chip_padding=ft.padding.symmetric(vertical=8, horizontal=2),
                layout_em_coluna=False
            )
            container = ft.Container(
                content=chip,
                expand=1,
                padding=ft.padding.only(right=5 if i == 0 else 0, left=5 if i == 1 else 0)
            )
            botoes.append(container)
        return botoes

    historico_saude_opcoes = ft.Container(
        content=ft.Row(
            controls=criar_botoes_sim_nao(selecao_sim_nao, registrar_historico_saude),
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(horizontal=10),
        width=280
    )

    historico_medicacao_opcoes = ft.Container(
        content=ft.Row(
            controls=criar_botoes_sim_nao(selecao_sim_nao, registrar_medicacao),
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(horizontal=10),
        width=280
    )

    classificacao_sono = [
        ("Ótimo", "Tenho noites de sono reparadoras", "Ótimo", ICONSS['sono_otimo'], 1),
        ("Bom", "Durmo rápido e ininterruptamente", "Bom", ICONSS['sono_bom'], 1),
        ("Regular", "Acordo regularmente a noite", "Regular", ICONSS['sono_regular'], 1),
        ("Ruim", "Acordo frequentemente a noite", "Ruim", ICONSS['sono_ruim'], 1),
    ]
    horas_sono = [
        ("Mais de OITO", "Acorda Cinderela! Vamos treinar!", "Mais de 8 Horas", ICONSS['sono_otimo'], 1),
        ("CINCO a OITO", "Este é um ótimo período de sono", "5 a 8 Horas", ICONSS['sono_bom'], 1),
        ("Menos de CINCO", "Você dorme muito pouco", "Menos de 5 Horas", ICONSS['sono_ruim'], 1),
    ]

    def criar_botoes_sono(niveis, on_select):
        grupo = []
        botoes = []
        for nivel, descricao, valor, url_icone, quantidade_icones in niveis:
            chip = criar_chip_padrao2(
                texto=nivel,
                descricao=descricao,
                valor=valor,
                on_select=on_select,
                grupo=grupo,
                selecionar_unico=True,
                icone=url_icone,
                tipo_icone="imagem",
                quantidade_icones=quantidade_icones,
                chip_width=50,
                icon_size=45,
                chip_padding=ft.padding.symmetric(vertical=8, horizontal=2),
                show_checkmark=False
            )
            botoes.append(chip)
            botoes.append(ft.Container(height=4))
        return botoes

    qualidade_sono = ft.Container(
        content=ft.Column(
            controls=criar_botoes_sono(classificacao_sono, selecionar_classificacao_sono),
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(8),
        width=370,
    )

    horas_sono_container = ft.Container(
        content=ft.Column(
            controls=criar_botoes_sono(horas_sono, selecionar_horas_sono),
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(8),
        width=370,
    )

    elementos_invisiveis = [patologia, medicamentos, historico_medicacao, historico_medicacao_opcoes, pergunta_qualidade_sono,
                            qualidade_sono, horas_sono_container, pergunta_horas_sono]

    for var in elementos_invisiveis:
        visibilidade(page, var, False)

    back_btn_conditional = back_button_conditional(page, "/imc_usuario", historico_saude, historico_saude_opcoes, page_history, current_page, update_progress)

    conteudo = [
        historico_saude,
        historico_saude_opcoes,
        patologia,
        historico_medicacao,
        historico_medicacao_opcoes,
        medicamentos,
        pergunta_qualidade_sono,
        qualidade_sono,
        pergunta_horas_sono,
        horas_sono_container,
    ]

    conteudo.append(ft.Container(content=botao_continuar, alignment=ft.alignment.bottom_center, padding=20))

    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/saude_sono",
            titulo="Saúde e Sono",
            progresso=pb,
            back_btn=back_btn_conditional,
            conteudo=conteudo
        )
    )
    page.update()