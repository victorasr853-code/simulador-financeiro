"""Interface web (Streamlit). Para rodar: streamlit run app.py"""
import streamlit as st

from nucleo.conteudo import DADOS, ETAPAS_BIRO, HABITOS, LEITURA_DOS_DADOS, PESOS_SCORE
from nucleo.dividas import parcela_price, simular_divida, taxa_implicita
from nucleo.orcamento import (cascata, comprometimento, diagnostico_renda, folga_mensal,
                              meses_para_atingir, meses_reserva_sugeridos, orcamento_50_30_20,
                              renda_base, reserva_alvo, retirada_maxima, simular_colchao)

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

def tela_orcamento():
    st.subheader("Orçamento para quem tem renda que varia")
    st.caption("Sem salário fixo, a regra 50/30/20 sozinha não basta: o que muda é como definir "
               "a renda do mês e como guardar nos meses bons para cobrir os ruins.")
    meses_txt = st.text_input("Quanto você recebeu em cada um dos últimos meses? (separe por vírgula; ideal: 6 a 12 meses)",
                              "1500, 2400, 900, 2000, 1200, 1800")
    custos = st.number_input("Custos do trabalho por mês, se houver (material, transporte, taxas) (R$)",
                             min_value=0.0, value=0.0, step=50.0)
    essenciais = st.number_input("Despesas essenciais por mês: moradia, comida, contas, transporte (R$)",
                                 min_value=0.0, value=1100.0, step=50.0)
    parcelas = st.number_input("Total de parcelas que você paga por mês (R$)", min_value=0.0, value=200.0, step=50.0)

    try:
        brutas = [float(x.replace(",", ".")) for x in meses_txt.replace(";", ",").split(",") if x.strip()]
        rendas = [r - custos for r in brutas]
        dg = diagnostico_renda(rendas)
    except ValueError:
        st.error("Digite pelo menos 2 meses, só números, separados por vírgula (use ponto nos centavos).")
        return

    etapa = st.radio("O que você quer ver?", ["1. Diagnóstico da renda", "2. Meu salário fixo",
                                              "3. Cascata de prioridades", "4. Reserva e proteção"])

    if etapa.startswith("1"):
        c1, c2, c3 = st.columns(3)
        c1.metric("Média por mês", real(dg["media"]))
        c2.metric("Pior mês", real(dg["minimo"]))
        c3.metric("Melhor mês", real(dg["maximo"]))
        st.write(f"Oscilação da renda: **{dg['nivel']}** (variação de {dg['variacao'] * 100:.0f}% em torno da média).")
        st.bar_chart(rendas)
        if dg["nivel"] != "estável":
            st.warning("Orçar pela média pode falhar nos meses fracos. Veja a aba 2, que mostra como transformar "
                       "uma renda que oscila em um valor fixo por mês.")
        base = renda_base(rendas)
        o = orcamento_50_30_20(base)
        st.write(f"Se você usar a regra 50/30/20 sobre a renda base ({real(base)}, média dos 3 piores meses): "
                 f"necessidades {real(o['necessidades'])}, desejos {real(o['desejos'])}, "
                 f"reserva e dívidas {real(o['reserva_e_dividas'])}.")
        comp = comprometimento(parcelas, base)
        st.write(f"As parcelas comprometem {comp * 100:.0f}% da renda base.")
        if comp > 0.30:
            st.warning("Acima de 30% da renda base (limite de referência, ajuste e cite a fonte).")

    elif etapa.startswith("2"):
        st.write("A ideia é **pagar a si mesmo um valor fixo todo mês**. Nos meses bons, o que sobra vai para um "
                 "colchão. Nos meses ruins, você usa o colchão e o valor continua o mesmo.")
        maxima = retirada_maxima(rendas)
        st.info(f"Com esse histórico, o maior valor fixo que você conseguiria retirar sem faltar em nenhum mês, "
                f"começando sem colchão, é **{real(maxima)}**.")
        retirada = st.number_input("Quanto você quer retirar por mês (R$)", min_value=0.0,
                                   value=float(int(maxima)), step=50.0)
        colchao0 = st.number_input("Colchão que você já tem hoje (R$)", min_value=0.0, value=0.0, step=100.0)
        r = simular_colchao(rendas, retirada, colchao0)
        st.line_chart(r["historico"])
        st.caption("Saldo do colchão ao final de cada mês.")
        if r["sustenta"]:
            st.success("Com esse valor fixo, o dinheiro não faltou em nenhum mês do histórico.")
        else:
            st.error(f"Faltou dinheiro em {r['meses_faltou']} mês(es), num total de {real(r['total_faltou'])}. "
                     "Reduza a retirada ou monte um colchão antes.")
        if retirada < essenciais:
            st.warning("Esse valor fixo é menor que suas despesas essenciais.")

    elif etapa.startswith("3"):
        st.write("Em vez de porcentagens fixas, o dinheiro que entra é distribuído **por ordem de prioridade**: "
                 "primeiro o essencial, depois as parcelas, depois a reserva, e só então o resto.")
        mes = st.number_input("Quanto entrou neste mês (R$)", min_value=0.0, value=float(max(dg["minimo"], 0)), step=50.0)
        reserva_mes = st.number_input("Quanto quer guardar por mês na reserva (R$)", min_value=0.0, value=100.0, step=50.0)
        c = cascata(mes, essenciais, parcelas, reserva_mes)
        st.write(f"1. Essenciais: {real(c['essenciais'])}")
        st.write(f"2. Parcelas: {real(c['parcelas'])}")
        st.write(f"3. Reserva: {real(c['reserva'])}")
        st.write(f"4. Livre para o resto: {real(c['livre'])}")
        if c["falta_essenciais"] > 0:
            st.error(f"Neste mês faltam {real(c['falta_essenciais'])} para cobrir o essencial. "
                     "Evite cobrir o buraco com rotativo ou cheque especial (veja a aba do simulador de dívida).")
        elif c["falta_parcelas"] > 0:
            st.warning(f"Faltam {real(c['falta_parcelas'])} para pagar as parcelas.")
        if mes > 0:
            st.caption(f"Neste mês, o essencial pesa {essenciais / mes * 100:.0f}% da renda. "
                       "Na regra 50/30/20, ele seria limitado a 50%.")

    else:
        meses_sug = meses_reserva_sugeridos(dg["nivel"])
        meses_res = st.slider("Meses de despesas essenciais que você quer ter guardados", 3, 12, meses_sug)
        meta = reserva_alvo(essenciais, meses_res)
        st.metric("Meta da reserva", real(meta))
        st.caption("Guias de educação financeira costumam indicar de 6 a 12 meses para renda variável, "
                   "contra 3 a 6 para quem tem salário fixo. Cite fontes oficiais no TCC.")
        aporte = st.number_input("Quanto você consegue guardar por mês (R$)", min_value=0.0, value=100.0, step=50.0)
        n = meses_para_atingir(meta, aporte)
        st.write("Guardando esse valor, você leva " + (f"cerca de {n} meses." if n else "um tempo indeterminado (aporte zero)."))
        st.markdown("**Outros cuidados para quem trabalha por conta própria**")
        st.write("- Separe o dinheiro da casa do dinheiro do trabalho.")
        st.write("- Reserve uma parte de cada recebimento antes de gastar (reserva e previdência).")
        st.write("- Sem contribuição à previdência, você fica sem proteção como auxílio por doença. "
                 "No MEI, a contribuição previdenciária já vem incluída na guia mensal.")
        st.write("- Fuja de crédito caro para cobrir mês fraco: use o simulador de dívida antes de contratar.")


with aba3:
    tela_orcamento()

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
