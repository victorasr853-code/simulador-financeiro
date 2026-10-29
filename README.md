# Simulador de dívidas e orçamento (TCC)

Projeto 100% em Python, com interface em Streamlit.

## Como rodar
```
python -m venv venv
venv\Scripts\activate        # Windows (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

## Testes dos cálculos
```
python -m unittest discover -s testes -v
```

## Estrutura
- `nucleo/dividas.py`: simulação da dívida mês a mês, Tabela Price e taxa implícita da oferta.
- `nucleo/orcamento.py`: renda base, regra 50/30/20, reserva, comprometimento e folga.
- `testes/`: testes automatizados do núcleo (usar no capítulo de testes do TCC).
- `app.py`: telas (simulador, avaliador de oferta, orçamento).

## Próximos passos
1. Trocar as taxas de exemplo pelas médias do Banco Central (com a data).
2. Conferir os resultados com uma calculadora oficial.
3. Adicionar a aba de conteúdo educativo (o que o score vê e não vê).
4. Questionário pré e pós-teste e validação com 10 a 15 pessoas.
