import flet as ft
from app.views import (
    landing,
    boas_vindas,
    dados_pessoais,
    imc_usuario,
    saude_sono,
    agua_alimentacao,
    exercicios,
    habitos_alimentares,
    preferencias_alimentares,
    agradecimento,
    redirect_ticket,
    testes,
    selecionar_alimentos,
)

# Dicionário de rotas (cada rota aponta para a função main correspondente)
routes = {
    "/landing": landing.main,
    "/app": boas_vindas.main,
    "/dados_pessoais": dados_pessoais.main,
    "/imc_usuario": imc_usuario.main,
    "/agua_alimentacao": agua_alimentacao.main,
    "/exercicios": exercicios.main,
    "/saude_sono": saude_sono.main,
    "/habitos_alimentares": habitos_alimentares.main,
    "/preferencias_alimentares": preferencias_alimentares.main,
    "/agradecimento": agradecimento.main,
    "/redirect_ticket": redirect_ticket.main,
    "/testes": testes.main,
    "/selecionar_alimentos": selecionar_alimentos.main,

}

def handle_route_change(page, respostas):
    """
    Centraliza a lógica de navegação entre as páginas do app.
    Busca a função correspondente à rota e chama com (page, respostas).
    """
    # Extrai o path base ignorando parâmetros de query string
    path_base = page.route.split("?")[0]

    # Busca a função da rota, se não encontrar vai para dados_pessoais
    func = routes.get(path_base, boas_vindas.main)

    # Limpa as views (garante que sempre renderiza a tela correta)
    page.views.clear()

    try:
        func(page, respostas)
    except Exception as e:
        # Mostra erro visível para não deixar a tela cinza caso algo quebre numa view
        import traceback
        page.views.clear()
        page.views.append(
            ft.View(
                route=path_base,
                controls=[
                    ft.Text("Erro ao carregar página.", color="red", size=20),
                    ft.Text(str(e)),
                    ft.Text(traceback.format_exc())
                ],
                scroll=ft.ScrollMode.AUTO
            )
        )
    page.update()
