import requests
import os

# URL do backend — pode ser lida da env do Render ou definida aqui:
BACKEND_URL = os.getenv("BACKEND_URL", "https://appnutri-8lyy.onrender.com")

def gerar_link_pagamento(nome_cliente, email_cliente, valor_reais, referencia):
    payload = {
        "nome_cliente": nome_cliente,
        "email_cliente": email_cliente,
        "valor_reais": valor_reais,
        "referencia": referencia
    }
    resp = requests.post(f"{BACKEND_URL}/pagamento/link", json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()["init_point"]

def gerar_relatorio_pdf(respostas):
    resp = requests.post(f"{BACKEND_URL}/relatorio/pdf", json=respostas, timeout=30)
    resp.raise_for_status()
    return resp.content  # bytes do PDF

def gerar_plano_pdf(respostas):
    resp = requests.post(f"{BACKEND_URL}/plano/pdf", json=respostas, timeout=30)
    resp.raise_for_status()
    return resp.content  # bytes do PDF

def gerar_textos_relatorio(respostas):
    resp = requests.post(f"{BACKEND_URL}/ai/relatorio", json=respostas, timeout=30)
    resp.raise_for_status()
    return resp.json()

def gerar_plano_alimentar_ai(respostas):
    resp = requests.post(f"{BACKEND_URL}/ai/plano", json=respostas, timeout=30)
    resp.raise_for_status()
    return resp.json()
