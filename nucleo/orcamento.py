"""Cálculos de orçamento para quem tem renda variável ou informal."""
import math
from statistics import mean, pstdev


def renda_base(rendas, piores=3):
    """Média dos `piores` menores meses da lista de rendas (ex.: últimos 6 meses)."""
    if not rendas:
        raise ValueError("Informe ao menos um mês de renda.")
    menores = sorted(rendas)[:piores]
    return sum(menores) / len(menores)


def orcamento_50_30_20(renda):
    """Divide a renda em necessidades (50%), desejos (30%) e reserva/dívidas (20%)."""
    return {"necessidades": renda * 0.5, "desejos": renda * 0.3, "reserva_e_dividas": renda * 0.2}


def reserva_alvo(despesas_essenciais, meses):
    return despesas_essenciais * meses


def comprometimento(parcelas_mensais, renda):
    """Parte da renda base já comprometida com parcelas (0 a 1)."""
    return parcelas_mensais / renda if renda > 0 else float("inf")


def folga_mensal(renda, despesas_essenciais, parcelas_mensais):
    return renda - despesas_essenciais - parcelas_mensais


# ---------- renda variável: ferramentas além da regra 50/30/20 ----------

LIMITE_ESTAVEL = 0.15   # variação (desvio/média) abaixo disso: renda estável
LIMITE_MODERADA = 0.35  # abaixo disso: moderada; acima: alta (limites escolhidos pelo projeto)


def diagnostico_renda(rendas):
    """Resume o histórico de renda: média, menor, maior, variação e nível de oscilação."""
    if len(rendas) < 2:
        raise ValueError("Informe ao menos 2 meses de renda.")
    media = mean(rendas)
    variacao = pstdev(rendas) / media if media > 0 else float("inf")
    nivel = "estável" if variacao < LIMITE_ESTAVEL else "moderada" if variacao < LIMITE_MODERADA else "alta"
    return {"media": media, "minimo": min(rendas), "maximo": max(rendas),
            "variacao": variacao, "nivel": nivel}


def meses_reserva_sugeridos(nivel):
    """Meses de despesas essenciais sugeridos, dentro da faixa de 6 a 12 meses
    citada em guias de educação financeira para renda variável."""
    return {"estável": 6, "moderada": 9, "alta": 12}[nivel]


def retirada_maxima(rendas, colchao_inicial=0.0):
    """Maior 'salário fixo' que se consegue retirar todo mês, com base no histórico,
    sem que o colchão fique negativo em nenhum mês: min_k (C + soma dos k primeiros) / k."""
    acumulado, melhor = colchao_inicial, float("inf")
    for k, renda in enumerate(rendas, 1):
        acumulado += renda
        melhor = min(melhor, acumulado / k)
    return max(melhor, 0.0)


def simular_colchao(rendas, retirada, colchao_inicial=0.0):
    """Cada mês entra a renda e sai a retirada fixa. O que falta (saldo negativo)
    é contabilizado e o colchão volta a zero."""
    saldo, historico = colchao_inicial, []
    meses_faltou, total_faltou = 0, 0.0
    for renda in rendas:
        saldo += renda - retirada
        if saldo < -1e-9:
            meses_faltou += 1
            total_faltou += -saldo
            saldo = 0.0
        historico.append(saldo)
    return {"historico": historico, "meses_faltou": meses_faltou,
            "total_faltou": total_faltou, "sustenta": meses_faltou == 0}


def cascata(renda_mes, essenciais, parcelas, reserva_mensal):
    """Distribui a renda do mês por ordem de prioridade: essenciais, parcelas,
    reserva e, por último, o que sobra para o resto."""
    restante, resultado = max(renda_mes, 0.0), {}
    for nome, valor in (("essenciais", essenciais), ("parcelas", parcelas), ("reserva", reserva_mensal)):
        pago = min(restante, valor)
        resultado[nome] = pago
        resultado["falta_" + nome] = valor - pago
        restante -= pago
    resultado["livre"] = restante
    return resultado


def meses_para_atingir(meta, aporte_mensal):
    """Meses para juntar a meta guardando um valor fixo por mês (None se não guardar nada)."""
    return None if aporte_mensal <= 0 else math.ceil(meta / aporte_mensal)
