import flet as ft
from app.themes.tema import AppTheme
from app.components.icons import ICONSS
from app.components.progress import progress_bar2
from app.components.layout import pagina_base_responsivo, configure_page, divider
from app.components.buttons import back_button, create_continue_button
from app.components.chips import criar_chip_padrao2
from app.components.fields import create_text_field
from app.components.dialog_refeicoes import criar_dialog_padrao
from app.components.loading import show_loading, hide_loading  # NOVO
import asyncio


def main(page: ft.Page, respostas: dict, auto_advance=True):
    hide_loading(page)
    configure_page(page)
    current_page = 6
    pb, update_progress = progress_bar2(page, current_page)
    back_btn = back_button(page, "/agua_alimentacao", current_page, update_progress)

    refeicoes_selecionadas = {"valor": None}

    def ir_para_preferencias_alimentares():
        async def next_page():
            show_loading(page, "Carregando...")
            await asyncio.sleep(0.5)
            hide_loading(page)
            page.go("/preferencias_alimentares")
        page.run_task(next_page)

    def is_valid():
        return refeicoes_selecionadas["valor"] is not None and all(
            respostas.get(f"Refeição {i}") for i in range(1, refeicoes_selecionadas["valor"] + 1)
        )

    def criar_campos_refeicoes(qtd_refeicoes):
        campos, erros = [], []

        def criar_campo(hint_text):
            erro = ft.Text("", color=ft.colors.RED, size=10, text_align=ft.TextAlign.CENTER)
            campo_container = create_text_field(
                label="",
                border_color=AppTheme.get_color("SECONDARY_COLOR"),
                fill_color=AppTheme.get_color("TEXT_FIELD_COLOR"),
                page=page,
                keyboard_type=ft.KeyboardType.NUMBER,
                alignment=ft.alignment.center
            )
            tf = campo_container.content
            tf.hint_text = hint_text
            tf.height = 38
            tf.max_length = 2
            tf.text_align = ft.TextAlign.CENTER
            return tf, erro

        for i in range(1, qtd_refeicoes + 1):
            chave = f"Refeição {i}"
            h, h_error = criar_campo("12")
            m, m_error = criar_campo("00")

            if chave in respostas:
                h.value = respostas[chave].get("horas", "")
                m.value = respostas[chave].get("minutos", "")

            campos.append((h, m))
            erros.append((h_error, m_error))

        for idx, (h, m) in enumerate(campos):
            def ao_digitar_horas(e, i=idx):
                if len(e.control.value) == 2:
                    campos[i][1].focus()

            def ao_digitar_minutos(e, i=idx):
                if len(e.control.value) == 2 and i + 1 < len(campos):
                    campos[i + 1][0].focus()

            h.on_change = ao_digitar_horas
            m.on_change = ao_digitar_minutos

        return campos, erros

    def registrar_qtd_refeicoes(e, qtd):
        respostas["Refeições Diárias"] = f"{qtd} Refeições"
        refeicoes_selecionadas["valor"] = qtd

        campos, erros = criar_campos_refeicoes(qtd)

        elementos = []
        for i in range(len(campos)):
            linha = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(f"Refeição {i+1}", size=12),
                        width=70,
                        alignment=ft.alignment.center_left
                    ),
                    ft.Container(content=campos[i][0], expand=True),
                    ft.Container(content=campos[i][1], expand=True)
                ],
                spacing=2,
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER
            )

            linha_erros = ft.Row(
                controls=[erros[i][0], erros[i][1]],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )

            elementos.append(
                ft.Column(
                    controls=[linha, linha_erros],
                    spacing=2
                )
            )

        def atualizar_estado_botao():
            botao_continuar.disabled = not is_valid()
            botao_continuar.bgcolor = (
                AppTheme.get_color("BUTTON_BG_COLOR")
                if not botao_continuar.disabled
                else AppTheme.get_color("BUTTON_BG_COLOR_DISABLED")
            )
            page.update()

        def confirmar_horarios(e):
            has_error = False
            for idx, (h, m) in enumerate(campos):
                h_val, m_val = h.value.strip(), m.value.strip()
                erros[idx][0].value = erros[idx][1].value = ""
                h.border_color = m.border_color = AppTheme.get_color("SECONDARY_COLOR")

                if not h_val.isdigit() or not (0 <= int(h_val) <= 23):
                    erros[idx][0].value = "0–23"
                    h.border_color = ft.colors.RED
                    has_error = True
                if not m_val.isdigit() or not (0 <= int(m_val) <= 59):
                    erros[idx][1].value = "0–59"
                    m.border_color = ft.colors.RED
                    has_error = True

            if has_error:
                page.update()
                return

            for idx, (h, m) in enumerate(campos, start=1):
                respostas[f"Refeição {idx}"] = {"horas": h.value, "minutos": m.value}

            atualizar_estado_botao()
            dialog.open = False
            page.update()

        dialog = criar_dialog_padrao(
            page=page,
            titulo="Horários das Refeições",
            elementos_conteudo=elementos,
            on_confirm=confirmar_horarios
        )

        page.dialog = dialog
        dialog.open = True
        page.update()

    # Chips
    imagem_url = ICONSS["refeicao"]
    grupo_chips = []
    chips = []
    for qtd in range(2, 7):
        chip = criar_chip_padrao2(
            texto=f"{qtd} Refeições",
            descricao=f"{qtd} refeições ao longo do dia",
            valor=qtd,
            icone=imagem_url,
            tipo_icone="imagem",
            quantidade_icones=1,
            on_select=registrar_qtd_refeicoes,
            grupo=grupo_chips,
            selecionar_unico=True,
            chip_width=50,
            icon_size=45
        )
        chips.append(chip)

    qtd_refeicoes_container = ft.Container(
        content=ft.Column(controls=chips, alignment=ft.MainAxisAlignment.CENTER, spacing=14),
        alignment=ft.alignment.center,
        padding=10,
        width=370
    )

    def avancar(e):
        ir_para_preferencias_alimentares()

    botao_continuar = create_continue_button("Continuar", is_valid, avancar)

    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/habitos_alimentares",
            titulo="Quantidade de Refeições",
            conteudo=[qtd_refeicoes_container],
            progresso=pb,
            back_btn=back_btn,
            exibir_botao_continuar=True,
            botao_continuar=botao_continuar
        )
    )

    page.update()
