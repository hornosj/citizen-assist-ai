"""
Citizen Assist AI - assistente de orientação cidadã (protótipo acadêmico).

Execução:
    python src/sistema.py                      menu interativo
    python src/sistema.py --pergunta "texto"   responde uma pergunta e sai
    python src/sistema.py --testes             roda a avaliação automática
    python src/sistema.py --validar            confere a base de conhecimento
    python src/sistema.py --usabilidade        roteiro do teste de facilidade de uso
    python src/sistema.py --modelo A           usa o modelo de resposta A
"""

import argparse
import sys
import time

import respostas as R
from base_conhecimento import CAMINHO_BASE, ErroBase, carregar_base
from busca import AMBIGUA, ENCONTRADA, ENTRADA_INVALIDA, ENTRADA_VAZIA, SEM_RESPOSTA, MotorBusca
from navegacao import GrafoAssuntos

TITULO = "CITIZEN ASSIST AI - orientação cidadã"


class Sair(Exception):
    """Usuário pediu para encerrar (Ctrl+C / fim da entrada)."""


class Assistente:
    def __init__(self, base, modelo="B", entrada=input, saida=print):
        self.base = base
        self.motor = MotorBusca(base)
        self.grafo = GrafoAssuntos(base)
        self.modelo = modelo
        self.entrada = entrada
        self.saida = saida
        self.consultas = 0          # usado no teste de usabilidade

    # ---------- entrada com validação ----------
    def ler(self, rotulo):
        try:
            return self.entrada(rotulo).strip()
        except (EOFError, KeyboardInterrupt):
            raise Sair()

    def escolher(self, rotulo, opcoes):
        """
        Pede uma opção até ser válida. 'opcoes' é um dicionário
        {texto_digitado: valor}. Trata entrada vazia e opção inexistente.
        """
        while True:
            valor = self.ler(rotulo).upper()
            if not valor:
                self.saida("Você não digitou nenhuma opção. Digite uma das opções mostradas.")
            elif valor in opcoes:
                return opcoes[valor]
            else:
                self.saida(f"A opção \"{valor}\" não existe. Digite uma das opções mostradas.")

    # ---------- exibição ----------
    def cabecalho(self):
        self.saida("=" * R.LARGURA)
        self.saida(TITULO.center(R.LARGURA))
        self.saida("=" * R.LARGURA)
        self.saida(R._quebrar(R.AVISO_GERAL, recuo=""))
        self.saida("Não informe dados pessoais (CPF, endereço, telefone): eles não são necessários.")

    def mostrar_orientacao(self, registro, tempo_ms=None):
        """Mostra a orientação e oferece a navegação para assuntos relacionados."""
        while registro is not None:
            self.consultas += 1
            relacionados = self.grafo.sugestoes_continuidade(registro["id"])
            self.saida("")
            self.saida(R.formatar_orientacao(registro, self.base, self.modelo, relacionados))
            if self.modelo == "A":  # o modelo A não lista os relacionados no texto
                self.saida("Assuntos relacionados:")
                for n, rid in enumerate(relacionados, start=1):
                    self.saida(f"  [{n}] {rid} - {self.base.por_id[rid]['titulo']}")
            if tempo_ms is not None:
                self.saida(f"(consulta respondida em {tempo_ms:.2f} ms)")
                tempo_ms = None
            self.saida("")
            opcoes = {str(n): self.base.por_id[rid] for n, rid in enumerate(relacionados, start=1)}
            opcoes.update({"P": "P", "M": None})
            escolha = self.escolher(
                f"Digite 1 a {len(relacionados)} para continuar, P para nova pergunta ou M para o menu: ",
                opcoes,
            )
            if escolha == "P":
                self.fazer_pergunta()
                return
            registro = escolha

    def escolher_entre(self, ids):
        opcoes = {str(n): self.base.por_id[rid] for n, rid in enumerate(ids, start=1)}
        opcoes["M"] = None
        registro = self.escolher(f"Digite o número (1 a {len(ids)}) ou M para voltar ao menu: ", opcoes)
        if registro:
            self.mostrar_orientacao(registro)

    def responder(self, texto):
        """Fluxo completo: valida, busca, decide e apresenta."""
        inicio = time.perf_counter()
        res = self.motor.buscar(texto)
        tempo_ms = (time.perf_counter() - inicio) * 1000

        if res.dados_pessoais:
            self.saida(R.msg_dados_pessoais(res.dados_pessoais))
        if res.status == ENCONTRADA:
            self.mostrar_orientacao(res.registro, tempo_ms)
            return
        self.consultas += 1
        if res.status == ENTRADA_VAZIA:
            self.saida(R.msg_entrada_vazia())
        elif res.status == ENTRADA_INVALIDA:
            self.saida(R.msg_entrada_invalida())
        elif res.status == AMBIGUA:
            self.saida(R.msg_ambigua(res.opcoes, self.base))
            self.escolher_entre(res.opcoes)
        elif res.status == SEM_RESPOSTA:
            self.saida(R.msg_sem_resposta(res.opcoes, res.sugestoes_temas, self.base, res.motivo))
            if res.opcoes:
                self.escolher_entre(res.opcoes)

    # ---------- opções do menu ----------
    def navegar_temas(self):
        temas = self.base.temas_com_registros()
        self.saida("\nTEMAS DISPONÍVEIS")
        for n, t in enumerate(temas, start=1):
            self.saida(f"  [{n}] {self.base.nome_tema(t)} - {self.base.temas[t]['descricao']}")
        opcoes = {str(n): t for n, t in enumerate(temas, start=1)}
        opcoes["M"] = None
        tema = self.escolher("Escolha o tema (número) ou M para voltar: ", opcoes)
        if tema is None:
            return
        self.saida(f"\n{self.base.nome_tema(tema).upper()}")
        ids = []
        for subtema, lista in self.base.por_tema[tema].items():
            if not lista:
                continue
            self.saida(f"  {self.base.nome_subtema(tema, subtema)}")
            for rid in lista:
                ids.append(rid)
                self.saida(f"    [{len(ids)}] {self.base.por_id[rid]['titulo']}")
        proximos = self.grafo.temas_proximos(tema)
        if proximos:
            self.saida("  Temas próximos: " + ", ".join(self.base.nome_tema(t) for t in proximos))
        self.escolher_entre(ids)

    def fazer_pergunta(self):
        self.saida("\nEscreva sua dúvida em poucas palavras (ex.: \"como tirar o passaporte\").")
        self.responder(self.ler("Sua pergunta: "))

    def consultar_por_id(self):
        self.saida("\nCódigos disponíveis: " + ", ".join(self.base.por_id))
        codigo = self.ler("Digite o código (ex.: DOC01): ").upper()
        if not codigo:
            self.saida("Você não digitou nenhum código.")
        elif codigo in self.base.por_id:
            self.mostrar_orientacao(self.base.por_id[codigo])
        else:
            self.saida(f"O código \"{codigo}\" não existe na base.")

    def trocar_modelo(self):
        self.modelo = "A" if self.modelo == "B" else "B"
        self.saida(f"Agora usando: {R.MODELOS[self.modelo]['nome']}.")
        self.saida("Instrução (prompt) deste modelo:")
        self.saida(R.MODELOS[self.modelo]["instrucao"])

    def sobre(self):
        self.saida("\nSOBRE, PRIVACIDADE E LIMITAÇÕES")
        for texto in (
            R.AVISO_GERAL,
            "Como funciona: a pergunta é comparada com uma base de "
            f"{len(self.base.registros)} orientações verificadas em fontes oficiais; a resposta "
            "sempre mostra a fonte e a data em que ela foi conferida.",
            "Quando não há orientação suficiente, o assistente avisa e sugere outros "
            "temas, em vez de inventar uma resposta.",
            "Privacidade: nenhuma pergunta é gravada. CPF, e-mail e telefone digitados "
            "são removidos antes da busca.",
            "Em emergência: SAMU 192, Polícia Militar 190, Bombeiros 193.",
        ):
            self.saida(R._quebrar(texto))
        self.saida("\nORGANIZAÇÃO DOS ASSUNTOS")
        self.saida(self.grafo.arvore_texto())

    def rodar_testes(self):
        from avaliacao import rodar_avaliacao
        rodar_avaliacao(self.base, imprimir=self.saida)

    def rodar_usabilidade(self):
        from usabilidade import conduzir_teste
        conduzir_teste(self.base, entrada=self.entrada, saida=self.saida)

    # ---------- laço principal ----------
    def menu(self, modo_tarefa=False):
        acoes = {
            "1": self.navegar_temas,
            "2": self.fazer_pergunta,
            "3": self.consultar_por_id,
            "4": self.trocar_modelo,
            "5": self.sobre,
        }
        if not modo_tarefa:
            acoes.update({"6": self.rodar_testes, "7": self.rodar_usabilidade})
        acoes["0"] = None
        while True:
            self.saida("\nMENU PRINCIPAL")
            self.saida("  [1] Escolher um tema")
            self.saida("  [2] Fazer uma pergunta")
            self.saida("  [3] Consultar por código da orientação")
            self.saida(f"  [4] Trocar modelo de resposta (atual: {R.MODELOS[self.modelo]['nome']})")
            self.saida("  [5] Sobre, privacidade e limitações")
            if not modo_tarefa:
                self.saida("  [6] Rodar testes e indicadores")
                self.saida("  [7] Teste de facilidade de uso (roteiro)")
            self.saida("  [0] " + ("Terminei a tarefa" if modo_tarefa else "Sair"))
            acao = self.escolher("Opção: ", acoes)
            if acao is None:
                return
            acao()


def configurar_console():
    for fluxo in (sys.stdout, sys.stderr, sys.stdin):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def main(argv=None):
    configurar_console()
    parser = argparse.ArgumentParser(description="Citizen Assist AI - orientação cidadã")
    parser.add_argument("--pergunta", help="responde uma pergunta e sai")
    parser.add_argument("--modelo", choices=["A", "B"], default="B", help="modelo de resposta (padrão B)")
    parser.add_argument("--testes", action="store_true", help="roda a avaliação automática")
    parser.add_argument("--validar", action="store_true", help="valida a base e mostra a organização")
    parser.add_argument("--usabilidade", action="store_true", help="conduz o teste de facilidade de uso")
    parser.add_argument("--grafo", action="store_true", help="imprime o grafo de assuntos em Mermaid")
    parser.add_argument("--base", default=str(CAMINHO_BASE), help="caminho do arquivo da base")
    args = parser.parse_args(argv)

    try:
        base = carregar_base(args.base)
    except ErroBase as erro:
        print(f"Não foi possível carregar a base de conhecimento.\nMotivo: {erro}")
        print("Confira o arquivo data/base_conhecimento.json e tente de novo.")
        return 1

    assistente = Assistente(base, modelo=args.modelo)
    try:
        if args.validar:
            print(f"Base carregada: {len(base.registros)} orientações, "
                  f"{len(base.temas_com_registros())} temas, "
                  f"{assistente.grafo.total_arestas()} ligações no grafo.")
            print("\n".join(f"AVISO: {a}" for a in base.avisos) or "Nenhum problema encontrado.")
            print()
            print(assistente.grafo.arvore_texto())
        elif args.grafo:
            print(assistente.grafo.mermaid())
        elif args.testes:
            assistente.rodar_testes()
        elif args.usabilidade:
            assistente.rodar_usabilidade()
        elif args.pergunta is not None:
            assistente.entrada = lambda _: "M"   # modo não interativo: volta ao fim
            assistente.responder(args.pergunta)
        else:
            assistente.cabecalho()
            for aviso in base.avisos:
                print(f"AVISO DA BASE: {aviso}")
            assistente.menu()
            print("\nAté logo! Lembre-se de confirmar as informações nos canais oficiais.")
    except Sair:
        print("\nAté logo! Lembre-se de confirmar as informações nos canais oficiais.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
