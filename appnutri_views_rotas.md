# AppNutri — Views e Rotas detectadas

As views originais devem existir 1:1. Abaixo, lista de views e rotas chamadas por arquivo.

## Views (arquivos em `frontend/app/views/`)

- `agradecimento`
- `agua_alimentacao`
- `boas_vindas`
- `dados_pessoais`
- `exercicios`
- `habitos_alimentares`
- `imc_usuario`
- `landing`
- `mockup_usuarios`
- `preferencias_alimentares`
- `redirect_ticket`
- `saude_sono`
- `selecionar_alimentos`
- `testes`

## Rotas detectadas (page.go)

- `/`
- `/agua_alimentacao`
- `/app`
- `/dados_pessoais`
- `/exercicios`
- `/habitos_alimentares`
- `/imc_usuario`
- `/preferencias_alimentares`
- `/saude_sono`

## Navegação por origem (arquivo → rotas chamadas)

- `frontend/app/views/agua_alimentacao.py` → /habitos_alimentares
- `frontend/app/views/boas_vindas.py` → /dados_pessoais
- `frontend/app/views/dados_pessoais.py` → /imc_usuario
- `frontend/app/views/exercicios.py` → /agua_alimentacao
- `frontend/app/views/habitos_alimentares.py` → /preferencias_alimentares
- `frontend/app/views/imc_usuario.py` → /saude_sono
- `frontend/app/views/saude_sono.py` → /exercicios
- `frontend/app/views/selecionar_alimentos.py` → /preferencias_alimentares
- `frontend/main.py` → /, /app