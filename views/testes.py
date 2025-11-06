import flet as ft
import requests
import threading
import os
import urllib3
from app.components.icons import ICONSS
from app.components.layout import configure_page, pagina_base_responsivo
from app.themes.tema import AppTheme
import logging
from urllib.parse import parse_qs

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BACKEND_URL = "https://appnutri-8lyy.onrender.com"

def extrair_parametros_url(page):
    rota = getattr(page, "route", None) or getattr(page, "url", "")
    if "?" in rota:
        query = rota.split("?")[1]
        params = parse_qs(query)
        nutri_id = params.get("nutri_id", [None])[0]
        paciente_id = params.get("paciente_id", [None])[0]
        return nutri_id, paciente_id
    return None, None

def carregar_respostas_do_firebase(nutri_id, paciente_id):
    FIREBASE_URL = os.getenv("FIREBASE_URL", "https://app-nutri-inteligentev1-default-rtdb.firebaseio.com")
    url = f"{FIREBASE_URL}/{nutri_id}/{paciente_id}/respostas.json"
    try:
        r = requests.get(url, timeout=5, verify=False)
        if r.status_code == 200 and r.json():
            logger.info(f"Respostas carregadas do Firebase: {nutri_id}/{paciente_id}")
            return r.json()
    except Exception as e:
        logger.error(f"Erro ao carregar respostas do Firebase: {e}")
    return {}

def salvar_no_firebase(nutri_id: str, paciente_id: str, respostas: dict) -> bool:
    url = f"{BACKEND_URL}/salvar_respostas"
    payload = {
        "nutri_id": nutri_id,
        "paciente_id": paciente_id,
        "dados_paciente": respostas
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao salvar no backend Firebase: {e}")
        return False

def consultar_pagamento_confirmado(nutri_id: str, paciente_id: str) -> bool:
    FIREBASE_URL = os.getenv("FIREBASE_URL", "https://app-nutri-inteligentev1-default-rtdb.firebaseio.com")
    url = f"{FIREBASE_URL}/{nutri_id}/{paciente_id}/respostas/pagamento_confirmado.json"
    try:
        r = requests.get(url, timeout=5, verify=False)
        return r.status_code == 200 and r.json() is True
    except:
        return False

def buscar_link_pagamento(nutri_id, paciente_id):
    FIREBASE_URL = os.getenv("FIREBASE_URL", "https://app-nutri-inteligentev1-default-rtdb.firebaseio.com")
    url = f"{FIREBASE_URL}/{nutri_id}/{paciente_id}/respostas/link_pagamento.json"
    try:
        r = requests.get(url, timeout=5, verify=False)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def checar_status_pagamento(botao, nutri_id, paciente_id, page, timeout=600):
    logger.info(f"🔎 Iniciando monitoramento de pagamento para {nutri_id}/{paciente_id}")
    if getattr(botao, "_monitorando", False):
        logger.info("Monitoramento já ativo, ignorando nova chamada.")
        return
    botao._monitorando = True
    def loop():
        tempo_passado = 0
        while tempo_passado < timeout:
            import time
            time.sleep(10)
            tempo_passado += 10
            if consultar_pagamento_confirmado(nutri_id, paciente_id):
                logger.info("✅ Pagamento confirmado! (monitoramento encerrado)")
                botao.disabled = False
                botao.bgcolor = AppTheme.get_color("PRIMARY_COLOR")
                page.update()
                break
            else:
                logger.info(f"⏳ Aguardando confirmação do pagamento... ({tempo_passado}s)")
        else:
            logger.warning("⚠️ Timeout de pagamento atingido (15 minutos).")
            page.snack_bar = ft.SnackBar(content=ft.Text(
                "Tempo limite de 15 minutos para pagamento atingido. Gere um novo link para tentar novamente."),
                bgcolor="orange"
            )
            page.snack_bar.open = True
            page.update()
        botao._monitorando = False
    threading.Thread(target=loop, daemon=True).start()

def divisoria_passo(numero):
    return ft.Row(
        controls=[
            ft.Container(content=ft.Divider(thickness=2, color=ft.Colors.GREY_400, height=1), expand=True),
            ft.Text(str(numero), size=18, weight=ft.FontWeight.BOLD, color=AppTheme.get_color("PRIMARY_COLOR")),
            ft.Container(content=ft.Divider(thickness=2, color=ft.Colors.GREY_400, height=1), expand=True),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        height=20,
        width=330,
    )

def main(page: ft.Page, respostas: dict, auto_advance=True):
    configure_page(page)
    dark_mode_ativo = page.theme_mode == ft.ThemeMode.DARK
    cor_texto_padrao = AppTheme.get_color_by_mode("TEXT_COLOR", dark_mode_ativo)

    nutri_id_url, paciente_id_url = extrair_parametros_url(page)
    nutri_id = nutri_id_url or respostas.get("nutri_id") or "nutri0001"
    paciente_id = paciente_id_url or respostas.get("paciente_id")
    external_ref = f"{nutri_id}_{paciente_id}"

    if not respostas.get("nome") or not respostas.get("email"):
        respostas.clear()
        respostas_firebase = carregar_respostas_do_firebase(nutri_id, paciente_id)
        if not respostas_firebase:
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Sessão expirada ou paciente não encontrado. Refaça o processo."),
                bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()
            return
        respostas.update(respostas_firebase)
    else:
        salvar_no_firebase(nutri_id, paciente_id, respostas)

    respostas["nutri_id"] = nutri_id
    respostas["paciente_id"] = paciente_id
    respostas["external_reference"] = external_ref
    respostas.setdefault("pagamento_status", "pendente")
    respostas.setdefault("pagamento_confirmado", False)
    respostas.setdefault("valor_pago", 0.50)

    logger.info(f"paciente_id: {paciente_id}")
    logger.info(f"nutri_id: {nutri_id}")

    btn_finalizar = ft.ElevatedButton(
        text="Finalizar Formulário",
        on_click=lambda e: finalizar_formulario(e),
        disabled=True,
        style=ft.ButtonStyle(
            bgcolor=AppTheme.get_color("SECONDARY_COLOR"),
            color=AppTheme.get_color("BUTTON_COLOR_TEXT"),
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=20, vertical=20),
        )
    )

    link_pagamento_existente = buscar_link_pagamento(nutri_id, paciente_id)
    if link_pagamento_existente:
        respostas["link_pagamento"] = link_pagamento_existente
        logger.info("⏩ Link já existe. Iniciando monitoramento automático!")
        checar_status_pagamento(btn_finalizar, nutri_id, paciente_id, page, timeout=900)

    def finalizar_formulario(e):
        progress = ft.ProgressRing()
        status_text = ft.Text("Gerando PDFs e enviando e-mail, aguarde...", size=12)
        email_status_icon = ft.Icon(name=ft.icons.EMAIL_OUTLINED, color=ft.colors.GREY, size=34)
        dialog_content = ft.Column(
            controls=[progress, status_text, email_status_icon],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )
        dialog = ft.AlertDialog(
            title=ft.Text("Processando"),
            content=dialog_content,
            actions=[],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            open=True,
        )
        page.dialog = dialog
        page.update()
        def call_backend():
            try:
                payload = dict(respostas)
                resp = requests.post(f"{BACKEND_URL}/finalizar_formulario", json=payload, timeout=120)
                data = resp.json() if resp.content else {}
                if resp.status_code == 200 and data.get("sucesso"):
                    status_text.value = f"E-mail enviado para: {respostas.get('email','')}"
                    dialog.title = ft.Text("Tudo pronto!")
                    email_status_icon.name = ft.icons.MARK_EMAIL_READ_ROUNDED
                    email_status_icon.color = ft.colors.GREEN_500
                    dialog.content.controls.remove(progress)
                    salvar_no_firebase(nutri_id, paciente_id, respostas)
                else:
                    status_text.value = f"❌ Falha ao enviar e-mail."
                    dialog.title = ft.Text("Erro ao enviar e-mail")
                    email_status_icon.name = ft.icons.ERROR_OUTLINE
                    email_status_icon.color = ft.colors.RED_400
                    dialog.content.controls.remove(progress)
                page.update()
            except Exception as err:
                status_text.value = f"❌ Erro inesperado: {err}"
                dialog.title = ft.Text("Erro")
                email_status_icon.name = ft.icons.ERROR_OUTLINE
                email_status_icon.color = ft.colors.RED_400
                dialog.content.controls.remove(progress)
                page.update()
        threading.Thread(target=call_backend, daemon=True).start()

    def gerar_link_pagamento_backend():
        payload = {
            "nome_cliente": respostas.get("nome", "Paciente"),
            "email_cliente": respostas.get("email", ""),
            "valor_reais": respostas.get("valor_pago", 0.5),
            "referencia": respostas.get("external_reference"),
            "nutri_id": respostas.get("nutri_id"),
            "paciente_id": respostas.get("paciente_id")
        }
        logger.info(f"🔗 Solicitando geração de novo link de pagamento para {nutri_id}/{paciente_id}")
        resp = requests.post(f"{BACKEND_URL}/pagamento/link", json=payload, timeout=10)
        respostas["link_pagamento"] = resp.json()["init_point"]
        salvar_no_firebase(nutri_id, paciente_id, respostas)
        logger.info(f"✅ Novo link de pagamento salvo: {respostas['link_pagamento']}")

    def gerar_pagamento_ao_clicar(e, valor):
        try:
            link_existente = buscar_link_pagamento(nutri_id, paciente_id)
            if link_existente:
                respostas["link_pagamento"] = link_existente
                logger.info("Link de pagamento já existente! Abrindo checkout Mercado Pago.")
            else:
                logger.info("Nenhum link salvo, gerando novo link de pagamento...")
                gerar_link_pagamento_backend()
            page.launch_url(respostas["link_pagamento"])
            checar_status_pagamento(btn_finalizar, nutri_id, paciente_id, page, timeout=900)
        except Exception as erro:
            logger.error(f"❌ Erro ao gerar link de pagamento: {erro}")
            page.snack_bar = ft.SnackBar(content=ft.Text(f"❌ Erro ao gerar link: {erro}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    chip_mercadopago = ft.ElevatedButton(
        text="Link de Pagamento",
        on_click=lambda e: gerar_pagamento_ao_clicar(e, None),
        style=ft.ButtonStyle(
            bgcolor="#EAF8E3",
            color=ft.colors.BLACK,
            overlay_color="#B7F5A9",
            shape=ft.RoundedRectangleBorder(radius=14),
            elevation={"": 8, "hovered": 12, "pressed": 2},
            shadow_color="#a3a3a3",
            padding=ft.Padding(12, 6, 12, 6),
        ),
        width=320,
        height=60,
    )

    # --- BLOCO DE TESTE (como pedido) ---
    botao_teste_click = ft.ElevatedButton(
        "Open with CLICK",
        on_click=lambda e: e.page.launch_url("https://google.com"),
    )
    botao_teste_url = ft.ElevatedButton(
        "Open with URL",
        url="https://google.com"
    )

    def simular_pagamento_aprovado(e=None):
        respostas["pagamento_confirmado"] = True
        respostas["pagamento_status"] = "aprovado"
        salvar_no_firebase(nutri_id, paciente_id, respostas)
        btn_finalizar.disabled = False
        btn_finalizar.bgcolor = AppTheme.get_color("PRIMARY_COLOR")
        page.snack_bar = ft.SnackBar(content=ft.Text("✅ Pagamento simulado como aprovado!"), bgcolor="green")
        page.snack_bar.open = True
        btn_finalizar.update()
        page.update()

    btn_teste_pagamento = ft.FloatingActionButton(
        icon=ft.Icons.CHECK_CIRCLE,
        tooltip="Simular Pagamento Aprovado",
        on_click=simular_pagamento_aprovado,
        bgcolor=ft.colors.GREEN_400,
        mini=True,
        visible=True,
    )

    conteudo = ft.Column(
        controls=[
            ft.Container(content=ft.Image(src="https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fnutri_0001%2Flogo2_nutri_0001.png?alt=media&token=cbb3ed42-d61b-49d5-8cae-4ab42d19238e", width=260, height=170), alignment=ft.alignment.center, padding=10),
            divisoria_passo("01"),
            ft.Text("Você será encaminhado ao Mercado Pago para executar o pagamento.", size=12, text_align=ft.TextAlign.CENTER, color=cor_texto_padrao),
            ft.Container(content=ft.Column(controls=[chip_mercadopago], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), alignment=ft.alignment.center, padding=ft.padding.all(6), width=320),
            divisoria_passo("02"),
            ft.Text("TESTE: botão abrindo link externo:", size=12, text_align=ft.TextAlign.CENTER, color=cor_texto_padrao),
            botao_teste_click,
            botao_teste_url,
            divisoria_passo("03"),
            ft.Text("Com o pagamento aprovado, clique em \n “Finalizar Formulário” para receber seu plano alimentar\n por e-mail.", size=12, text_align=ft.TextAlign.CENTER, color=cor_texto_padrao),
            ft.Container(content=btn_finalizar, alignment=ft.alignment.center, padding=ft.padding.only(top=10, bottom=20)),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=18,
        scroll=ft.ScrollMode.HIDDEN,
    )
    page.overlay.append(btn_teste_pagamento)
    page.views.append(pagina_base_responsivo(page, "/", "Agradecemos pela confiança", [conteudo], altura_dinamica=True))
    page.update()
    checar_status_pagamento(btn_finalizar, nutri_id, paciente_id, page, timeout=900)