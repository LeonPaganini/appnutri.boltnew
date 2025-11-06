def calcular_gasto_energetico(respostas, metodo="harris_benedict"):
    peso = float(respostas["peso_atual"])
    altura = float(respostas["altura"])
    idade = int(respostas["idade"])
    sexo = respostas["sexo"].lower()
    objetivo = respostas["objetivo"].lower()
    fator_atividade = float(respostas["Nível de Atividade"])

    if metodo == "harris_benedict":
        if sexo == "masculino":
            tmb = 66 + (13.8 * peso) + (5 * altura) - (6.8 * idade)
        else:
            tmb = 655 + (9.6 * peso) + (1.8 * altura) - (4.7 * idade)
    else:
        raise ValueError("Método de cálculo ainda não implementado.")

    # Gasto energético total (GET)
    get = tmb * fator_atividade

    # Ajuste fixo por objetivo
    if "perder" in objetivo:
        calorias_meta = get * 0.80  # déficit de 20%
        estrat_dietetica = "Dieta Hipocalórica"
        respostas["estrategia_alimentar"] = estrat_dietetica

    elif "ganhar" in objetivo:
        calorias_meta = get * 1.15  # superávit de 15%
        estrat_dietetica = "Dieta Hipercalórica"
        respostas["estrategia_alimentar"] = estrat_dietetica
    else:
        calorias_meta = get  # manter
        estrat_dietetica = "Dieta Normocalórica"
        respostas["estrategia_alimentar"] = estrat_dietetica

    # Macronutrientes base: 40% C, 30% P, 30% G
    prot_kcal = calorias_meta * 0.30
    carb_kcal = calorias_meta * 0.40
    gord_kcal = calorias_meta * 0.30

    macros = {
        "proteinas_g": round(prot_kcal / 4),
        "carboidratos_g": round(carb_kcal / 4),
        "gorduras_g": round(gord_kcal / 9)
    }

    # Atualiza o dicionário original
    respostas["TMB"] = round(tmb)
    respostas["GET"] = round(get)
    respostas["calorias_meta"] = round(calorias_meta)
    respostas["macros"] = macros
    respostas["metodo_calculo"] = metodo

    return respostas

