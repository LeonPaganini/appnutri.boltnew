import flet as ft
import requests
import asyncio
import random

from app.views.mockup_usuarios import usuarios_mock

# [MUDANÇA] — data/hora BR com timezone SP (apenas string)
from datetime import datetime
from zoneinfo import ZoneInfo  # Py>=3.9

from app.components.layout import configure_page, pagina_base_responsivo
from app.components.buttons import create_button_with_condition
from app.components.fields import create_text_field
from app.themes.tema import AppTheme
from app.components.loading import show_loading, hide_loading


# --- UTILITÁRIO DE TESTE AUTOMATIZADO ---
def simular_fluxo_completo(page, respostas):
    """
    Sorteia um usuário mock e preenche o formulário para teste automático.
    """
    usuario = random.choice(usuarios_mock)
    respostas.clear()
    respostas.update(usuario)
    # Avança direto para agradecimento
    page.go(f"/agradecimento")


# Configurações do projeto
BACKEND_URL = "https://appnutri-8lyy.onrender.com"  # FastAPI
NUTRI_ID_PADRAO = "nutri0001"


# [MUDANÇA] — helper minimalista: retorna só a string BR
def agora_sp_br() -> str:
    tz = ZoneInfo("America/Sao_Paulo")
    return datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")


# [MUDANÇA] — normaliza telefone (mantém só dígitos)
def so_digitos(s: str) -> str:
    return "".join(ch for ch in (s or "") if ch.isdigit())


# [MUDANÇA] — validação simples de e-mail/telefone (agora usando normalização)
def validar_email(valor):
    return isinstance(valor, str) and ("@" in valor and "." in valor)


def validar_telefone(valor):
    v = so_digitos(valor)
    return v.isdigit() and 10 <= len(v) <= 11


def mostrar_erro(page, mensagem, is_dark):
    hide_loading(page)
    snack_bar = ft.SnackBar(
        content=ft.Text(
            mensagem,
            color=AppTheme.get_color_by_mode("DARK_BUTTON_TEXT_COLOR", is_dark)
        ),
        bgcolor=AppTheme.get_color_by_mode("WARNING_TEXT_COLOR", is_dark),
        behavior=ft.SnackBarBehavior.FLOATING,
        duration=3000,
    )
    page.overlay.append(snack_bar)
    snack_bar.open = True
    page.update()


def buscar_paciente_id_por_telefone(nutri_id, telefone):
    """Consulta o Firebase para verificar se já existe paciente cadastrado com esse telefone"""
    try:
        url = f"https://app-nutri-inteligentev1-default-rtdb.firebaseio.com/{nutri_id}.json"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and resp.json():
            dados = resp.json()
            for k, v in dados.items():
                tel_cadastrado = (
                    v.get("telefone") or
                    v.get("respostas", {}).get("telefone")
                )
                # [MUDANÇA] — comparar sempre dígito a dígito
                if tel_cadastrado and so_digitos(tel_cadastrado) == so_digitos(telefone):
                    return k  # Ex: "pac0001"
    except Exception as e:
        print("Erro ao consultar Firebase:", e)
    return None


def gerar_id_paciente(nutri_id: str) -> str:
    """Gera próximo id sequencial com base no Firebase"""
    try:
        url = f"https://app-nutri-inteligentev1-default-rtdb.firebaseio.com/{nutri_id}.json"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and resp.json():
            dados = resp.json()
            numeros = [
                int(key.replace("pac", ""))
                for key in dados.keys()
                if key.startswith("pac") and key.replace("pac", "").isdigit()
            ]
            proximo_num = max(numeros) + 1 if numeros else 1
        else:
            proximo_num = 1
        return f"pac{str(proximo_num).zfill(4)}"
    except Exception as e:
        print(f"Erro ao gerar ID: {e}")
        return "pac0001"


# [MUDANÇA] — manter SOMENTE data_cadastro_br; não salvar ISO/início
def salvar_no_firebase(nutri_id, paciente_id, dados):
    """
    Salva os dados básicos do paciente no backend/Firebase
    """
    external_reference = dados.get("external_reference") or f"{nutri_id}_{paciente_id}"
    dados["external_reference"] = external_reference

    # Só setamos data_cadastro_br se ainda não existir
    dados.setdefault("data_cadastro_br", agora_sp_br())

    url = f"{BACKEND_URL}/salvar_respostas"
    payload = {
        "nutri_id": nutri_id,
        "paciente_id": paciente_id,
        "dados_paciente": dados,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        return resp.status_code == 200
    except Exception as e:
        print("Erro ao salvar no Firebase:", e)
        return False


def main(page: ft.Page, respostas: dict, auto_advance=True):
    hide_loading(page)
    configure_page(page)
    is_dark = page.theme_mode == ft.ThemeMode.DARK

    # UI Components
    titulo_boas_vindas = ft.Text(
        "Bem-vinda(o) ao seu plano Inteligente!",
        size=24,
        weight=ft.FontWeight.BOLD,
        color=AppTheme.get_color_by_mode("TEXT_COLOR", is_dark_mode=is_dark),
        text_align=ft.TextAlign.CENTER
    )

    frase_motivacional = ft.Text(
        "Vamos iniciar sua jornada rumo a uma alimentação mais saudável e equilibrada.",
        size=14,
        color=AppTheme.get_color_by_mode("TEXT_COLOR", is_dark_mode=is_dark),
        text_align=ft.TextAlign.CENTER
    )

    nutri_id_logo = "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fnutri_0001%2Flogo.png?alt=media&token=3430d7f7-8dab-4418-8cfa-94866a93e1b2"
    logo = ft.Image(
        src=nutri_id_logo,
        width=260,
        height=170,
        fit=ft.ImageFit.COVER
    )

    telefone_field = create_text_field(
        "Telefone com DDD",
        AppTheme.get_color_by_mode("SECONDARY_COLOR", is_dark_mode=is_dark),
        AppTheme.get_color_by_mode("TEXT_FIELD_COLOR", is_dark_mode=is_dark),
        page=page,
        cache_key="telefone_field",
        keyboard_type=ft.KeyboardType.NUMBER
    )

    email_field = create_text_field(
        "E-mail",
        AppTheme.get_color_by_mode("SECONDARY_COLOR", is_dark_mode=is_dark),
        AppTheme.get_color_by_mode("TEXT_FIELD_COLOR", is_dark_mode=is_dark),
        page=page,
        cache_key="email_field",
        keyboard_type=ft.KeyboardType.TEXT
    )

    def campos_preenchidos():
        return bool(telefone_field.content.value and email_field.content.value)

    # [MUDANÇA] — flag simples para evitar duplo clique
    _em_andamento = {"iniciar": False}

    def iniciar_anamnese(e):
        # [MUDANÇA] — debounce
        if _em_andamento["iniciar"]:
            return
        _em_andamento["iniciar"] = True

        # Normaliza e valida
        telefone_raw = (telefone_field.content.value or "").strip()
        telefone = so_digitos(telefone_raw)  # normaliza
        email = (email_field.content.value or "").strip()

        if not validar_telefone(telefone):
            mostrar_erro(page, "Telefone inválido. Insira com DDD (somente números).", is_dark)
            _em_andamento["iniciar"] = False
            return
        if not validar_email(email):
            mostrar_erro(page, "E-mail inválido.", is_dark)
            _em_andamento["iniciar"] = False
            return

        # Preenche respostas iniciais
        respostas["telefone"] = telefone
        respostas["email"] = email
        respostas["nutri_id"] = NUTRI_ID_PADRAO

        # Feedback
        mostrar_erro(page, "Verificando cadastro...", is_dark)

        def fluxo_id_e_salvamento():
            try:
                paciente_id_existente = buscar_paciente_id_por_telefone(NUTRI_ID_PADRAO, telefone)
                if paciente_id_existente:
                    async def fechar_loader_e_mostrar_erro():
                        hide_loading(page)
                        mostrar_erro(
                            page,
                            "Usuário já cadastrado. Utilize outro telefone ou prossiga com o cadastro existente.",
                            is_dark
                        )
                    page.run_task(fechar_loader_e_mostrar_erro)
                    return

                # Usuário novo
                novo_paciente_id = gerar_id_paciente(NUTRI_ID_PADRAO)
                respostas["paciente_id"] = novo_paciente_id

                dados_iniciais = {
                    "telefone": telefone,
                    "email": email,
                    "nutri_id": NUTRI_ID_PADRAO,
                    "paciente_id": novo_paciente_id,
                    # Sem datas de início; apenas data_cadastro_br será setada no salvar_no_firebase()
                }

                sucesso = salvar_no_firebase(NUTRI_ID_PADRAO, novo_paciente_id, dados_iniciais)
                if not sucesso:
                    async def erro_salvar():
                        hide_loading(page)
                        mostrar_erro(page, "Erro ao salvar dados. Tente novamente.", is_dark)
                    page.run_task(erro_salvar)
                    return

                # Próxima tela
                async def avancar_para_proxima():
                    hide_loading(page)
                    page.go("/dados_pessoais")
                page.run_task(avancar_para_proxima)

            except Exception as ex:
                async def erro_geral():
                    hide_loading(page)
                    mostrar_erro(page, f"Erro ao verificar cadastro: {ex}", is_dark)
                page.run_task(erro_geral)
            finally:
                # [MUDANÇA] — libera para outra tentativa se necessário
                _em_andamento["iniciar"] = False

        import threading
        threading.Thread(target=fluxo_id_e_salvamento, daemon=True).start()

    iniciar_btn = create_button_with_condition(
        text="Iniciar Anamnese",
        color=AppTheme.get_color_by_mode("PRIMARY_COLOR", is_dark_mode=is_dark),
        on_click=iniciar_anamnese,
        condition=campos_preenchidos,
        width=250
    )

    # --- BOTÃO DE TESTE AUTOMÁTICO (VISÍVEL SÓ EM DEV) ---
    botao_teste = ft.ElevatedButton(
        "Testar Fluxo Automático",
        bgcolor="#FFD600",
        color="#333",
        on_click=lambda e: simular_fluxo_completo(page, respostas),
        width=220,
        tooltip="Executa todo o fluxo do formulário automaticamente para testes."
    )

    page.views.append(
        pagina_base_responsivo(
            page=page,
            route="/",
            titulo="",
            conteudo=[
                titulo_boas_vindas,
                logo,
                frase_motivacional,
                telefone_field,
                email_field,
                iniciar_btn,
                #botao_teste,
            ]
        )
    )
    page.update()