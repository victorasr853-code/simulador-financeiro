"""Cálculos de orçamento para quem tem renda variável ou informal."""


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
