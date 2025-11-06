import flet as ft
import logging

# 🔥 Dicionário de ícones já configurado
ICONSS = {
    "perder_peso": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fperder_peso.png?alt=media&token=c62d72df-3992-499e-9fbc-4bd1c9ef3c2d",
    "agua_moderado": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fagua_moderado.png?alt=media&token=1ad7801e-f4fc-427e-983b-dfaac205a249",
    "agua_nao": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fagua_nao.png?alt=media&token=0d4a245b-fe39-4c89-ad42-ccc49a7aab5e",
    "agua_otima": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fagua_otima.png?alt=media&token=f3a65259-6fc3-4dc2-9f87-2c4e7e4d7eef",
    "agua_pouca": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fagua_pouca.png?alt=media&token=5cfe4b21-e251-4c9d-9832-f017e9b67023",
    "carboidratos": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fcarboidratos.png?alt=media&token=9087d239-f6e6-4615-b4d7-1832878e3284",
    "extrem_ativo": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fextrem_ativo.png?alt=media&token=3c49f005-fe6a-4201-94cb-3bd5c8517a7f",
    "frutas": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Ffrutas.png?alt=media&token=3f5752a7-0c09-4496-a262-59558f25f294",
    "ganhar_peso": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fganhar_peso.png?alt=media&token=78c6bba3-d127-4730-baea-24445d7e596f",
    "gorduras": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fgorduras.png?alt=media&token=ecc3bf23-a8bf-4df2-8221-bcb7dae4ec9e",
    "manter_peso": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fmanter_peso.png?alt=media&token=1c8e55e2-bb8d-47cb-b703-80d8dc8833f9",
    "moderad_ativo": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fmoderad_ativo.png?alt=media&token=7035d857-6a71-4779-a7f2-ffad645e3c67",
    "muito_ativo": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fmuito_ativo.png?alt=media&token=b67956bd-bbc5-4c1c-8688-66886a34b14d",
    "pouco_ativo": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fpouco_ativo.png?alt=media&token=0c46eb1c-76c2-468b-bc37-0183e228c336",
    "proteinas": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fproteinas.png?alt=media&token=a3c9319d-7f07-42ef-aade-98029a5afb81",
    "refeicao": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Frefeicao.png?alt=media&token=1a8b8e97-e394-4170-9618-412cc2d2ffce",
    "sedentario": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fsedentario.png?alt=media&token=e6159ce3-1434-4379-8d54-ee4b7bf940a7",
    "sono_bom": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fsono_bom.png?alt=media&token=5422a706-5778-4cdd-abbe-4425bf23d21f",
    "sono_otimo": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fsono_otimo.png?alt=media&token=8ffb5499-d914-40b1-8a3e-74a5c528ab5f",
    "sono_regular": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fsono_regular.png?alt=media&token=2b886492-f174-4414-a609-6ccfe7b931cb",
    "sono_ruim": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fsono_ruim.png?alt=media&token=05b35d86-2eba-4348-9f3a-5ba003a8a0d9",
    "vegetais": "https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fvegetais.png?alt=media&token=5911c32f-9886-4441-8ee7-d6b5a4c11ec7",
    "whatsapp_icon":"https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fwhatsapp_icon.png?alt=media&token=76c23fc7-42c5-4cb9-9c38-cb828a645c5c",
    "mercado_pago_icon":"https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Fmercadopago_logo.png?alt=media&token=c5c79264-d382-497c-a2b3-6d8ca6ea87a1",
    "telegram_icon":"https://firebasestorage.googleapis.com/v0/b/app-nutri-inteligentev1.firebasestorage.app/o/assets%2Fcompartilhados%2Ficons%2Ftelegram_icon.png?alt=media&token=1dd10390-44a4-4153-987d-d6f8515e7226",
}

def preload_images(page: ft.Page):
    """
    Pré-carrega todas as imagens de ícones definidos no dicionário ICONSS.
    Isso ajuda a evitar atrasos ou falhas de carregamento visual durante a navegação.
    """
    logging.info("🟢 Pré-carregando imagens...")
    for key, url in ICONSS.items():
        page.assets.append(url)
    logging.info("✅ Todas as imagens pré-carregadas!")