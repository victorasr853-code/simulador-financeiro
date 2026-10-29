"""Cálculos de dívida: simulação mês a mês, Tabela Price e taxa implícita."""


def parcela_price(valor, taxa_mensal, n_parcelas):
    """Parcela fixa (Tabela Price): PMT = PV * i / (1 - (1 + i) ** -n)."""
    if taxa_mensal == 0:
        return valor / n_parcelas
    return valor * taxa_mensal / (1 - (1 + taxa_mensal) ** -n_parcelas)


def taxa_implicita(valor, parcela, n_parcelas):
    """Taxa mensal embutida numa oferta (valor recebido, parcela e nº de parcelas)."""
    if parcela * n_parcelas <= valor:
        return 0.0
    baixo, alto = 0.0, 1.0
    for _ in range(100):
        i = (baixo + alto) / 2
        valor_calc = parcela * (1 - (1 + i) ** -n_parcelas) / i
        if valor_calc > valor:
            baixo = i
        else:
            alto = i
    return i


def simular_divida(saldo, taxa_mensal, pagamentos, max_meses=600):
    """Simula uma dívida mês a mês: S(t+1) = S(t) * (1 + i) - P(t).

    `pagamentos` é um número (pagamento fixo) ou uma lista que se repete
    ciclicamente, útil para renda irregular, ex.: [300, 300, 0, 300].
    """
    ciclo = [pagamentos] if isinstance(pagamentos, (int, float)) else list(pagamentos)
    historico = [saldo]
    total_pago = total_juros = 0.0
    for mes in range(max_meses):
        if saldo <= 0.01:
            break
        juros = saldo * taxa_mensal
        pago = min(ciclo[mes % len(ciclo)], saldo + juros)
        saldo = saldo + juros - pago
        total_pago += pago
        total_juros += juros
        historico.append(saldo)
    quitou = saldo <= 0.01
    return {
        "quitou": quitou,
        "meses": len(historico) - 1,
        "total_pago": total_pago,
        "total_juros": total_juros,
        "historico": historico,
        "nao_cobre_juros": min(ciclo) < historico[0] * taxa_mensal,
    }
