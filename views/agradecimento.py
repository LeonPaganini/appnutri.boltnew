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
    """
    Extrai nutri_id, paciente_id e status da URL, ignorando demais parâmetros indesejados.
    Se existirem parâmetros extra, retorna apenas os necessários.
    """
    rota = getattr(page, "route", None) or getattr(page, "url", "")
    if "?" in rota:
        query = rota.split("?")[1]
        params = parse_qs(query)
        nutri_id = params.get("nutri_id", [None])[0]
        paciente_id = params.get("paciente_id", [None])[0]
        # Trata para pegar apenas o PRIMEIRO status não vazio e não null, se houver múltiplos
        status_lista = [s for s in params.get("status", []) if s and s != "null"]
        status = status_lista[0] if status_lista else None
        return nutri_id, paciente_id, status
    return None, None, None

def limpar_url_agradecimento(page, nutri_id, paciente_id):
    """
    Se a URL conter parâmetros indesejados, faz reload limpando tudo exceto nutri_id e paciente_id.
    Usado para evitar bug de navegação se Mercado Pago incluir query string extra.
    """
    rota = getattr(page, "route", None) or getattr(page, "url", "")
    if "?" in rota:
        import urllib.parse
        qs = urllib.parse.parse_qs(rota.split("?")[1])
        # Só deixa nutri_id e paciente_id
        allowed = {"nutri_id": nutri_id, "paciente_id": paciente_id}
        final_query = urllib.parse.urlencode(allowed)
        nova_url = f"/agradecimento?{final_query}"
        # Redireciona apenas se necessário
        if not (len(qs.keys()) == 2 and "nutri_id" in qs and "paciente_id" in qs):
            page.go(nova_url)
            return True
    return False

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

    # --- Extração dos parâmetros e status da URL ---
    nutri_id_url, paciente_id_url, status_pagamento = extrair_parametros_url(page)
    nutri_id = nutri_id_url or respostas.get("nutri_id") or "nutri0001"
    paciente_id = paciente_id_url or respostas.get("paciente_id")
    external_ref = f"{nutri_id}_{paciente_id}"

    # --- Correção automática da URL se query string vier "suja" do Mercado Pago ---
    if limpar_url_agradecimento(page, nutri_id, paciente_id):
        return  # O page.go() acima já dispara novo load e interrompe execução aqui

    # --- Tratamento de status de pagamento recebido pela URL ---
    if status_pagamento == "failure":
        link_pagamento = buscar_link_pagamento(nutri_id, paciente_id) or ""
        btn_pagar_novamente = ft.ElevatedButton(
            text="Tentar pagar novamente",
            url=link_pagamento,
            disabled=not bool(link_pagamento),
            style=ft.ButtonStyle(
                bgcolor=AppTheme.get_color("PRIMARY_COLOR"),
                color=ft.colors.WHITE,
                shape=ft.RoundedRectangleBorder(radius=14)
            ),
            width=240
        )
        page.views.clear()
        page.views.append(
            ft.View(
                "/agradecimento",
                controls=[
                    ft.Text("❌ Pagamento não foi concluído.", size=22, color="red"),
                    ft.Text("Se preferir, tente novamente.", size=16),
                    btn_pagar_novamente
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()
        return

    if status_pagamento == "pending":
        page.views.clear()
        page.views.append(
            ft.View(
                "/agradecimento",
                controls=[
                    ft.Text("⏳ Pagamento ainda não concluído.", size=20, color="orange"),
                    ft.Text("Aguarde a confirmação ou realize o pagamento.", size=16)
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        page.update()
        return
    # --------------------------------------------------------------

    # FLUXO NORMAL (success ou sem status)
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

    botao_mercadopago = ft.ElevatedButton(
        url=respostas.get("link_pagamento") or "",
        content=ft.Row(
            controls=[
                ft.Image(src=ICONSS['mercado_pago_icon'], width=34, height=34),
                ft.Text("Pagar com Mercado Pago", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, size=18),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=18,
        ),
        disabled=not bool(respostas.get("link_pagamento")),
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.YELLOW,
            color=ft.colors.WHITE,
            overlay_color="#B7F5A9",
            shape=ft.RoundedRectangleBorder(radius=14),
            elevation={"": 8, "hovered": 12, "pressed": 2},
            shadow_color="#a3a3a3",
            padding=ft.Padding(12, 6, 12, 6),
        ),
        width=320,
        height=60,
    )

    def atualizar_botao_pagamento():
        link = respostas.get("link_pagamento") or ""
        botao_mercadopago.url = link
        botao_mercadopago.disabled = not bool(link)
        page.update()

    def finalizar_formulario(e):
    # --- UI: modal de processamento ---
        progress = ft.ProgressRing()
        status_text = ft.Text("Finalizando formulário, aguarde...", size=12)
        icon = ft.Icon(name=ft.icons.SCHEDULE, color=ft.colors.AMBER_600, size=34)
    
        dialog_content = ft.Column(
            controls=[progress, status_text, icon],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            tight=True,
        )
        dialog = ft.AlertDialog(
            title=ft.Text("Processando"),
            content=dialog_content,
            actions=[],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            open=True,
            modal=True,
        )
        page.dialog = dialog
        page.update()
    
        # --- helper: recarrega snapshot do RTDB (garante que /plano_cod receba tudo atualizado) ---
        def _get_rtdb_snapshot(nutri_id, paciente_id):
            FIREBASE_URL = os.getenv(
                "FIREBASE_URL",
                "https://app-nutri-inteligentev1-default-rtdb.firebaseio.com"
            )
            url = f"{FIREBASE_URL}/{nutri_id}/{paciente_id}/respostas.json"
            try:
                r = requests.get(url, timeout=8)  # verify False não é necessário aqui
                if r.status_code == 200 and r.json():
                    return r.json()
            except Exception:
                pass
            return {}
    
        # --- helper: fecha dialog ---
        def _fechar_dialog():
            page.dialog.open = False
            page.update()
    
        def _work():
            try:
                # IDs
                n_id = respostas.get("nutri_id")
                p_id = respostas.get("paciente_id")
                if not n_id or not p_id:
                    # tenta extrair de external_reference "nutri_pac"
                    ext = respostas.get("external_reference") or ""
                    if "_" in ext:
                        n_id, p_id = ext.split("_", 1)
    
                # 1) salva o que já foi coletado (leve, sem PDFs)
                payload = dict(respostas)  # snapshot atual
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/finalizar_light",
                        json={"dados": payload},
                        timeout=60,
                    )
                    data = {}
                    try:
                        if resp.content:
                            data = resp.json()
                    except ValueError:
                        data = {"ok": False, "detail": f"Resposta inválida: {resp.text}"}
                except Exception as ex:
                    data = {"ok": False, "detail": str(ex)}
    
                if resp.status_code == 200 and data.get("ok"):
                    # --- mensagem amigável ao paciente ---
                    status_text.value = (
                        "Formulário finalizado! 😊\n\n"
                        "Seu RELATÓRIO será enviado ao seu e-mail.\n"
                        "O seu PLANO ALIMENTAR será validado pela Nutricionista Thaís Paganini antes do envio."
                    )
                    dialog.title = ft.Text("Formulário finalizado")
                    if data.get("email_enviado", False):
                        icon.name = ft.icons.MARK_EMAIL_READ_ROUNDED
                        icon.color = ft.colors.GREEN_500
                    else:
                        icon.name = ft.icons.EMAIL_OUTLINED
                        icon.color = ft.colors.AMBER_700
                    if progress in dialog.content.controls:
                        dialog.content.controls.remove(progress)
                    dialog.actions = [ft.TextButton("Ok, entendi", on_click=lambda _: _fechar_dialog())]
                    page.update()
    
                    # 2) garantia de persistência do PLANO e MACROS no Firebase
                    def _persistir_plano():
                        try:
                            # (a) recarrega snapshot mais atual do RTDB
                            snap = _get_rtdb_snapshot(n_id, p_id) if (n_id and p_id) else {}
                            corpo = dict(snap or {})
                            # preserva IDs
                            if n_id: corpo["nutri_id"] = n_id
                            if p_id: corpo["paciente_id"] = p_id
                            # se já houver plano no front, envia também (não conflita; backend decide)
                            if respostas.get("plano_alimentar"):
                                corpo["plano_alimentar"] = respostas["plano_alimentar"]
                            if respostas.get("plano_alimentar_compacto"):
                                corpo["plano_alimentar_compacto"] = respostas["plano_alimentar_compacto"]
                            if respostas.get("macros"):
                                corpo["macros"] = respostas["macros"]
    
                            # (b) dispara /plano_cod (esse endpoint GERA e PERSISTE plano + compacto + macros)
                            try:
                                r2 = requests.post(f"{BACKEND_URL}/plano_cod", json=corpo, timeout=120)
                                # opcional: checar sucesso
                                # jr = r2.json() if "json" in (r2.headers.get("content-type") or "").lower() else {}
                                # print("plano_cod:", r2.status_code, jr)
                            except Exception:
                                pass
    
                            # 3) notifica a equipe (failsafe)
                            try:
                                assunto = "Nova análise de plano pendente"
                                msg = (
                                    f"Há uma nova análise pendente.\n\n"
                                    f"Nutricionista: {n_id}\n"
                                    f"Paciente: {respostas.get('nome', 'Paciente')} (ID: {p_id})\n"
                                    f"E-mail do paciente: {respostas.get('email','')}\n"
                                    f"External ref: {respostas.get('external_reference') or (n_id and p_id and f'{n_id}_{p_id}')}\n"
                                )
                                email_payload = {
                                    "to": "equipe.nutripaganini@gmail.com",
                                    "assunto": assunto,
                                    "mensagem": msg,
                                    "nutri_id": n_id,
                                    "paciente_id": p_id,
                                }
                                for ep in ("/email/notificar_pendencia", "/email/notificar", "/enviar_email"):
                                    try:
                                        _ = requests.post(f"{BACKEND_URL}{ep}", json=email_payload, timeout=10)
                                    except Exception:
                                        continue
                            except Exception:
                                pass
    
                        except Exception:
                            # não quebrar o fluxo visual
                            pass
    
                    threading.Thread(target=_persistir_plano, daemon=True).start()
    
                else:
                    # erro no finalizar_light
                    detail = (data.get("detail") if isinstance(data, dict) else None) or (resp.text if 'resp' in locals() else "")
                    status_text.value = f"❌ Falha ao finalizar. {detail[:200]}"
                    dialog.title = ft.Text("Erro ao finalizar")
                    icon.name = ft.icons.ERROR_OUTLINE
                    icon.color = ft.colors.RED_400
                    if progress in dialog.content.controls:
                        dialog.content.controls.remove(progress)
                    dialog.actions = [ft.TextButton("Fechar", on_click=lambda _: _fechar_dialog())]
                    page.update()
    
            except Exception as err:
                status_text.value = f"❌ Erro inesperado: {err}"
                dialog.title = ft.Text("Erro")
                icon.name = ft.icons.ERROR_OUTLINE
                icon.color = ft.colors.RED_400
                if progress in dialog.content.controls:
                    dialog.content.controls.remove(progress)
                dialog.actions = [ft.TextButton("Fechar", on_click=lambda _: _fechar_dialog())]
                page.update()
    
        threading.Thread(target=_work, daemon=True).start()

    # def gerar_plano_modo_codigo(e):
    #     progress = ft.ProgressRing()
    #     status_text = ft.Text("Gerando plano e enviando e-mail, aguarde...", size=12)
    #     email_status_icon = ft.Icon(name=ft.icons.EMAIL_OUTLINED, color=ft.colors.GREY, size=34)
    #     dialog_content = ft.Column(
    #         controls=[progress, status_text, email_status_icon],
    #         alignment=ft.MainAxisAlignment.CENTER,
    #         horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    #         spacing=20,
    #     )
    #     dialog = ft.AlertDialog(
    #         title=ft.Text("Processando"),
    #         content=dialog_content,
    #         actions=[],
    #         actions_alignment=ft.MainAxisAlignment.CENTER,
    #         open=True,
    #     )
    #     page.dialog = dialog
    #     page.update()
    
    #     def call_backend():
    #         try:
    #             payload = dict(respostas)
    #             resp = requests.post(f"{BACKEND_URL}/plano_cod", json=payload, timeout=120, verify=False)

    #             data = {}
    #             try:
    #                 if resp.content:
    #                     data = resp.json()
    #             except ValueError:
    #                 data = {"sucesso": False, "erro": f"Resposta inválida: {resp.text}"}
    #             if resp.status_code == 200 and data.get("sucesso"):
    #                 status_text.value = f"E-mail enviado para: {respostas.get('email','')}"
    #                 dialog.title = ft.Text("Plano gerado (modo código)!")
    #                 email_status_icon.name = ft.icons.MARK_EMAIL_READ_ROUNDED
    #                 email_status_icon.color = ft.colors.GREEN_500
    #                 dialog.content.controls.remove(progress)
    #             else:
    #                 status_text.value = f"❌ Falha ao gerar/enviar plano."
    #                 dialog.title = ft.Text("Erro")
    #                 email_status_icon.name = ft.icons.ERROR_OUTLINE
    #                 email_status_icon.color = ft.colors.RED_400
    #                 dialog.content.controls.remove(progress)
    #             page.update()
    #         except Exception as err:
    #             status_text.value = f"❌ Erro inesperado: {err}"
    #             dialog.title = ft.Text("Erro")
    #             email_status_icon.name = ft.icons.ERROR_OUTLINE
    #             email_status_icon.color = ft.colors.RED_400
    #             dialog.content.controls.remove(progress)
    #             page.update()
    
    #     threading.Thread(target=call_backend, daemon=True).start()
        
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

    # Quando carregar a tela, verifica se o link de pagamento já existe e atualiza o botão!
    link_pagamento_existente = buscar_link_pagamento(nutri_id, paciente_id)
    if link_pagamento_existente:
        respostas["link_pagamento"] = link_pagamento_existente
        atualizar_botao_pagamento()
        logger.info("⏩ Link já existe. Iniciando monitoramento automático!")
        checar_status_pagamento(btn_finalizar, nutri_id, paciente_id, page, timeout=900)

    # Se o link for gerado depois (ex: por função backend), atualize SEMPRE após salvar!
    def gerar_link_pagamento_backend():
        # Sempre gere a referência na hora do envio
        external_reference = f"{respostas.get('nutri_id', 'nutri0001')}_{respostas.get('paciente_id', 'pacXXXX')}"
        respostas["external_reference"] = external_reference

        payload = {
            "nome_cliente": respostas.get("nome", "Paciente"),
            "email_cliente": respostas.get("email", ""),
            "valor_reais": respostas.get("valor_pago", 0.5),
            "referencia": external_reference,  # sempre correto!
            "nutri_id": respostas.get("nutri_id"),
            "paciente_id": respostas.get("paciente_id")
        }
        try:
            resp = requests.post(f"{BACKEND_URL}/pagamento/link", json=payload, timeout=10)
            novo_link = resp.json()["init_point"]
            respostas["link_pagamento"] = novo_link
            salvar_no_firebase(respostas.get("nutri_id"), respostas.get("paciente_id"), respostas)
            atualizar_botao_pagamento()
            logger.info(f"✅ Novo link de pagamento salvo e botão atualizado: {novo_link}")
        except Exception as err:
            page.snack_bar = ft.SnackBar(content=ft.Text(f"Erro ao gerar link: {err}"), bgcolor="red")
            page.snack_bar.open = True
            page.update()

    # Botões extras: Telegram, WhatsApp...
    botao_telegram = ft.ElevatedButton(
        url="https://t.me/algoritmosuplementos",
        content=ft.Row(
            controls=[
                ft.Image(src=ICONSS['telegram_icon'], width=34, height=34),
                ft.Text("Grupo Telegram", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, size=18),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=18,
        ),
        style=ft.ButtonStyle(
            bgcolor="#34b7f1",
            color=ft.colors.WHITE,
            overlay_color="#1977f3",
            shape=ft.RoundedRectangleBorder(radius=14),
            elevation={"": 8, "hovered": 12, "pressed": 2},
            shadow_color="#a3a3a3",
            padding=ft.Padding(12, 6, 12, 6),
        ),
        width=320,
        height=60,
    )

    botao_whatsapp = ft.ElevatedButton(
        url="https://chat.whatsapp.com/seu_grupo_aqui",
        content=ft.Row(
            controls=[
                ft.Image(src=ICONSS['whatsapp_icon'], width=34, height=34),
                ft.Text("Grupo WhatsApp", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE, size=18),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=18,
        ),
        style=ft.ButtonStyle(
            bgcolor="#25d366",
            color=ft.colors.WHITE,
            overlay_color="#128c7e",
            shape=ft.RoundedRectangleBorder(radius=14),
            elevation={"": 8, "hovered": 12, "pressed": 2},
            shadow_color="#a3a3a3",
            padding=ft.Padding(12, 6, 12, 6),
        ),
        width=320,
        height=60,
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
            ft.Text("Você será encaminhado ao Mercado Pago para executar o pagamento.", size=14, text_align=ft.TextAlign.CENTER, color=cor_texto_padrao),
            ft.Container(content=ft.Column(controls=[botao_mercadopago], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER), alignment=ft.alignment.center, padding=ft.padding.all(6), width=320),
            divisoria_passo("02"),
            ft.Text("Faça parte do grupo de ofertas de suplementos e \nartigos fitness e receba promoções exclusivas diariamente", size=14, text_align=ft.TextAlign.CENTER, color=cor_texto_padrao),
            ft.Text("*Não obrigatório", size=10, color=ft.Colors.RED_400, text_align=ft.TextAlign.CENTER),
            ft.Container(content=botao_telegram, alignment=ft.alignment.center, padding=ft.padding.all(10), width=320),
            ft.Container(content=botao_whatsapp, alignment=ft.alignment.center, padding=ft.padding.all(10), width=320),
            divisoria_passo("03"),
            ft.Text("Com o pagamento aprovado, clique em \n “Finalizar Formulário” para receber seu plano alimentar\n por e-mail.", size=14, text_align=ft.TextAlign.CENTER, color=cor_texto_padrao),
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

