"""Interface web (Streamlit). Para rodar: streamlit run app.py"""
import streamlit as st

from nucleo.conteudo import DADOS, ETAPAS_BIRO, HABITOS, LEITURA_DOS_DADOS, PESOS_SCORE
from nucleo.dividas import parcela_price, simular_divida, taxa_implicita
from nucleo.orcamento import (comprometimento, folga_mensal, orcamento_50_30_20,
                              renda_base, reserva_alvo)

st.set_page_config(page_title="Simulador de dívidas e orçamento", page_icon="💰")
st.title("Simulador de dívidas e orçamento")
st.caption("Ferramenta educativa. Não é recomendação financeira personalizada.")


def real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


aba1, aba2, aba3, aba4, aba5 = st.tabs(["Simulador de dívida", "Avaliar oferta de crédito", "Meu orçamento",
                                      "Birôs e score", "Dados e justificativa"])

with aba1:
    st.subheader("Como uma dívida cresce (ou não)")
    tipo = st.selectbox("Tipo de dívida", ["Cartão rotativo", "Cheque especial", "Empréstimo pessoal"])
    # Valores de exemplo. Substituir pelas taxas médias do Banco Central (citar a data).
    saldo = st.number_input("Valor da dívida (R$)", min_value=0.0, value=1000.0, step=100.0)
    taxa = st.number_input(f"Juros ao mês (%) – {tipo} (valor de exemplo, edite)", min_value=0.0, value=8.0, step=0.5) / 100
    bom = st.number_input("Quanto você paga num mês bom (R$)", min_value=0.0, value=300.0, step=50.0)
    ruim = st.number_input("Quanto você paga num mês ruim (R$)", min_value=0.0, value=0.0, step=50.0)
    n_ruins = st.slider("Meses ruins a cada 6", 0, 5, 0)

    if st.button("Simular", key="sim"):
        ciclo = [bom] * (6 - n_ruins) + [ruim] * n_ruins
        r = simular_divida(saldo, taxa, ciclo)
        if r["nao_cobre_juros"]:
            st.warning("Em algum mês o pagamento não cobre nem os juros: a dívida cresce.")
        if r["quitou"]:
            st.success(f"Dívida quitada em {r['meses']} meses.")
        else:
            st.error("Com esses valores a dívida não acaba (ou passa de 50 anos).")
        c1, c2 = st.columns(2)
        c1.metric("Total pago", real(r["total_pago"]))
        c2.metric("Só de juros", real(r["total_juros"]))
        st.line_chart(r["historico"])
        st.caption("Evolução do saldo devedor mês a mês.")

with aba2:
    st.subheader("Quanto custa de verdade essa oferta?")
    valor = st.number_input("Valor que você recebe (R$)", min_value=1.0, value=2000.0, step=100.0)
    parcela = st.number_input("Valor de cada parcela (R$)", min_value=1.0, value=250.0, step=10.0)
    n = st.number_input("Número de parcelas", min_value=1, value=12, step=1)
    if st.button("Calcular", key="oferta"):
        i = taxa_implicita(valor, parcela, int(n))
        total = parcela * n
        st.metric("Juros embutidos ao mês", f"{i * 100:.2f}%")
        c1, c2 = st.columns(2)
        c1.metric("Total que você vai pagar", real(total))
        c2.metric("Só de juros", real(total - valor))
        st.info("Olhe o total pago, não só se a parcela cabe no bolso.")

with aba3:
    st.subheader("Orçamento para renda que varia")
    meses = st.text_input("Sua renda nos últimos 6 meses (separe por vírgula)", "1500, 2400, 900, 2000, 1200, 1800")
    essenciais = st.number_input("Despesas essenciais por mês (R$)", min_value=0.0, value=1100.0, step=50.0)
    parcelas = st.number_input("Total de parcelas que você paga por mês (R$)", min_value=0.0, value=200.0, step=50.0)
    meses_reserva = st.slider("Meses de reserva que você quer ter", 3, 12, 6)
    if st.button("Calcular orçamento", key="orc"):
        try:
            rendas = [float(x.replace(",", ".")) for x in meses.replace(";", ",").split(",") if x.strip()]
            base = renda_base(rendas)
        except ValueError:
            st.error("Digite só números, separados por vírgula (use ponto nos centavos).")
        else:
            st.metric("Renda base (média dos 3 piores meses)", real(base))
            o = orcamento_50_30_20(base)
            st.write(f"Regra 50/30/20: necessidades {real(o['necessidades'])}, "
                     f"desejos {real(o['desejos'])}, reserva e dívidas {real(o['reserva_e_dividas'])}.")
            comp = comprometimento(parcelas, base)
            st.write(f"Parcelas comprometem {comp * 100:.0f}% da renda base.")
            if comp > 0.30:
                st.warning("Acima de 30% da renda base (limite de referência, ajuste e cite a fonte).")
            f = folga_mensal(base, essenciais, parcelas)
            (st.success if f >= 0 else st.error)(f"Folga mensal no pior cenário: {real(f)}")
            st.write(f"Reserva-alvo: {real(reserva_alvo(essenciais, meses_reserva))}.")

with aba4:
    st.subheader("Como os birôs de crédito e o score funcionam")
    for k, etapa in enumerate(ETAPAS_BIRO, 1):
        st.write(f"**{k}.** {etapa}")
    st.markdown("**O que mais pesa no Serasa Score (%)**")
    st.bar_chart(PESOS_SCORE)
    st.caption("Fonte: Serasa, página Mitos e verdades sobre o Serasa Score. Os pesos mudam com o modelo.")
    st.markdown("**Teste um hábito**")
    escolha = st.selectbox("O que você faria?", list(HABITOS))
    efeito, texto = HABITOS[escolha]
    {"sobe": st.success, "desce": st.error, "neutro": st.info}[efeito](
        {"sobe": "Tende a ajudar. ", "desce": "Tende a prejudicar. ", "neutro": "Não muda o score. "}[efeito] + texto)
    st.warning("O score mede a chance de você pagar, não se o crédito é bom para você. "
               "Uma oferta aprovada não significa que a parcela cabe na sua pior renda do mês.")

with aba5:
    st.subheader("Por que este projeto importa")
    st.dataframe([{"Indicador": a, "Valor": b, "Fonte": c, "Período": d} for a, b, c, d in DADOS],
                 hide_index=True)
    st.info(LEITURA_DOS_DADOS)
    st.caption("Dados consultados em outubro de 2026. Confira nas fontes primárias antes de citar.")
