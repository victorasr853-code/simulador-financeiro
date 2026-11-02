"""Simulador de Bola de Neve – interface (Streamlit). Para rodar: streamlit run app.py"""
import streamlit as st
import streamlit.components.v1 as components

from nucleo.conteudo import DADOS, ETAPAS_BIRO, HABITOS, LEITURA_DOS_DADOS, PESOS_SCORE
from nucleo.dividas import simular_divida, taxa_implicita
from nucleo.orcamento import (cascata, comprometimento, diagnostico_renda, meses_para_atingir,
                              meses_reserva_sugeridos, orcamento_50_30_20, renda_base,
                              reserva_alvo, retirada_maxima, simular_colchao)

st.set_page_config(page_title="Simulador de Bola de Neve", page_icon="⛄", layout="centered")

CSS = """
<style>
.block-container { max-width: 920px; padding-top: 1.6rem; }
.hero { padding: 1.5rem 1.7rem; border-radius: 20px; margin-bottom: 1.2rem; color: #fff;
        background: linear-gradient(135deg, #1b4b8f 0%, #2b7bc4 60%, #7cc4ee 100%); }
.hero h1 { margin: 0; font-size: 2.1rem; color: #fff; padding: 0; }
.hero p { margin: .4rem 0 0; font-size: 1.02rem; opacity: .95; }
.card { border-radius: 14px; padding: .85rem 1rem; margin-bottom: .6rem;
        border: 1px solid rgba(120,140,170,.28); background: rgba(43,123,196,.08); }
.card .t { font-size: .82rem; opacity: .8; }
.card .v { font-size: 1.55rem; font-weight: 700; line-height: 1.25; }
.card .l { font-size: .8rem; opacity: .75; }
.card.good { background: rgba(16,185,129,.12); border-color: rgba(16,185,129,.45); }
.card.bad  { background: rgba(220,60,60,.10);  border-color: rgba(220,60,60,.45); }
.card.warn { background: rgba(245,158,11,.12); border-color: rgba(245,158,11,.5); }
.card.azul  { border-left: 7px solid #2563eb; }
.card.ambar { border-left: 7px solid #f59e0b; }
.card.verde { border-left: 7px solid #10b981; }
.bar { display: flex; height: 38px; border-radius: 12px; overflow: hidden; margin: .3rem 0 .9rem; }
.bar div { display: flex; align-items: center; justify-content: center; color: #fff;
           font-weight: 700; font-size: .9rem; }
.passo { display: flex; gap: .8rem; align-items: center; padding: .6rem .9rem; margin-bottom: .45rem;
         border-radius: 12px; border: 1px solid rgba(120,140,170,.25); background: rgba(43,123,196,.06); }
.passo .n { flex: 0 0 2rem; height: 2rem; border-radius: 50%; display: flex; align-items: center;
            justify-content: center; font-weight: 700; color: #fff; background: #2b7bc4; }
.stTabs [data-baseweb="tab-list"] { gap: .3rem; flex-wrap: wrap; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: .5rem .8rem; }
.rodape { font-size: .8rem; opacity: .7; text-align: center; margin-top: 2rem; }
</style>
"""


def idioma_pt():
    """Avisa ao navegador que a página está em português, para o tradutor automático
    do Chrome não bagunçar os textos."""
    components.html(
        "<script>try{const d=window.parent.document;d.documentElement.lang='pt-BR';"
        "if(!d.querySelector('meta[name=google]')){const m=d.createElement('meta');"
        "m.name='google';m.content='notranslate';d.head.appendChild(m);}}catch(e){}</script>",
        height=0)


def real(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def card(titulo, valor, legenda="", tom=""):
    return (f'<div class="card {tom}"><div class="t">{titulo}</div>'
            f'<div class="v">{valor}</div><div class="l">{legenda}</div></div>')


def cards(*itens):
    colunas = st.columns(len(itens))
    for coluna, item in zip(colunas, itens):
        coluna.markdown(card(*item), unsafe_allow_html=True)


def passo(n, texto):
    st.markdown(f'<div class="passo"><div class="n">{n}</div><div>{texto}</div></div>',
                unsafe_allow_html=True)


def bloco_regra_50_30_20(base, essenciais):
    """Visual da regra 50/30/20 sobre a renda base, comparando com os essenciais reais."""
    o = orcamento_50_30_20(base)
    st.markdown("#### Regra 50/30/20 sobre a sua renda base")
    st.caption(f"Renda base: {real(base)} (média dos 3 piores meses). A regra divide esse valor em três partes.")
    partes = [(50, "#2563eb"), (30, "#f59e0b"), (20, "#10b981")]
    barra = "".join(f'<div style="width:{p}%;background:{c}">{p}%</div>' for p, c in partes)
    st.markdown(f'<div class="bar">{barra}</div>', unsafe_allow_html=True)
    cards(("Necessidades", real(o["necessidades"]), "moradia, comida, contas, transporte", "azul"),
          ("Desejos", real(o["desejos"]), "lazer, compras, o que dá prazer", "ambar"),
          ("Reserva e dívidas", real(o["reserva_e_dividas"]), "guardar e pagar parcelas", "verde"))
    pct = essenciais / base * 100 if base > 0 else float("inf")
    tom = "good" if pct <= 50 else "bad"
    msg = ("dentro do limite da regra." if pct <= 50 else
           "acima do limite de 50%. Com renda que varia, a regra sozinha não fecha: veja as próximas etapas.")
    st.markdown(card("Seus essenciais comparados à regra", f"{pct:.0f}% da renda base",
                     f"O limite para necessidades é 50%: você está {msg}", tom), unsafe_allow_html=True)


# ---------------------------------------------------------------- abas

def tela_divida():
    st.subheader("Como uma dívida cresce (ou não)")
    st.caption("Informe a dívida e quanto você consegue pagar. O simulador mostra, mês a mês, o que acontece.")
    c1, c2 = st.columns(2)
    tipo = c1.selectbox("Tipo de dívida", ["Cartão rotativo", "Cheque especial", "Empréstimo pessoal"])
    saldo = c2.number_input("Valor da dívida (R$)", min_value=0.0, value=1000.0, step=100.0)
    # Valor de exemplo. Substituir pelas taxas médias do Banco Central (citar a data).
    taxa = st.number_input(f"Juros ao mês (%) – {tipo} (valor de exemplo, edite)",
                           min_value=0.0, value=8.0, step=0.5) / 100
    c3, c4, c5 = st.columns(3)
    bom = c3.number_input("Pagamento em mês bom (R$)", min_value=0.0, value=300.0, step=50.0)
    ruim = c4.number_input("Pagamento em mês ruim (R$)", min_value=0.0, value=0.0, step=50.0)
    n_ruins = c5.slider("Meses ruins a cada 6", 0, 5, 0)

    if st.button("Simular", key="sim", type="primary"):
        r = simular_divida(saldo, taxa, [bom] * (6 - n_ruins) + [ruim] * n_ruins)
        if r["quitou"]:
            st.markdown(card("Resultado", f"Dívida quitada em {r['meses']} meses", "", "good"), unsafe_allow_html=True)
        else:
            st.markdown(card("Resultado", "A dívida não acaba",
                             "Com esses valores ela cresce ou nunca zera (limite de 50 anos).", "bad"),
                        unsafe_allow_html=True)
        if r["nao_cobre_juros"]:
            st.warning("Em algum mês o pagamento não cobre nem os juros: a dívida cresce.")
        pct_juros = r["total_juros"] / r["total_pago"] * 100 if r["total_pago"] > 0 else 0
        cards(("Total pago", real(r["total_pago"]), ""),
              ("Só de juros", real(r["total_juros"]), ""),
              ("Juros no que você pagou", f"{pct_juros:.0f}%", "de cada R$ 100 pagos, quanto foi juro"))
        st.line_chart(r["historico"])
        st.caption("Evolução do saldo devedor mês a mês.")


def tela_oferta():
    st.subheader("Quanto custa de verdade essa oferta?")
    st.caption("Olhe o custo total, não só se a parcela cabe no bolso.")
    c1, c2, c3 = st.columns(3)
    valor = c1.number_input("Valor que você recebe (R$)", min_value=1.0, value=2000.0, step=100.0)
    parcela = c2.number_input("Valor de cada parcela (R$)", min_value=1.0, value=250.0, step=10.0)
    n = c3.number_input("Número de parcelas", min_value=1, value=12, step=1)
    if st.button("Calcular", key="oferta", type="primary"):
        i = taxa_implicita(valor, parcela, int(n))
        total = parcela * n
        cards(("Juros embutidos", f"{i * 100:.2f}% ao mês", "taxa implícita da oferta", "warn"),
              ("Total que você vai pagar", real(total), ""),
              ("Só de juros", real(total - valor), ""))


def tela_orcamento():
    st.subheader("Orçamento para quem tem renda que varia")
    st.caption("Sem salário fixo, a regra 50/30/20 sozinha não basta: o que muda é como definir a renda do mês "
               "e como guardar nos meses bons para cobrir os ruins.")
    meses_txt = st.text_input("Quanto você recebeu em cada um dos últimos meses? (separe por vírgula; ideal: 6 a 12 meses)",
                              "1500, 2400, 900, 2000, 1200, 1800")
    c1, c2, c3 = st.columns(3)
    custos = c1.number_input("Custos do trabalho por mês (R$)", min_value=0.0, value=0.0, step=50.0,
                             help="Material, transporte, taxas. É descontado de cada mês.")
    essenciais = c2.number_input("Despesas essenciais por mês (R$)", min_value=0.0, value=1100.0, step=50.0,
                                 help="Moradia, comida, contas, transporte.")
    parcelas = c3.number_input("Parcelas por mês (R$)", min_value=0.0, value=200.0, step=50.0)

    try:
        brutas = [float(x.replace(",", ".")) for x in meses_txt.replace(";", ",").split(",") if x.strip()]
        rendas = [r - custos for r in brutas]
        dg = diagnostico_renda(rendas)
    except ValueError:
        st.error("Digite pelo menos 2 meses, só números, separados por vírgula (use ponto nos centavos).")
        return

    etapa = st.radio("O que você quer ver?", ["1. Diagnóstico", "2. Salário fixo", "3. Prioridades", "4. Reserva"],
                     horizontal=True)

    if etapa.startswith("1"):
        cards(("Média por mês", real(dg["media"]), ""), ("Pior mês", real(dg["minimo"]), "", "bad"),
              ("Melhor mês", real(dg["maximo"]), "", "good"))
        tom = {"estável": "good", "moderada": "warn", "alta": "bad"}[dg["nivel"]]
        st.markdown(card("Oscilação da sua renda", dg["nivel"].capitalize(),
                         f"variação de {dg['variacao'] * 100:.0f}% em torno da média", tom), unsafe_allow_html=True)
        st.bar_chart(rendas)
        if dg["nivel"] != "estável":
            st.warning("Orçar pela média pode falhar nos meses fracos. Veja a etapa 2, que transforma uma renda "
                       "que oscila em um valor fixo por mês.")
        base = renda_base(rendas)
        bloco_regra_50_30_20(base, essenciais)
        comp = comprometimento(parcelas, base)
        tom = "bad" if comp > 0.30 else "good"
        st.markdown(card("Parcelas sobre a renda base", f"{comp * 100:.0f}%",
                         "Referência usada: até 30% (ajuste e cite a fonte).", tom), unsafe_allow_html=True)

    elif etapa.startswith("2"):
        st.write("A ideia é **pagar a si mesmo um valor fixo todo mês**. Nos meses bons, o que sobra vai para um "
                 "colchão. Nos meses ruins, você usa o colchão e o valor continua o mesmo.")
        maxima = retirada_maxima(rendas)
        st.markdown(card("Maior valor fixo possível com esse histórico", real(maxima),
                         "sem faltar em nenhum mês, começando sem colchão", "azul"), unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        retirada = c1.number_input("Quanto quer retirar por mês (R$)", min_value=0.0, value=float(int(maxima)), step=50.0)
        colchao0 = c2.number_input("Colchão que você já tem (R$)", min_value=0.0, value=0.0, step=100.0)
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
        c1, c2 = st.columns(2)
        mes = c1.number_input("Quanto entrou neste mês (R$)", min_value=0.0, value=float(max(dg["minimo"], 0)), step=50.0)
        reserva_mes = c2.number_input("Quanto quer guardar na reserva (R$)", min_value=0.0, value=100.0, step=50.0)
        c = cascata(mes, essenciais, parcelas, reserva_mes)
        passo(1, f"Essenciais: <b>{real(c['essenciais'])}</b>")
        passo(2, f"Parcelas: <b>{real(c['parcelas'])}</b>")
        passo(3, f"Reserva: <b>{real(c['reserva'])}</b>")
        passo(4, f"Livre para o resto: <b>{real(c['livre'])}</b>")
        if c["falta_essenciais"] > 0:
            st.error(f"Neste mês faltam {real(c['falta_essenciais'])} para cobrir o essencial. "
                     "Evite cobrir o buraco com rotativo ou cheque especial (veja o simulador de dívida).")
        elif c["falta_parcelas"] > 0:
            st.warning(f"Faltam {real(c['falta_parcelas'])} para pagar as parcelas.")
        if mes > 0:
            st.caption(f"Neste mês, o essencial pesa {essenciais / mes * 100:.0f}% da renda. "
                       "Na regra 50/30/20, ele seria limitado a 50%.")

    else:
        meses_sug = meses_reserva_sugeridos(dg["nivel"])
        meses_res = st.slider("Meses de despesas essenciais que você quer ter guardados", 3, 12, meses_sug)
        meta = reserva_alvo(essenciais, meses_res)
        aporte = st.number_input("Quanto você consegue guardar por mês (R$)", min_value=0.0, value=100.0, step=50.0)
        n = meses_para_atingir(meta, aporte)
        cards(("Meta da reserva", real(meta), f"{meses_res} meses de essenciais", "azul"),
              ("Tempo para chegar lá", f"{n} meses" if n else "indefinido", "guardando o valor informado"))
        st.caption("Guias de educação financeira costumam indicar de 6 a 12 meses para renda variável, contra 3 a 6 "
                   "para quem tem salário fixo. Cite fontes oficiais no TCC.")
        st.markdown("**Outros cuidados para quem trabalha por conta própria**")
        passo("✓", "Separe o dinheiro da casa do dinheiro do trabalho.")
        passo("✓", "Reserve uma parte de cada recebimento antes de gastar (reserva e previdência).")
        passo("✓", "Sem contribuição à previdência, você fica sem proteção como o auxílio por doença. "
                   "No MEI, a contribuição previdenciária já vem incluída na guia mensal.")
        passo("✓", "Fuja de crédito caro para cobrir mês fraco: use o simulador de dívida antes de contratar.")


def tela_biros():
    st.subheader("Como os birôs de crédito e o score funcionam")
    for k, etapa in enumerate(ETAPAS_BIRO, 1):
        passo(k, etapa)
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


def tela_dados():
    st.subheader("Por que este projeto importa")
    st.dataframe([{"Indicador": a, "Valor": b, "Fonte": c, "Período": d} for a, b, c, d in DADOS],
                 hide_index=True)
    st.info(LEITURA_DOS_DADOS)
    st.caption("Dados consultados em outubro de 2026. Confira nas fontes primárias antes de citar.")


# ---------------------------------------------------------------- página

idioma_pt()
st.markdown(CSS, unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>⛄ Simulador de Bola de Neve</h1>'
            '<p>Veja como uma dívida cresce, avalie ofertas de crédito e organize o orçamento '
            'quando a renda varia de mês para mês.</p></div>', unsafe_allow_html=True)

aba1, aba2, aba3, aba4, aba5 = st.tabs(["📉 Dívida", "💳 Oferta", "💰 Orçamento", "🔎 Birôs e score", "📊 Dados"])
with aba1:
    tela_divida()
with aba2:
    tela_oferta()
with aba3:
    tela_orcamento()
with aba4:
    tela_biros()
with aba5:
    tela_dados()

st.markdown('<div class="rodape">Ferramenta educativa, sem recomendação financeira personalizada. '
            'O que você digita aqui não é gravado.</div>', unsafe_allow_html=True)
