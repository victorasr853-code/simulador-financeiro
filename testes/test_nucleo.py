import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nucleo.dividas import parcela_price, simular_divida, taxa_implicita
from nucleo.orcamento import (cascata, comprometimento, diagnostico_renda, folga_mensal,
                              meses_para_atingir, meses_reserva_sugeridos, orcamento_50_30_20,
                              renda_base, reserva_alvo, retirada_maxima, simular_colchao)


class TestDividas(unittest.TestCase):
    def test_quita_com_pagamento_suficiente(self):
        r = simular_divida(1000, 0.05, 200)
        self.assertTrue(r["quitou"])
        self.assertLess(r["meses"], 10)
        self.assertAlmostEqual(r["total_pago"] - r["total_juros"], 1000, places=2)

    def test_nao_quita_se_pagamento_igual_aos_juros(self):
        r = simular_divida(1000, 0.10, 100, max_meses=60)
        self.assertFalse(r["quitou"])
        self.assertTrue(r["nao_cobre_juros"] or r["historico"][-1] >= 1000 - 0.01)

    def test_renda_irregular_demora_mais(self):
        fixo = simular_divida(1000, 0.05, 200)
        irregular = simular_divida(1000, 0.05, [200, 200, 0, 200])
        self.assertGreater(irregular["meses"], fixo["meses"])

    def test_price_e_taxa_implicita_sao_inversas(self):
        pmt = parcela_price(5000, 0.035, 12)
        self.assertAlmostEqual(taxa_implicita(5000, pmt, 12), 0.035, places=6)

    def test_oferta_sem_juros(self):
        self.assertEqual(taxa_implicita(1200, 100, 12), 0.0)


class TestOrcamento(unittest.TestCase):
    def test_renda_base_usa_os_piores_meses(self):
        self.assertEqual(renda_base([2000, 500, 1500, 3000, 800, 1200]), (500 + 800 + 1200) / 3)

    def test_renda_base_vazia(self):
        with self.assertRaises(ValueError):
            renda_base([])

    def test_50_30_20_soma_a_renda(self):
        o = orcamento_50_30_20(2000)
        self.assertAlmostEqual(sum(o.values()), 2000)

    def test_indicadores(self):
        self.assertEqual(reserva_alvo(1500, 6), 9000)
        self.assertAlmostEqual(comprometimento(300, 1000), 0.3)
        self.assertEqual(folga_mensal(2000, 1000, 300), 700)


class TestRendaVariavel(unittest.TestCase):
    def test_diagnostico_niveis(self):
        self.assertEqual(diagnostico_renda([1000, 1010, 990, 1000])["nivel"], "estável")
        self.assertEqual(diagnostico_renda([800, 2400, 500, 2000, 1000, 1700])["nivel"], "alta")

    def test_diagnostico_exige_dois_meses(self):
        with self.assertRaises(ValueError):
            diagnostico_renda([1000])

    def test_retirada_maxima_nunca_faltou(self):
        rendas = [1500, 2400, 900, 2000, 1200, 1800]
        w = retirada_maxima(rendas)
        self.assertTrue(simular_colchao(rendas, w)["sustenta"])
        self.assertFalse(simular_colchao(rendas, w + 50)["sustenta"])

    def test_retirada_maxima_com_colchao(self):
        rendas = [500, 500, 500]
        self.assertAlmostEqual(retirada_maxima(rendas, 300), 600)

    def test_colchao_contabiliza_falta(self):
        r = simular_colchao([100, 0, 0], 100)
        self.assertEqual(r["meses_faltou"], 2)
        self.assertEqual(r["total_faltou"], 200)

    def test_cascata_prioridade(self):
        r = cascata(1000, 700, 200, 150)
        self.assertEqual((r["essenciais"], r["parcelas"], r["reserva"]), (700, 200, 100))
        self.assertEqual(r["falta_reserva"], 50)
        self.assertEqual(r["livre"], 0)
        ruim = cascata(500, 700, 200, 150)
        self.assertEqual(ruim["falta_essenciais"], 200)
        self.assertEqual(ruim["parcelas"], 0)

    def test_reserva_e_prazo(self):
        self.assertEqual(meses_reserva_sugeridos("alta"), 12)
        self.assertEqual(meses_para_atingir(9000, 400), 23)
        self.assertIsNone(meses_para_atingir(9000, 0))


if __name__ == "__main__":
    unittest.main()
