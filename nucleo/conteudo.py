"""Conteúdo educativo e dados de justificativa (com fonte). Conferir as fontes primárias antes de citar no TCC."""

# (indicador, valor, fonte, período)
DADOS = [
    ("Taxa de informalidade, 18 a 29 anos", "37,4% (30 a 59 anos: 34,8%)", "IBGE, PNAD Contínua", "2º tri 2026"),
    ("Taxa de informalidade, 18 a 24 anos", "39,4%", "MTE/SEET, com dados da PNAD Contínua", "1º tri 2026"),
    ("Desemprego, 18 a 29 anos", "9,2% (30 a 59 anos: 3,8%)", "IBGE, PNAD Contínua", "2º tri 2026"),
    ("Ficam menos de 1 ano no mesmo trabalho", "38,2% (18 a 24 anos); 25,3% (25 a 29 anos)", "MTE/SEET", "1º tri 2026"),
    ("Brasileiros inadimplentes", "81,7 milhões, com 332 milhões de dívidas", "Serasa, Mapa da Inadimplência", "fev/2026"),
    ("Inadimplentes que ganham até 1 salário mínimo", "48%", "Serasa, Mapa da Inadimplência", "2026"),
    ("Inadimplentes que já estavam nessa condição há 10 anos", "42%", "Serasa, Mapa da Inadimplência", "2026"),
    ("Participação de 18 a 25 anos entre os inadimplentes", "15,93% (2016) para 11,45% (2026)", "Serasa, Mapa da Inadimplência", "2016-2026"),
    ("Jovens de 18 a 25 anos que negociaram dívidas", "alta de 49% (jan-jul 2025 contra 2024)", "Serasa Limpa Nome", "2025"),
    ("Jovens de 18 a 29 anos que arcam sozinhos com os gastos", "55% (e 39% ajudam nas despesas da casa)", "Pesquisa Serasa/Opinion Box, 2.923 jovens", "jul/2024"),
    ("Jovens do Nordeste (18 a 29 anos) que arcam sozinhos com os gastos", "59,3% (e 35,6% ajudam nas contas de casa)", "Pesquisa Serasa/Opinion Box", "jul/2024"),
    ("Negociações de dívida de jovens de 18 a 25 anos: Bahia e Paraíba", "alta de 62,1% e de 56,6% (Brasil: 49%)", "Serasa Limpa Nome", "jan-jul 2025"),
    ("Informalidade nos estados do Nordeste", "todos acima da média nacional (37,8%); Maranhão 56,2% e Bahia 52,3%", "IBGE, PNAD Contínua", "2º e 3º tri 2025"),
]

LEITURA_DOS_DADOS = (
    "Os dados da Serasa mostram que os jovens de 18 a 25 anos estão entre os menos inadimplentes, "
    "e a participação deles caiu em dez anos. O argumento do trabalho se apoia em outros pontos: "
    "a informalidade é maior entre os jovens do que entre os adultos, a renda é instável, eles assumem "
    "gastos cedo e as negociações de dívida entre eles crescem. A ligação direta entre informalidade e "
    "desinformação financeira é uma hipótese do trabalho, a ser testada com o questionário. No Nordeste, a informalidade "
    "é maior e mais jovens já sustentam os próprios gastos, o que reforça a hipótese para a região."
)

ETAPAS_BIRO = [
    "Você paga ou atrasa uma conta (loja, banco, cartão, conta de consumo).",
    "A empresa credora informa o birô. Quem decide negativar é o credor, não o birô.",
    "O birô junta dados de várias fontes (bancos, lojas, concessionárias e fontes públicas).",
    "Cada birô calcula o seu score com critérios próprios (Serasa, Boa Vista, SPC e Quod).",
    "Quando você pede crédito, a empresa consulta o birô, e a consulta fica registrada.",
    "A empresa decide aprovar, negar ou ofertar, e define limite e juros pela política dela.",
]

# Pesos oficiais do Serasa Score (Serasa, página "Mitos e verdades"). Os demais fatores têm peso menor.
PESOS_SCORE = {
    "Pagamentos em dia": 29,
    "Tempo de relacionamento com o crédito": 24,
    "Dívidas negativadas": 21,
}

# hábito: (efeito, explicação)
HABITOS = {
    "Pagar as contas em dia": ("sobe", "Melhora o histórico de pagamentos, o fator de maior peso."),
    "Atrasar uma conta e ser negativado": ("desce", "Pesa nas dívidas negativadas e no histórico de pagamentos."),
    "Manter crédito ativo e bem pago por anos": ("sobe", "Aumenta o tempo de relacionamento com o mercado de crédito."),
    "Pedir crédito em várias lojas na mesma semana": ("desce", "Muitas buscas por crédito em pouco tempo pesam contra."),
    "Manter o cadastro atualizado": ("sobe", "Os dados cadastrais entram no cálculo, com peso menor."),
    "Ter uma renda maior": ("neutro", "A Serasa classifica como mito que a renda maior aumenta o score."),
    "Colocar o CPF na nota fiscal": ("neutro", "Não entra no cálculo do score."),
}
