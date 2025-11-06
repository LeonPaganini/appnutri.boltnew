import flet as ft
import time
from app.themes.tema import AppTheme
import threading



### ----------------------------------- ELEMENTOS DA PÁGINA IMC ---------------------------------------------- ###


# Rótulos para o IMC e suas cores
imc_labels = ["Abaixo do Peso", "Peso Normal", "Sobrepeso", "Obesidade"]
imc_thresholds = [18.5, 24.9, 29.9, 40]  # Limites adaptados para normalização
imc_colors = {
    "Abaixo do Peso": ft.Colors.ORANGE_300,
    "Peso Normal": ft.Colors.GREEN_400,
    "Sobrepeso": ft.Colors.ORANGE_500,
    "Obesidade": ft.Colors.RED_600,
}

# Frases motivacionais empáticas
frases_motivacionais = {
    "Abaixo do Peso": "Você está abaixo do peso desejável. Vamos alcançar um peso saudável juntas.",
    "Peso Normal": "Ótimo trabalho! Chegou a hora de conquistar objetivos mais desafiadores. Certo?",
    "Sobrepeso": "Você está acima do peso desejável. Esta é sua chance de conquistar seu peso ideal.",
    "Obesidade": "Hoje você está acima do peso desejável. Não desista, estou aqui para te ajudar a ter sucesso."
}

def determinar_categoria(imc):
    for i, threshold in enumerate(imc_thresholds):
        if imc < threshold:
            return imc_labels[i]
    return imc_labels[-1]

def criar_barra(imc, resultado_imc_text, carregando_text, page, frase_motivacional):
    imc_proporcao = min(imc / imc_thresholds[-1], 1.0)  # Normaliza para 1.0
    categoria = determinar_categoria(imc)
    cor_barra = imc_colors.get(categoria, ft.Colors.GREY)

    progress_bar = ft.ProgressBar(value=0, color=cor_barra, bar_height=10)
    
    container = ft.Container(
        content=progress_bar,
        width=340,
        height=25,
        bgcolor=AppTheme.get_color("BACKGROUND_COLOR"),
        border_radius=5,
        padding=10,
        alignment=ft.alignment.center,
    )

    # Função para animar a barra de progresso
    def animar_barra():
        passos = 100  # Total de interações da animação
        for i in range(passos + 1):
            progress_bar.value = i / passos * imc_proporcao
            time.sleep(0.005)  # Controle a velocidade da animação
            page.update()  # Atualiza a página

        # Torna o resultado do IMC visível após a animação e oculta o texto "Carregando..."
        carregando_text.visible = False
        resultado_imc_text.visible = True
        frase_motivacional.visible = True
        page.update()

 # Função para fazer o texto "Carregando..." piscar
    def piscar_texto():
        while carregando_text.visible:
            carregando_text.opacity = 0 if carregando_text.opacity == 1 else 1
            page.update()
            time.sleep(0.2)  # Intervalo de piscar

    # Chamar a função de animação e a função de piscar em threads separadas
    threading.Thread(target=animar_barra).start()
    threading.Thread(target=piscar_texto).start()

    return container
