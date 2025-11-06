# app/views/selecionar_alimentos.py
# ----------------------------------
# Página dedicada para seleção de alimentos por categoria.
# Compatível com Flet 0.25.1 e reutilizando helpers/estilos já existentes.

import flet as ft
import asyncio
from urllib.parse import urlparse, parse_qs, quote

from app.themes.tema import AppTheme
from app.components.progress import progress_bar2
from app.components.layout import pagina_base_responsivo, configure_page
from app.components.buttons import back_button, create_continue_button
from app.components.loading import show_loading, hide_loading

import requests

# === Fonte do JSON (mesmo link já usado em preferencias_alimentares) ===
LINK_JSON = "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Falimentos_categorizados.json?alt=media&token=4a0abfdb-4ca5-43dd-b0d8-b1182fc9642a"

# === Mapas idênticos aos da tela de categorias (evita import circular) ===
CATEGORIA_PARA_ID = {
    "Fontes de Proteínas": "1",
    "Lanches de Fontes de Proteínas": "2",
    "Fontes de Carboidratos": "3",
    "Lanches de Fontes de Carboidratos": "4",
    "Fontes de Gorduras": "5",
    "Vegetais": "6",
    "Frutas": "7",
}

TITULOS_CATEGORIAS = {
    "Fontes de Proteínas": "Proteínas: Almoço e Jantar",
    "Lanches de Fontes de Proteínas": "Proteínas: Lanches",
    "Fontes de Carboidratos": "Carboidratos: Almoço e Jantar",
    "Lanches de Fontes de Carboidratos": "Carboidratos: Lanches",
    "Fontes de Gorduras": "Gorduras: Almoço, Jantar e Lanches",
    "Vegetais": "Vegetais",
    "Frutas": "Frutas",
}

# -------- Helpers locais --------
def _carregar_alimentos(url: str) -> dict:
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"[selecionar_alimentos] Erro ao carregar JSON: {e}")
        return {}

def _validar_categoria(nome_categoria: str, respostas: dict) -> tuple[bool, str]:
    cat_id = CATEGORIA_PARA_ID[nome_categoria]
    itens = respostas.get(cat_id, [])
    if len(itens) < 3:
        return False, "Selecione pelo menos 3 alimentos."
    if len(itens) > 5:
        return False, "Selecione no máximo 5 alimentos."
    return True, ""

def _subcategorias_para(categoria_raiz: str) -> list[tuple[str, str]]:
    # Para Proteínas e Carboidratos, mantém (1+2) e (3+4)
    if categoria_raiz == "Fontes de Proteínas":
        return [
            ("Fontes de Proteínas", TITULOS_CATEGORIAS["Fontes de Proteínas"]),
            ("Lanches de Fontes de Proteínas", TITULOS_CATEGORIAS["Lanches de Fontes de Proteínas"]),
        ]
    if categoria_raiz == "Fontes de Carboidratos":
        return [
            ("Fontes de Carboidratos", TITULOS_CATEGORIAS["Fontes de Carboidratos"]),
            ("Lanches de Fontes de Carboidratos", TITULOS_CATEGORIAS["Lanches de Fontes de Carboidratos"]),
        ]
    # Demais são “singulares”
    return [(categoria_raiz, TITULOS_CATEGORIAS[categoria_raiz])]

def main(page: ft.Page, respostas: dict):
    """Rota: /selecionar_alimentos?cat=<categoria_url_encoded>"""
    hide_loading(page)
    configure_page(page)

    # === Lê categoria da querystring ===
    qs = parse_qs(urlparse(page.route).query or "")
    categoria_raiz = (qs.get("cat") or [""])[0] or "Fontes de Proteínas"

    # === Progresso & voltar === (mantém etapa 7 como em preferencias)
    current_page = 7
    pb, update_progress = progress_bar2(page, current_page)
    back_btn = back_button(page, "/preferencias_alimentares", current_page, update_progress)

    # === Dados ===
    alimentos = _carregar_alimentos(LINK_JSON)
    subcats = _subcategorias_para(categoria_raiz)

    # === UI: blocos de seleção ===
    blocos = []
    feedback_map: dict[str, ft.Text] = {}
    search_ref_map: dict[str, ft.Ref[ft.TextField]] = {}
    colunas_map: dict[str, ft.Column] = {}

    ALTURA_CHIPS = 250

    def _montar_lista(nome_categoria: str, filtro: str = ""):
        """(Re)monta a lista de chips de uma subcategoria no respectivo Column."""
        col_chips = colunas_map[nome_categoria]
        col_chips.controls.clear()

        cat_id = CATEGORIA_PARA_ID[nome_categoria]
        lista_completa = alimentos.get(cat_id, [])
        selecionados = respostas.setdefault(cat_id, [])

        if filtro:
            base = [a for a in lista_completa if filtro.lower() in a["nome"].lower()]
        else:
            base = [a for a in lista_completa if a.get("prioridade") is True or a.get("prioridade") == "true"]

        # Sempre manter selecionados no topo
        sel_set = set(selecionados)
        escolhidos = [a for a in lista_completa if a["id_alimento"] in sel_set]
        ids_escolhidos = set(a["id_alimento"] for a in escolhidos)

        nao_escolhidos = [a for a in base if a["id_alimento"] not in ids_escolhidos]
        lista_final = escolhidos + nao_escolhidos

        if not lista_final:
            col_chips.controls.append(ft.Text("Nenhum alimento encontrado.", size=11, color="red"))
            page.update()
            return

        linha = ft.Row(
            wrap=True,
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        for idx, a in enumerate(lista_final):
            nome = a["nome"]
            id_alimento = a["id_alimento"]

            def _toggle(e, _id=id_alimento, _cat_id=cat_id, _nome=nome):
                chip = e.control
                itens = respostas.setdefault(_cat_id, [])

                if chip.selected:
                    chip.selected = False
                    chip.bgcolor = AppTheme.get_color("CHIP_PREF_ALIM_COLOR_SELECTED")
                    if _id in itens:
                        itens.remove(_id)
                else:
                    # Limite 5
                    if len(itens) >= 5:
                        fb = feedback_map[nome_categoria]
                        fb.value = "Limite de 5 itens atingido."
                        fb.color = "red"
                        fb.opacity = 1
                        page.update()

                        async def _reset():
                            await asyncio.sleep(2.5)
                            fb.value = "Selecione de 3 a 5 alimentos."
                            fb.color = "gray"
                            fb.opacity = 0.8
                            page.update()
                        page.run_task(_reset)
                        return
                    chip.selected = True
                    chip.bgcolor = AppTheme.get_color("CHIP_PREF_ALIM_COLOR")
                    itens.append(_id)

                # Limpa filtro para reordenar e atualizar estado do botão
                sr = search_ref_map[nome_categoria].current
                if sr:
                    sr.value = ""
                _montar_lista(nome_categoria, "")
                btn_confirmar.update_state()
                page.update()

            chip = ft.Container(
                content=ft.Text(nome, size=13, color=AppTheme.get_color("TEXT_COLOR")),
                padding=ft.padding.all(4),
                border_radius=AppTheme.BORDER_RADIUS,
                on_click=_toggle,
                animate=ft.animation.Animation(120, "easeInOut"),
            )
            chip.selected = id_alimento in selecionados
            chip.bgcolor = AppTheme.get_color("CHIP_PREF_ALIM_COLOR") if chip.selected else AppTheme.get_color("CHIP_PREF_ALIM_COLOR_SELECTED")

            linha.controls.append(chip)

            if (idx + 1) % 3 == 0 or idx == len(lista_final) - 1:
                col_chips.controls.append(linha)
                linha = ft.Row(
                    wrap=True,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )

        page.update()

    # Montagem visual de cada subcategoria (título + feedback + busca + chips)
    for nome_cat, titulo in subcats:
        feedback = ft.Text(
            "Selecione de 3 a 5 alimentos.",
            size=11, color="gray", opacity=0.8, animate_opacity=200
        )
        feedback_map[nome_cat] = feedback

        sr = ft.Ref[ft.TextField]()
        search_ref_map[nome_cat] = sr

        col_chips = ft.Column(scroll=ft.ScrollMode.ADAPTIVE, expand=True)
        colunas_map[nome_cat] = col_chips

        def _on_change(e, _nome=nome_cat):
            _montar_lista(_nome, e.control.value or "")

        busca = ft.TextField(
            ref=sr,
            label=ft.Text("Buscar novo alimento", size=12, color=AppTheme.get_color("TEXT_COLOR")),
            height=30, width=400, text_size=10,
            border_radius=6, content_padding=4,
            border_color=AppTheme.get_color("PRIMARY_COLOR"),
            on_change=_on_change
        )

        blocos.extend([
            ft.Text(titulo, size=13, weight=ft.FontWeight.BOLD, color=AppTheme.get_color("TEXT_COLOR")),
            feedback,
            ft.Container(
                content=ft.Column([busca, col_chips]),
                height=ALTURA_CHIPS,
                border_radius=4,
                padding=0,
                alignment=ft.alignment.top_left,
            ),
            ft.Container(height=10),
        ])

    # Inicializa listas após construir refs
    for nome_cat, _ in subcats:
        _montar_lista(nome_cat, "")

    # ----- Botão Confirmar (desabilita até ficar válido) -----
    def _is_valid():
        for nome_cat, _ in subcats:
            ok, _ = _validar_categoria(nome_cat, respostas)
            if not ok:
                return False
        return True

    def _on_confirm(e):
        # Apenas volta para a tela de categorias; seleções já estão em `respostas`
        page.go("/preferencias_alimentares")

    btn_confirmar = create_continue_button(
        text="Confirmar seleção",
        is_valid=_is_valid,
        on_click=_on_confirm
    )

    # Força estado inicial
    btn_confirmar.update_state()

    # ----- Render -----
    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/selecionar_alimentos",
            titulo=f"Seleção: {categoria_raiz}",
            progresso=pb,
            back_btn=back_btn,
            conteudo=[
                ft.Container(
                    content=ft.Text(
                        "Escolha de 3 a 5 alimentos por seção.",
                        size=12,
                        color=AppTheme.get_color("TEXT_COLOR")
                    ),
                    alignment=ft.alignment.center,
                    padding=ft.padding.only(bottom=6),
                ),
                *blocos,
            ],
            exibir_botao_continuar=True,
            botao_continuar=btn_confirmar,
            altura_dinamica=True,  # respeita limites e deixa fluir em celulares
        )
    )
    page.update()
