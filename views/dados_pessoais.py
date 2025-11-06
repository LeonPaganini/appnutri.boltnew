import flet as ft
import asyncio
import logging
from app.themes.tema import AppTheme
from app.components.progress import progress_bar2
from app.components.icons import ICONSS
from app.components.layout import pagina_base_responsivo, configure_page
from app.components.buttons import back_button
from app.components.fields import create_text_field
from app.components.loading import show_loading, hide_loading

def main(page: ft.Page, respostas: dict, auto_advance=True):
    hide_loading(page)
    configure_page(page)
    current_page = 1
    pb, update_progress = progress_bar2(page, current_page)
    back_btn = back_button(page, "/", current_page, update_progress)

    # ------ TextFields ------
    nome = create_text_field("Nome", AppTheme.get_color("SECONDARY_COLOR"), AppTheme.get_color("FIELD_BG_COLOR"), page=page, cache_key="nome", keyboard_type=ft.KeyboardType.TEXT)
    idade = create_text_field("Idade", AppTheme.get_color("SECONDARY_COLOR"), AppTheme.get_color("FIELD_BG_COLOR"), page=page, cache_key="idade", keyboard_type=ft.KeyboardType.NUMBER)
    altura = create_text_field("Altura (cm)", AppTheme.get_color("SECONDARY_COLOR"), AppTheme.get_color("FIELD_BG_COLOR"), page=page, cache_key="altura", keyboard_type=ft.KeyboardType.NUMBER)
    peso_atual = create_text_field("Peso Atual (kg)", AppTheme.get_color("SECONDARY_COLOR"), AppTheme.get_color("FIELD_BG_COLOR"), page=page, cache_key="peso_atual", keyboard_type=ft.KeyboardType.NUMBER)
    peso_desejado = create_text_field("Peso Desejado (kg)", AppTheme.get_color("SECONDARY_COLOR"), AppTheme.get_color("FIELD_BG_COLOR"), page=page, cache_key="peso_desejado", keyboard_type=ft.KeyboardType.NUMBER)

    # --- Feedback/erro ---
    feedback_erro = ft.Container(
        content=ft.Text(
            "A seleção do gênero é necessária para os cálculos do plano.",
            size=10,
            color=AppTheme.get_color("WARNING_TEXT_COLOR"),
            text_align=ft.TextAlign.CENTER,
            visible=False
        ),
        padding=ft.padding.only(top=8, bottom=2),
        alignment=ft.alignment.center,
        visible=False,
    )

    def validar_e_avancar(genero):
        # Mesma validação do botão anterior
        nome_val = nome.content.value.strip()
        idade_val = idade.content.value.strip()
        altura_val = altura.content.value.strip()
        peso_val = peso_atual.content.value.strip()
        peso_desejado_val = peso_desejado.content.value.strip()

        try:
            if (len(nome_val) < 2 or any(char.isdigit() for char in nome_val)):
                return False
            if not idade_val.isdigit() or not (10 <= int(idade_val) <= 100):
                return False
            if not altura_val.isdigit() or not (100 <= int(altura_val) <= 250):
                return False
            peso_float = float(peso_val.replace(",", "."))
            if not (30 <= peso_float <= 300):
                return False
            peso_desejado_float = float(peso_desejado_val.replace(",", "."))
            if not (30 <= peso_desejado_float <= 300):
                return False
        except:
            return False
        # Salva as respostas e avança!
        respostas["nome"] = nome.content.value
        respostas["idade"] = idade.content.value
        respostas["altura"] = altura.content.value
        respostas["peso_atual"] = peso_atual.content.value
        respostas["peso_desejado"] = peso_desejado.content.value
        respostas["sexo"] = genero
        
        async def next_page():
            show_loading(page, "Carregando...")
            await asyncio.sleep(0.5)
            hide_loading(page)
            page.go("/imc_usuario")
        page.run_task(next_page)
        return True

    def criar_chips_genero():
        chip_masculino = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.MALE, color="#383838", size=22),
                    ft.Text("Masculino", color="#383838", size=18),  # Ajuste de size
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor="#b3ddb1",
            border_radius=12,
            padding=ft.padding.symmetric(vertical=12, horizontal=10),  # Mais espaço vertical!
            expand=1,
            width=None,
            height=60,  # Ajuste de altura
            alignment=ft.alignment.center,
            on_click=lambda e: validar_e_avancar("masculino"),
        )
        chip_feminino = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.FEMALE, color="#383838", size=22),
                    ft.Text("Feminino", color="#383838", size=18),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor="#ffac88",
            border_radius=12,
            padding=ft.padding.symmetric(vertical=12, horizontal=10),
            expand=1,
            width=None,
            height=60,
            alignment=ft.alignment.center,
            on_click=lambda e: validar_e_avancar("feminino"),
        )
        return chip_masculino, chip_feminino

    chip_masc, chip_fem = criar_chips_genero()
    chips_row = ft.Row(
        [chip_masc, chip_fem],
        spacing=16,
        alignment=ft.MainAxisAlignment.CENTER
    )

    genero_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Text(
                        "Selecione seu Gênero",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    padding=2,
                ),
                ft.Container(content=ft.Divider(height=2, thickness=1), padding=ft.padding.only(bottom=2)),
                chips_row,
                ft.Container(
                    content=ft.Text(
                        "A seleção do gênero é necessária para os cálculos do plano alimentar.",
                        size=10,
                        color=AppTheme.get_color("WARNING_TEXT_COLOR"),
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=6,
                    alignment=ft.alignment.center,
                ),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        padding=ft.padding.all(2),
    )

    # ------ Montagem final ------
    conteudo = [
        ft.Container(content=nome),
        ft.Container(content=idade),
        ft.Container(content=altura),
        ft.Container(content=peso_atual),
        ft.Container(content=peso_desejado),
        genero_container
        # Botão REMOVIDO
    ]

    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/",
            titulo="Dados Pessoais",
            progresso=pb,
            back_btn=back_btn,
            conteudo=conteudo,
        )
    )

    page.update()
