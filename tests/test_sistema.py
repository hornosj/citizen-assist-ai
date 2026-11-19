"""
Testes automáticos de robustez (unittest, sem bibliotecas externas).
Rodar a partir da raiz do projeto:  python -m unittest discover tests -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from base_conhecimento import ErroBase, carregar_base  # noqa: E402
from busca import (AMBIGUA, ENCONTRADA, ENTRADA_INVALIDA, ENTRADA_VAZIA,  # noqa: E402
                   SEM_RESPOSTA, MotorBusca, mascarar_dados_pessoais, radical)
from navegacao import GrafoAssuntos  # noqa: E402
from sistema import Assistente  # noqa: E402

BASE = carregar_base()


def base_temporaria(conteudo):
    arq = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8")
    arq.write(conteudo if isinstance(conteudo, str) else json.dumps(conteudo))
    arq.close()
    return arq.name


class TestBase(unittest.TestCase):
    def test_base_real_valida(self):
        self.assertGreaterEqual(len(BASE.registros), 15)
        self.assertGreaterEqual(len(BASE.temas_com_registros()), 3)
        self.assertEqual(BASE.avisos, [])

    def test_arquivo_ausente(self):
        with self.assertRaises(ErroBase):
            carregar_base("nao_existe.json")

    def test_arquivo_vazio(self):
        with self.assertRaises(ErroBase):
            carregar_base(base_temporaria(""))

    def test_json_invalido(self):
        with self.assertRaises(ErroBase):
            carregar_base(base_temporaria("{ isso nao e json"))

    def test_registro_incompleto_e_ignorado(self):
        dados = json.loads(Path(__file__).resolve().parent.parent.joinpath("data", "base_conhecimento.json")
                           .read_text(encoding="utf-8"))
        dados["orientacoes"].append({"id": "XXX01", "tema": "documentos"})  # sem campos obrigatórios
        dados["orientacoes"].append(dict(dados["orientacoes"][0]))           # id repetido
        base = carregar_base(base_temporaria(dados))
        self.assertNotIn("XXX01", base.por_id)
        self.assertEqual(len(base.registros), len(BASE.registros))
        self.assertTrue(any("XXX01" in a for a in base.avisos))
        self.assertTrue(any("id repetido" in a for a in base.avisos))


class TestBusca(unittest.TestCase):
    motor = MotorBusca(BASE)

    def test_pergunta_direta(self):
        res = self.motor.buscar("Como tirar o passaporte?")
        self.assertEqual(res.status, ENCONTRADA)
        self.assertEqual(res.registro["id"], "DOC05")

    def test_erro_de_digitacao(self):
        self.assertEqual(self.motor.buscar("pasaporte").registro["id"], "DOC05")

    def test_busca_por_id(self):
        self.assertEqual(self.motor.buscar("dir06").registro["id"], "DIR06")

    def test_entrada_vazia(self):
        self.assertEqual(self.motor.buscar("   ").status, ENTRADA_VAZIA)
        self.assertEqual(self.motor.buscar(None).status, ENTRADA_VAZIA)

    def test_entrada_invalida(self):
        self.assertEqual(self.motor.buscar("?!?!").status, ENTRADA_INVALIDA)
        self.assertEqual(self.motor.buscar("como faço?").status, ENTRADA_INVALIDA)

    def test_ambigua(self):
        res = self.motor.buscar("documento")
        self.assertEqual(res.status, AMBIGUA)
        self.assertGreaterEqual(len(res.opcoes), 2)

    def test_fora_do_tema(self):
        self.assertEqual(self.motor.buscar("receita de bolo de cenoura").status, SEM_RESPOSTA)

    def test_dado_local(self):
        res = self.motor.buscar("qual o horário do posto de saúde?")
        self.assertEqual((res.status, res.motivo), (SEM_RESPOSTA, "dado_local"))

    def test_dados_pessoais_removidos(self):
        texto, tipos = mascarar_dados_pessoais("meu cpf 123.456.789-00 e email a@b.com")
        self.assertNotIn("123.456", texto)
        self.assertEqual(tipos, ["CPF", "e-mail"])

    def test_radical(self):
        self.assertEqual(radical("idosa"), radical("idoso"))
        self.assertEqual(radical("documentos"), radical("documento"))
        self.assertEqual(radical("denunciar"), radical("denuncia"))


class TestNavegacao(unittest.TestCase):
    def test_sugestoes_continuidade(self):
        grafo = GrafoAssuntos(BASE)
        sugestoes = grafo.sugestoes_continuidade("DOC02")
        self.assertEqual(len(sugestoes), 3)
        self.assertNotIn("DOC02", sugestoes)

    def test_fluxo_interativo_com_entradas_invalidas(self):
        """Simula um usuário: opção inexistente, vazio, tema, orientação e navegação."""
        entradas = iter(["9", "", "1", "1", "1", "1", "M", "2", "", "0"])
        saida = []
        assistente = Assistente(BASE, entrada=lambda _: next(entradas), saida=saida.append)
        assistente.menu()
        texto = "\n".join(saida)
        self.assertIn('A opção "9" não existe', texto)
        self.assertIn("Você não digitou nenhuma opção", texto)
        self.assertIn("FONTE CONSULTADA", texto)
        self.assertIn("Você não digitou nenhuma pergunta", texto)
        self.assertGreaterEqual(assistente.consultas, 3)


if __name__ == "__main__":
    unittest.main()
