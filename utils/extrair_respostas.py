# app/utils/extrair_respostas.py

def extrair_respostas(payload):
    """
    Extrai o dicionário de respostas do JSON recebido do Firebase,
    independente do nível de aninhamento. 
    Se já estiver 'flat', retorna como está.
    Lança ValueError se não encontrar.
    """
    # Caso já seja dict 'flat'
    if isinstance(payload, dict) and "nome" in payload and "idade" in payload:
        return payload
    # Se for o padrão Firebase aninhado
    if isinstance(payload, dict):
        for nutri in payload.values():
            if isinstance(nutri, dict):
                for pac in nutri.values():
                    if isinstance(pac, dict) and "respostas" in pac:
                        return pac["respostas"]
    # Se não encontrou
    raise ValueError("Formato de payload inválido para extração de respostas.")
