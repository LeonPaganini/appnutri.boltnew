import random
import json

# Carregue seu JSON real de alimentos
with open('app/views/alimentos_categorizados.json', encoding='utf-8') as f:
    alimentos_categorizados = json.load(f)

# --- Listas de possibilidades para sortear dados aleatórios ---
nomes_femininos = [
    "Ana", "Bianca", "Camila", "Daniela", "Elisa", "Fernanda", "Gabriela", "Helena", "Isabela", "Juliana",
    "Karen", "Larissa", "Mariana", "Nathalia", "Olivia"
]
nomes_masculinos = [
    "Bruno", "Carlos", "Eduardo", "Fábio", "Gustavo"
]
sobrenomes = ["Silva", "Oliveira", "Santos", "Souza", "Ferreira", "Costa", "Pereira", "Rodrigues", "Martins", "Almeida"]

condicoes_imc = ["Magreza", "Normal", "Sobrepeso", "Obesidade I", "Obesidade II", "Obesidade III"]
objetivos = ["Perder Peso", "Ganhar Peso", "Manter Peso"]
qualidade_sono = ["Ótimo", "Bom", "Regular", "Ruim"]
horas_sono = ["Mais de 8 Horas", "5 a 8 Horas", "Menos de 5 Horas"]
atividades = ["Não se Aplica", "Caminhada", "Corrida", "Ciclismo", "Natação", "Yoga", "Pilates", "Musculação", "Dança", "Lutas", "Crossfit", "Outros"]
tempos_atividade = ["10 minutos", "20 minutos", "30 minutos", "40 minutos", "50 minutos", "1h", "1h20", "1h30", "2h", "2h30", "3h"]
# Sempre baixo para os mocks de teste
niveis_atividade = [1.2, 1.375]
consumo_agua = ["Consumo baixo de Água", "Consumo Moderado de Água", "Consumo ideal de Água", "Consumo Ruim de Água"]
refeicoes_diarias = ["2 Refeições", "3 Refeições", "4 Refeições", "5 Refeições", "6 Refeições"]

def gerar_horarios_refeicoes_ordenados(qtd_refeicoes):
    """
    Gera uma lista de horários em ordem crescente, espaçados uniformemente no dia.
    Retorna lista de dicionários no formato [{"horas": "08", "minutos": "00"}, ...]
    """
    hora_inicio = 7   # Primeira refeição pode ser entre 7h e 8h
    hora_fim = 22     # Última até 22h
    intervalo = (hora_fim - hora_inicio) / (qtd_refeicoes - 1) if qtd_refeicoes > 1 else 0
    horarios = []
    for i in range(qtd_refeicoes):
        hora = int(round(hora_inicio + i * intervalo))
        minuto = random.choice(["00", "15", "30", "45"])
        horarios.append({"horas": str(hora).zfill(2), "minutos": minuto})
    return horarios

def gerar_preferencias_alimentares():
    prefs = {}
    for categoria in [str(i) for i in range(1, 8)]:
        alimentos = alimentos_categorizados[categoria]
        n = random.randint(3, 5)
        prefs[categoria] = random.sample([a["id_alimento"] for a in alimentos], n)
    return prefs

usuarios_mock = []

for i in range(20):
    # Sexo: 0-14 feminino, 15-19 masculino
    if i < 15:
        nome = f"{random.choice(nomes_femininos)} {random.choice(sobrenomes)}"
        sexo = "feminino"
    else:
        nome = f"{random.choice(nomes_masculinos)} {random.choice(sobrenomes)}"
        sexo = "masculino"

    telefone = "219" + "".join([str(random.randint(0,9)) for _ in range(8)])  # formato 2199xxxxxxx
    # Gera e-mail único para cada usuário
    email = "thaispaganinirj@exemplo.com"
    nutri_id = "nutri0001"
    paciente_id = f"pac{str(i+1).zfill(4)}"
    idade = str(random.randint(18, 45))
    altura = str(random.randint(150, 185))
    peso_atual = str(random.randint(50, 110))
    peso_desejado = str(int(peso_atual) - random.randint(5, 10))  # sempre 5 a 10 kg a menos

    imc = round(random.uniform(18.0, 38.0), 1)
    condicao = random.choice(condicoes_imc)
    objetivo = random.choice(objetivos)

    historico_saude = "Sim" if i < 15 else "Não"  # 15 sim, 5 não
    historico_medicamentos = "Sim" if random.random() < 0.25 else "Não"
    sono = random.choice(qualidade_sono)
    horas = random.choice(horas_sono)

    atv1 = random.choice(atividades)
    tempo1 = random.choice(tempos_atividade)
    atv2 = random.choice(atividades)
    tempo2 = random.choice(tempos_atividade)
    nivel_atv = random.choice(niveis_atividade)  # sempre baixo

    agua = random.choice(consumo_agua)
    n_refeicoes = random.choice(refeicoes_diarias)
    qtd_refeicoes = int(n_refeicoes.split()[0])
    horarios = gerar_horarios_refeicoes_ordenados(qtd_refeicoes)
    refeicoes_dict = {f"Refeição {j+1}": horarios[j] for j in range(qtd_refeicoes)}
    preferencias = gerar_preferencias_alimentares()

    usuario = {
        "telefone": telefone,
        "email": email,
        "nutri_id": nutri_id,
        "paciente_id": paciente_id,
        "nome": nome,
        "idade": idade,
        "altura": altura,
        "peso_atual": peso_atual,
        "peso_desejado": peso_desejado,
        "sexo": sexo,
        "imc": imc,
        "imc_condicao": condicao,
        "objetivo": objetivo,
        "Histórico de Saúde": historico_saude,
        "Histórico de Medicamentos": historico_medicamentos,
        "Qualidade Sono": sono,
        "horas sono": horas,
        "Atividade Física 1": atv1,
        "Tempo de Atividade": tempo1,
        "Atividade Física 2": atv2,
        "Tempo de Atividade 2": tempo2,
        "Nível de Atividade": nivel_atv,
        "Consumo de Água": agua,
        "Refeições Diárias": n_refeicoes,
        **refeicoes_dict,
        "pagamento_confirmado": False,
        "pagamento_status": "pendente",
        "external_reference": f"{nutri_id}_{paciente_id}",
        "valor_pago": 0.50
    }
    # Preferências alimentares
    usuario.update(preferencias)
    usuarios_mock.append(usuario)

# --- Exporta lista final de usuários para uso nos testes ---
# Você pode importar usuarios_mock em qualquer tela!
# Exemplo de uso:
#   from mockup_usuarios import usuarios_mock

# Para testar, descomente abaixo:
# print(json.dumps(usuarios_mock, indent=2, ensure_ascii=False))