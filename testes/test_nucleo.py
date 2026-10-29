import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nucleo.dividas import parcela_price, simular_divida, taxa_implicita
from nucleo.orcamento import (comprometimento, folga_mensal, orcamento_50_30_20,
                              renda_base, reserva_alvo)


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


if __name__ == "__main__":
    unittest.main()
