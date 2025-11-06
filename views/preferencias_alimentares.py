import flet as ft
import json
import asyncio
from app.themes.tema import AppTheme
from app.components.icons import ICONSS
from app.components.progress import progress_bar2
from app.components.layout import *
from app.components.buttons import back_button, create_continue_button
from app.components.visibility import *
from app.components.chips import criar_chip_padrao2
from urllib.parse import urlparse
import requests
from app.components.loading import show_loading, hide_loading

# ------------------------------------------------------------
# Config
# ------------------------------------------------------------
link_json = "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Falimentos_categorizados.json?alt=media&token=4a0abfdb-4ca5-43dd-b0d8-b1182fc9642a"
BACKEND_URL = "https://appnutri-8lyy.onrender.com"
# ===== Helpers de verificação da categoria =====
CATEGORIA_PARA_ID = {
    "Fontes de Proteínas": "1",
    "Lanches de Fontes de Proteínas": "2",
    "Fontes de Carboidratos": "3",
    "Lanches de Fontes de Carboidratos": "4",
    "Fontes de Gorduras": "5",
    "Vegetais": "6",
    "Frutas": "7",
}

def _ids_da_categoria_raiz(nome: str):
    # Proteínas e Carboidratos exigem as duas seções (1+2) e (3+4)
    if nome == "Fontes de Proteínas":
        return ["1", "2"]
    if nome == "Fontes de Carboidratos":
        return ["3", "4"]
    return [CATEGORIA_PARA_ID[nome]]

def categoria_completa(nome: str, respostas: dict) -> bool:
    # COMPLETA = TODAS seções exigidas têm entre 3 e 5 itens
    for cid in _ids_da_categoria_raiz(nome):
        n = len(respostas.get(cid, []))
        if n < 3 or n > 5:
            return False
    return True

TITULOS_CATEGORIAS = {
    "Fontes de Proteínas": "Proteínas: Almoço e Jantar",
    "Lanches de Fontes de Proteínas": "Proteínas: Lanches",
    "Fontes de Carboidratos": "Carboidratos: Almoço e Jantar",
    "Lanches de Fontes de Carboidratos": "Carboidratos: Lanches",
    "Fontes de Gorduras": "Gorduras: Almoço, Jantar e Lanches",
    "Vegetais": "Vegetais",
    "Frutas": "Frutas"
}

# [ALTERAÇÃO] mapa global para manter referência dos chips por NOME de categoria
chips_categorias: dict[str, ft.Control] = {}   # <- usado pela sincronização

# ------------------------------------------------------------
# Data
# ------------------------------------------------------------
def carregar_alimentos_padronizados(url):
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erro ao carregar alimentos_padronizados: {e}")
        return {}

# ------------------------------------------------------------
# Sincronização visual dos chips (chamar ao final da view)
# ------------------------------------------------------------
def sincronizar_estado_chips(page: ft.Page, respostas: dict):
    """
    Aplica o 'selecionado' visual nos chips de CATEGORIA
    conforme o dicionário 'respostas'.
    Requer chips_categorias preenchido durante a criação dos chips.
    """
    for nome, chip in chips_categorias.items():
        ativo = categoria_completa(nome, respostas)
        if hasattr(chip, "apply_selected_state"):
            # chips.py deve ter o patch apply_selected_state()
            chip.apply_selected_state(ativo)
        else:
            chip.selected = ativo
    page.update()  # único repaint

# ------------------------------------------------------------
# View
# ------------------------------------------------------------
def main(page: ft.Page, respostas: dict, auto_advance=True):
    hide_loading(page)
    configure_page(page)
    current_page = 7
    pb, update_progress = progress_bar2(page, current_page)
    back_btn = back_button(page, "/habitos_alimentares", current_page, update_progress)

    sub_titulo = ft.Text(
        "Selecione sua preferência alimentar abaixo:",
        size=12,
        color=AppTheme.get_color("TEXT_COLOR")
    )

    alimentos = carregar_alimentos_padronizados(link_json)

    def ir_para_agradecimento():
        async def next_page():
            show_loading(page, "Carregando...")
            await asyncio.sleep(0.5)
            hide_loading(page)
            page.go(f"/agradecimento?nutri_id={respostas['nutri_id']}&paciente_id={respostas['paciente_id']}")
        page.run_task(next_page)

    # --------------------------------------------------------
    # (Helper antigo – não usado nesta tela, mas mantido)
    # --------------------------------------------------------
    def gerar_grupo_com_search(categoria, respostas, feedback_text):
        id_categoria = CATEGORIA_PARA_ID[categoria]
        campo_busca_ref = ft.Ref[ft.TextField]()

        campo_busca = ft.TextField(
            ref=campo_busca_ref,
            label=ft.Text("Buscar novo alimento", size=12, color=AppTheme.get_color("TEXT_COLOR")),
            height=30,
            width=400,
            text_size=10,
            border_radius=6,
            content_padding=4,
            border_color=AppTheme.get_color("PRIMARY_COLOR"),
            on_change=lambda e: atualizar_lista(e.control.value),
        )

        coluna_chips = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)

        def scroll_para_searchbox():
            try:
                page.scroll_to_control(campo_busca_ref.current, duration=250)
            except Exception:
                pass

        def atualizar_lista(filtro=""):
            coluna_chips.controls.clear()
            lista_completa = alimentos.get(id_categoria, [])
            selecionados = respostas.setdefault(id_categoria, [])
            selecionados_set = set(selecionados)

            if filtro:
                lista_filtrada = [a for a in lista_completa if filtro.lower() in a["nome"].lower()]
            else:
                lista_filtrada = [a for a in lista_completa if a.get("prioridade") is True or a.get("prioridade") == "true"]

            chips_selecionados = [a for a in lista_completa if a["id_alimento"] in selecionados_set]
            ids_selecionados = set(a["id_alimento"] for a in chips_selecionados)
            chips_nao_selecionados = [a for a in lista_filtrada if a["id_alimento"] not in ids_selecionados]
            lista_final = chips_selecionados + chips_nao_selecionados

            if not lista_final:
                coluna_chips.controls.append(ft.Text("Nenhum alimento encontrado", color="red", size=11))
                return

            linha = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)

            for idx, alimento in enumerate(lista_final):
                nome = alimento["nome"]
                id_alimento = alimento["id_alimento"]

                def toggle_chip(e, id_alimento=id_alimento):
                    chip = e.control
                    selecionados = respostas.setdefault(id_categoria, [])

                    if chip.selected:
                        chip.selected = False
                        chip.bgcolor = AppTheme.get_color("CHIP_PREF_ALIM_COLOR_SELECTED")
                        if id_alimento in selecionados:
                            selecionados.remove(id_alimento)
                    else:
                        if len(selecionados) >= 5:
                            feedback_text.value = "Limite de seleção atingido."
                            feedback_text.color = "red"
                            feedback_text.opacity = 1
                            page.update()

                            async def resetar_msg():
                                await asyncio.sleep(3)
                                feedback_text.value = "Selecione de 3 a 5 alimentos."
                                feedback_text.color = "gray"
                                feedback_text.opacity = 0.8
                                page.update()

                            page.run_task(resetar_msg)
                            return

                        chip.selected = True
                        chip.bgcolor = AppTheme.get_color("CHIP_PREF_ALIM_COLOR")
                        selecionados.append(id_alimento)

                        campo_busca.value = ""
                        atualizar_lista()

                    page.update()
                    botao_continuar.update_state()

                chip = ft.Container(
                    content=ft.Text(nome, size=13, color=AppTheme.get_color("TEXT_COLOR")),
                    padding=ft.padding.all(4),
                    border_radius=AppTheme.BORDER_RADIUS,
                    on_click=toggle_chip,
                    animate=ft.animation.Animation(150, "easeInOut")
                )
                chip.selected = id_alimento in selecionados
                chip.bgcolor = AppTheme.get_color("CHIP_PREF_ALIM_COLOR") if chip.selected else AppTheme.get_color("CHIP_PREF_ALIM_COLOR_SELECTED")
                linha.controls.append(chip)

                if (idx + 1) % 3 == 0 or idx == len(lista_final) - 1:
                    coluna_chips.controls.append(linha)
                    linha = ft.Row(wrap=True, alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)

            page.update()

        atualizar_lista()

        async def focar_searchbox():
            await asyncio.sleep(0.1)
            if campo_busca_ref.current:
                try:
                    campo_busca_ref.current.focus()
                    scroll_para_searchbox()
                except Exception as e:
                    print(f"Erro ao focar: {e}")

        page.run_task(focar_searchbox)

        return ft.Column([campo_busca, coluna_chips])

    # --------------------------------------------------------
    # Validações
    # --------------------------------------------------------
    def validar_categoria(nome_categoria: str, respostas: dict):
        id_categoria = CATEGORIA_PARA_ID[nome_categoria]
        selecionados = respostas.get(id_categoria, [])
        if len(selecionados) < 3:
            return False, "Quantidade de alimentos insuficiente."
        elif len(selecionados) > 5:
            return False, "Quantidade máxima de alimentos atingida."
        return True, ""

    def verificar_categorias_invalidas(categorias, respostas):
        categorias_invalidas = []
        for categoria in categorias:
            valido, _ = validar_categoria(categoria, respostas)
            if not valido:
                categorias_invalidas.append(categoria)
        return categorias_invalidas

    # --------------------------------------------------------
    # Navegação para tela de seleção por categoria
    # --------------------------------------------------------
    def registrar_alimento(tipo_alimento, chip_botao):
        from urllib.parse import quote
        categoria_encoded = quote(tipo_alimento, safe="")
        page.go(f"/selecionar_alimentos?cat={categoria_encoded}")

    # --------------------------------------------------------
    # Chips de CATEGORIAS (com controle_externo=True)
    # [ALTERAÇÃO] registrar no dict chips_categorias para a sincronização
    # --------------------------------------------------------
    selecao_alimentos_botoes = [
        ("Fontes de Proteínas",     "Selecione ao menos 3 opções", "Fontes de Proteínas",     ICONSS['proteinas'],     1),
        ("Fontes de Carboidratos",  "Selecione ao menos 3 opções", "Fontes de Carboidratos",  ICONSS['carboidratos'],  1),
        ("Fontes de Gorduras",      "Selecione ao menos 3 opções", "Fontes de Gorduras",      ICONSS['gorduras'],      1),
        ("Vegetais",                "Selecione ao menos 3 opções", "Vegetais",                ICONSS['vegetais'],      1),
        ("Frutas",                  "Selecione ao menos 3 opções", "Frutas",                  ICONSS['frutas'],        1),
    ]

    def criar_botoes_tipo_alimento(niveis):
        botoes = []
        grupo = []
        for nivel, descricao, valor, imagem_url, quantidade_icones in niveis:
            chip = criar_chip_padrao2(
                texto=nivel,
                descricao=descricao,
                valor=nivel,
                on_select=lambda e, valor=valor: registrar_alimento(valor, e.control),
                grupo=grupo,
                selecionar_unico=False,
                icone=imagem_url,
                tipo_icone="imagem",
                quantidade_icones=quantidade_icones,
                chip_width=50,
                icon_size=45,
                controle_externo=True,  # estado visual será aplicado via sincronização
                chip_padding=ft.padding.symmetric(vertical=8, horizontal=8),
            )
            # [ALTERAÇÃO] salvar referência para sincronização
            chips_categorias[nivel] = chip
            botoes.append(chip)
            botoes.append(ft.Container(height=2))
        return botoes

    chip_controls = criar_botoes_tipo_alimento(selecao_alimentos_botoes)

    selecao_alimentos_container = ft.Container(
        content=ft.Column(
            controls=chip_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4
        ),
        alignment=ft.alignment.center,
        padding=ft.padding.all(6),
        width=370
    )

    # --------------------------------------------------------
    # Pagamento
    # --------------------------------------------------------
    def gerar_link_pagamento_front(respostas: dict) -> str:
        """
        Cria o link de pagamento chamando o backend.
        [MUDANÇA] — defense-in-depth: se 'external_reference' não existir aqui
        (por qualquer motivo), geramos a partir de nutri_id/paciente_id antes de enviar.
        """
        # [MUDANÇA] — Fallback defensivo
        n_id = respostas.get("nutri_id") or "nutri0001"
        p_id = respostas.get("paciente_id") or "pac0001"
        ext = respostas.get("external_reference") or f"{n_id}_{p_id}"
        respostas["external_reference"] = ext  # mantém consistente no dicionário em memória

        payload = {
            "nome_cliente": respostas.get("nome", "Paciente"),
            "email_cliente": respostas.get("email", ""),
            "valor_reais": respostas.get("valor_pago", 2.50),
            "referencia": ext,               # <- NUNCA nulo
            "nutri_id": n_id,
            "paciente_id": p_id,
        }
        resp = requests.post(f"{BACKEND_URL}/pagamento/link", json=payload, timeout=10)
        resp.raise_for_status()
        body = resp.json() if resp.content else {}
        return body.get("init_point", "")

    def botao_pagamento_click(e):
        try:
            # [MUDANÇA] — GARANTIR external_reference ANTES de criar o link
            n_id = respostas.get("nutri_id") or "nutri0001"
            p_id = respostas.get("paciente_id")
            if not p_id:
                page.snack_bar = ft.SnackBar(
                    content=ft.Text("Paciente sem ID. Volte e reinicie o fluxo."),
                    bgcolor="red"
                )
                page.snack_bar.open = True
                page.update()
                return

            # [MUDANÇA] — aqui garantimos a existência da ref usada pelo webhook
            respostas["external_reference"] = f"{n_id}_{p_id}"

            link_pagamento = gerar_link_pagamento_front(respostas)
            if not link_pagamento:
                raise RuntimeError("Backend não retornou init_point.")
            respostas["link_pagamento"] = link_pagamento
            ir_para_agradecimento()
        except Exception as err:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Erro ao gerar link: {err}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # [ALTERAÇÃO] validação do botão: exige categorias COMPLETAS (3–5)
    obrigatorias = [
        "Fontes de Proteínas",
        "Fontes de Carboidratos",
        "Fontes de Gorduras",
        "Vegetais",
        "Frutas",
    ]

    botao_continuar = create_continue_button(
        text="Pagamento",
        on_click=botao_pagamento_click,
        is_valid=lambda: all(categoria_completa(nome, respostas) for nome in obrigatorias),
    )

    # --------------------------------------------------------
    # Montagem da View
    # --------------------------------------------------------
    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/preferencias_alimentares",
            titulo="Preferências Alimentares",
            progresso=pb,
            back_btn=back_btn,
            conteudo=[
                ft.Container(content=sub_titulo, alignment=ft.alignment.center, padding=2),
                selecao_alimentos_container,
            ],
            exibir_botao_continuar=True,
            botao_continuar=botao_continuar,
            altura_dinamica=True,
        )
    )

    # [ALTERAÇÃO] aplicar estado visual dos chips após montar a árvore
    sincronizar_estado_chips(page, respostas)

    botao_continuar.update_state()


    page.update()