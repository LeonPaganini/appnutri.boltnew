import flet as ft
from app.components.layout import *
from app.utils.navigation import handle_route_change

def main(page: ft.Page):
    configure_page(page)  # Configura a página com o background
    respostas = {}
    

    # Vincula o roteador
    page.on_route_change = lambda e: handle_route_change(page, respostas)
    
    # Só direciona para "/" se a rota inicial for vazia (primeira carga)
    if not page.route or page.route == "/app":
        page.go("/app")  # Abre a página Boas Vindas

    # Se já existe rota na URL (ex: após refresh), o Flet automaticamente dispara on_route_change
    # e vai carregar a página correta baseada no que está no navegador.
    # Não precisa forçar nenhum redirect aqui.

if __name__ == "__main__":
    ft.app(
        target=main,
        view=ft.AppView.WEB_BROWSER,
        assets_dir="assets"
    )



# import flet as ft
# from app.components.layout import *
# from app.utils.navigation import handle_route_change

# def main(page: ft.Page):
#     configure_page(page)  # Configura a página com o background
#     respostas = {}
#     page.on_route_change = lambda e: handle_route_change(page, respostas)
#     page.go("/")  # Abre a página Boas Vindas;

    
    
# if __name__ == "__main__":
#     ft.app(
#         target=main,
#         view=ft.AppView.WEB_BROWSER,
#         assets_dir="assets"  # <-- Isso garante que /static/ seja público
#     )
