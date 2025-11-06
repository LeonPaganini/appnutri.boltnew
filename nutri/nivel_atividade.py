 ### ---------------------------------- ELEMENTOS CÁLCULOS ATIVIDADE FÍSICA ---------------------------------###

 # Função para criar botões a partir de uma lista de opções
def determinar_nivel_atividade(dias_atividade, minutos_por_dia, tipo_atividade, horas_sedentarias, dias_forca, tipo_trabalho):
    # Classificação inicial
    nivel_atividade = "Baixo"

    # Avaliação de atividade moderada a vigorosa
    if dias_atividade >= 3 and minutos_por_dia >= 20 and tipo_atividade in ["moderada", "vigorosa"]:
        nivel_atividade = "Moderado"
    if dias_atividade >= 5 and minutos_por_dia >= 30 and tipo_atividade == "vigorosa":
        nivel_atividade = "Alto"

    # Consideração de atividades sedentárias
    if horas_sedentarias > 8:
        nivel_atividade = "Baixo"

    # Consideração de exercícios de força
    if dias_forca >= 2:
        if nivel_atividade == "Baixo":
            nivel_atividade = "Moderado"
        elif nivel_atividade == "Moderado":
            nivel_atividade = "Alto"

    # Consideração do tipo de trabalho
    if tipo_trabalho == "Predominantemente sentado":
        nivel_atividade = "Baixo"
    elif tipo_trabalho == "Parcialmente sentado":
        if nivel_atividade == "Baixo":
            nivel_atividade = "Moderado"
    elif tipo_trabalho == "Caminhando":
        if nivel_atividade == "Baixo":
            nivel_atividade = "Moderado"
        elif nivel_atividade == "Moderado":
            nivel_atividade = "Alto"
    elif tipo_trabalho == "Força bruta":
        nivel_atividade = "Alto"

    return nivel_atividade
