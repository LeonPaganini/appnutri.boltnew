import flet as ft
from app.themes.tema import AppTheme
from app.components.icons import ICONSS
from app.components.progress import progress_bar2
from app.components.layout import configure_page, pagina_base_responsivo
from app.components.buttons import back_button_conditional, create_continue_button
from app.components.visibility import visibilidade
from app.components.chips import criar_chip_padrao2
from app.components.loading import show_loading, hide_loading  # NOVO
import asyncio


def main(page: ft.Page, respostas: dict, auto_advance=True):
    configure_page(page)

    current_page = 4
    pb, update_progress = progress_bar2(page, current_page)
    update_progress(current_page)

    page_history = []

    sub_titulo = ft.Container(
        content=ft.Text("Selecione seu nível de atividade", size=14),
        alignment=ft.alignment.center,
        padding=ft.padding.all(2)
    )
    visibilidade(page, sub_titulo, False)

    # ---------- Dropdowns ----------
    atividades_fisicas = [
        "Não se Aplica", "Caminhada", "Corrida", "Ciclismo", "Natação",
        "Yoga", "Pilates", "Musculação", "Dança", "Lutas", "Crossfit", "Outros"
    ]

    def criar_dropdown(on_change):
        return ft.Dropdown(
            hint_text="Atividade Física",
            options=[ft.dropdown.Option(atividade) for atividade in atividades_fisicas],
            on_change=on_change,
            width=330,
            height=50,
            text_size=14,
            bgcolor=AppTheme.get_color("BACKGROUND_COLOR"),
            border=ft.border.all(1, AppTheme.get_color("SECONDARY_COLOR")),
            focus_color=AppTheme.get_color("SECONDARY_COLOR"),
            border_radius=6,
            alignment=ft.alignment.center,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=4),
            max_menu_height=400
        )

    # ---------- Funções Registro ----------
    def registrar_atividade(e):
        respostas["Atividade Física 1"] = e.control.value
        atualizar_botao_continuar()

    def registrar_atividade2(e):
        respostas["Atividade Física 2"] = e.control.value
        atualizar_botao_continuar()

    def formatar_tempo(valor):
        horas = int(valor // 6)
        minutos = int((valor % 6) * 10)
        return f"{horas}h {minutos}min" if minutos > 0 else f"{horas}h"

    def registrar_tempo(e, chave):
        tempo = formatar_tempo(e.control.value)
        e.control.label = tempo
        e.control.update()
        respostas[chave] = tempo
        atualizar_botao_continuar()

    def ir_para_consumo_agua():
        async def next_page():
            show_loading(page, "Carregando...")
            await asyncio.sleep(0.5)
            hide_loading(page)
            page.go("/agua_alimentacao")
        page.run_task(next_page)

    # ---------- Containers Atividades ----------
    atividade_fisica_container = ft.Container(
        content=ft.Column([
            ft.Text("Selecione sua principal atividade física:", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            criar_dropdown(registrar_atividade)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        alignment=ft.alignment.center, padding=4, width=350
    )
    visibilidade(page, atividade_fisica_container, True)

    atividade_secundaria_container = ft.Container(
        content=ft.Column([
            ft.Text("Selecione sua segunda atividade física:", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            criar_dropdown(registrar_atividade2)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        alignment=ft.alignment.center, padding=4, width=350
    )
    visibilidade(page, atividade_secundaria_container, True)

    # ---------- Sliders ----------
    def criar_slider(on_change):
        return ft.Slider(
            min=0, max=60, divisions=60, label="0h", on_change=on_change,
            width=300, height=40, active_color=AppTheme.get_color("AMARELO_COLOR")
        )

    tempo_atividade_container = ft.Container(
        content=ft.Column([
            ft.Text("Selecione o TEMPO da atividade física:", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            criar_slider(lambda e: registrar_tempo(e, "Tempo de Atividade"))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        alignment=ft.alignment.center, padding=4, width=350
    )
    visibilidade(page, tempo_atividade_container, True)

    tempo_atividade2_container = ft.Container(
        content=ft.Column([
            ft.Text("Selecione o TEMPO da segunda atividade física:", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            criar_slider(lambda e: registrar_tempo(e, "Tempo de Atividade 2"))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        alignment=ft.alignment.center, padding=4, width=350
    )
    visibilidade(page, tempo_atividade2_container, True)

    # ---------- Chips Nível Atividade ----------
    niveis_atividade = [
        ("Sedentário", "Pouco ou nenhum exercício", 1.2, ICONSS['sedentario']),
        ("Pouco ativo", "Exercício leve 1-3 dias/semana", 1.375, ICONSS['pouco_ativo']),
        ("Moderadamente ativo", "Exercício moderado 3-5 dias/semana", 1.55, ICONSS['moderad_ativo']),
        ("Muito ativo", "Exercício pesado 6-7 dias/semana", 1.725, ICONSS['muito_ativo']),
        ("Extremamente ativo", "Exercício extremo 2x ao dia e trabalho intenso", 1.9, ICONSS['extrem_ativo']),
    ]

    def registrar_nivel(e, valor):
        respostas["Nível de Atividade"] = valor
        atualizar_botao_continuar()

    def criar_chips_nivel():
        grupo = []
        chips = []
        for nivel, descricao, valor, img in niveis_atividade:
            chips.append(
                criar_chip_padrao2(
                    texto=nivel, descricao=descricao, valor=valor,
                    on_select=lambda e, v=valor: registrar_nivel(e, v),
                    grupo=grupo, selecionar_unico=True,
                    icone=img, tipo_icone="imagem", quantidade_icones=1,
                    chip_width=50, layout_em_coluna=False,icon_size=45,
                    chip_padding=ft.padding.symmetric(vertical=4, horizontal=8)
                )
            )
            chips.append(ft.Container(height=2))
        return chips

    niveis_atividade_container = ft.Container(
        content=ft.Column(
            controls=criar_chips_nivel(),
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4
        ),
        alignment=ft.alignment.center, padding=4, width=360
    )
    visibilidade(page, niveis_atividade_container, False)

    # ---------- Controle de Etapas ----------
    etapa_1_concluida = False

    def atualizar_botao_continuar():
        atividade1 = respostas.get("Atividade Física 1")
        atividade2 = respostas.get("Atividade Física 2")
        tempo1 = respostas.get("Tempo de Atividade")
        tempo2 = respostas.get("Tempo de Atividade 2")
        nivel = respostas.get("Nível de Atividade")

        if not etapa_1_concluida:
            ok1 = atividade1 and (atividade1 == "Não se Aplica" or tempo1)
            ok2 = atividade2 and (atividade2 == "Não se Aplica" or tempo2)
            completo = ok1 and ok2
        else:
            completo = nivel is not None

        botao_continuar.disabled = not completo
        botao_continuar.bgcolor = (
            AppTheme.get_color("BUTTON_BG_COLOR")
            if completo else AppTheme.get_color("BUTTON_BG_COLOR_DISABLED")
        )
        botao_continuar.color = ft.colors.WHITE
        page.update()

    # ---------- Botão Continuar ----------
    def continuar(e):
        nonlocal etapa_1_concluida

        if not etapa_1_concluida:
            atividade1 = respostas.get("Atividade Física 1")
            tempo1 = respostas.get("Tempo de Atividade")
            atividade2 = respostas.get("Atividade Física 2")
            tempo2 = respostas.get("Tempo de Atividade 2")

            if not atividade1:
                page.snack_bar = ft.SnackBar(content=ft.Text("Selecione sua atividade física principal."), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            if atividade1 != "Não se Aplica" and not tempo1:
                page.snack_bar = ft.SnackBar(content=ft.Text("Informe o tempo da atividade física principal."), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            if not atividade2:
                page.snack_bar = ft.SnackBar(content=ft.Text("Selecione sua segunda atividade física."), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            if atividade2 != "Não se Aplica" and not tempo2:
                page.snack_bar = ft.SnackBar(content=ft.Text("Informe o tempo da segunda atividade física."), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            etapa_1_concluida = True

            visibilidade(page, atividade_fisica_container, False)
            visibilidade(page, tempo_atividade_container, False)
            visibilidade(page, atividade_secundaria_container, False)
            visibilidade(page, tempo_atividade2_container, False)
            visibilidade(page, sub_titulo, True)
            visibilidade(page, niveis_atividade_container, True)

            page.update()
            atualizar_botao_continuar()
        else:
            if not respostas.get("Nível de Atividade"):
                page.snack_bar = ft.SnackBar(content=ft.Text("Por favor, selecione seu nível de atividade."), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            ir_para_consumo_agua()

    def is_valid():
        if not etapa_1_concluida:
            a1 = respostas.get("Atividade Física 1")
            t1 = respostas.get("Tempo de Atividade")
            a2 = respostas.get("Atividade Física 2")
            t2 = respostas.get("Tempo de Atividade 2")

            t1_ok = (a1 == "Não se Aplica") or t1
            t2_ok = (a2 == "Não se Aplica") or t2

            return bool(a1 and a2 and t1_ok and t2_ok)
        else:
            return respostas.get("Nível de Atividade") is not None

    botao_continuar = create_continue_button("Continuar", is_valid, continuar)

    back_btn = back_button_conditional(
        page, "/saude_sono",
        atividade_fisica_container, tempo_atividade_container,
        page_history, current_page, update_progress
    )

    # ---------- Conteúdo Principal ----------
    conteudo = [
        sub_titulo,
        atividade_fisica_container,
        tempo_atividade_container,
        atividade_secundaria_container,
        tempo_atividade2_container,
        niveis_atividade_container,
    ]

    # ---------- View ----------
    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/exercicios",
            titulo="Nível de Atividade",
            conteudo=conteudo,
            progresso=pb,
            back_btn=back_btn,
            exibir_botao_continuar=True,
            botao_continuar=botao_continuar
        )
    )
    page.update()
