import flet as ft
import requests
import os
import time
from urllib.parse import parse_qs

def extrair_parametros_url(page):
    rota = getattr(page, "route", None) or getattr(page, "url", "") or ""
    if "?" in rota:
        query = rota.split("?")[1]
    else:
        query = getattr(page, "query", "")
    params = parse_qs(query)
    nutri_id = params.get("nutri_id", [None])[0]
    paciente_id = params.get("paciente_id", [None])[0]
    return nutri_id, paciente_id

def buscar_ticket_url(nutri_id, paciente_id):
    FIREBASE_URL = os.getenv("FIREBASE_URL", "https://app-nutri-inteligentev1-default-rtdb.firebaseio.com")
    url = f"{FIREBASE_URL}/{nutri_id}/{paciente_id}/respostas/ticket_url.json"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and r.json():
            return r.json()
    except Exception as e:
        print(f"Erro ao buscar ticket_url: {e}")
    return None

def main(page: ft.Page, respostas: dict, auto_advance=True):
    page.title = "Redirecionando..."
    page.views.clear()
    page.views.append(
        ft.View(
            "/redirect_ticket",
            controls=[ft.Text("Aguarde... consultando comprovante de pagamento.", size=18)],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    page.update()

    nutri_id, paciente_id = extrair_parametros_url(page)
    ticket_url = None

    tentativas = 10  # pode ajustar para até 20, se quiser
    for _ in range(tentativas):
        if nutri_id and paciente_id:
            ticket_url = buscar_ticket_url(nutri_id, paciente_id)
            if ticket_url:
                break
        time.sleep(1.5)

    page.views.clear()
    if ticket_url:
        # Tenta redirecionar (pode funcionar em alguns navegadores)
        try:
            page.launch_url(ticket_url)
        except Exception:
            pass
        # Sempre mostra botão para garantir acesso em qualquer navegador
        page.views.append(
            ft.View(
                "/redirect_ticket",
                controls=[
                    ft.Text("Seu comprovante está pronto!", size=18, color="green"),
                    ft.TextButton("Acessar Comprovante", url=ticket_url),
                    ft.Text("Se não abrir automaticamente, clique no botão acima.", size=12)
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    else:
        page.views.append(
            ft.View(
                "/redirect_ticket",
                controls=[
                    ft.Text("Comprovante ainda não está disponível.", size=18, color="red"),
                    ft.Text("Aguarde alguns segundos e tente novamente.", size=14),
                    ft.ElevatedButton("Tentar novamente", on_click=lambda e: main(page, respostas))
                ],
                vertical_alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
    page.update()