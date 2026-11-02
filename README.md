# Simulador de Bola de Neve (TCC)

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
- `nucleo/orcamento.py`: renda base, regra 50/30/20, reserva, comprometimento, folga e, para renda variável, diagnóstico da renda, salário fixo com colchão, cascata de prioridades e prazo da reserva.
- `testes/`: testes automatizados do núcleo (usar no capítulo de testes do TCC).
- `nucleo/conteudo.py`: dados com fonte e conteúdo educativo (birôs, score, hábitos).
- `app.py`: telas do Simulador de Bola de Neve (dívida, oferta, orçamento, birôs e score, dados) e o visual da página.
- `.streamlit/config.toml`: cores do tema (se essa pasta não subir para o GitHub, o app funciona igual, só com o tema padrão).

## Próximos passos
1. Trocar as taxas de exemplo pelas médias do Banco Central (com a data).
2. Conferir os resultados com uma calculadora oficial.
3. Adicionar a aba de conteúdo educativo (o que o score vê e não vê).
4. Questionário pré e pós-teste e validação com 10 a 15 pessoas.
