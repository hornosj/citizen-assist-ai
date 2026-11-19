"""
Organização dos assuntos em um grafo simples (lista de adjacência).

Nós:
  "tema:<chave>"              ex.: tema:documentos
  "sub:<tema>/<subtema>"      ex.: sub:documentos/identificacao
  "reg:<id>"                  ex.: reg:DOC01

Arestas:
  - hierarquia (tema -> subtema -> orientação): forma uma árvore de 3 níveis;
  - "relacionados" de cada orientação (orientação <-> orientação): ligam
    assuntos que costumam aparecer juntos (ex.: CPF -> CIN -> conta gov.br);
  - "temas_relacionados" (tema <-> tema): usados para sugerir outro tema
    quando a pergunta não tem resposta.

A busca em largura (BFS) a partir de uma orientação devolve primeiro os vizinhos
diretos (mais próximos) e depois os vizinhos dos vizinhos.
"""

from collections import deque


class GrafoAssuntos:
    def __init__(self, base):
        self.base = base
        self.adjacencia = {}   # nó -> lista de (vizinho, tipo_da_aresta)
        self._montar()

    def _ligar(self, a, b, tipo, mao_dupla=True):
        self.adjacencia.setdefault(a, [])
        self.adjacencia.setdefault(b, [])
        if (b, tipo) not in self.adjacencia[a]:
            self.adjacencia[a].append((b, tipo))
        if mao_dupla and (a, tipo) not in self.adjacencia[b]:
            self.adjacencia[b].append((a, tipo))

    def _montar(self):
        for tema, subtemas in self.base.por_tema.items():
            for subtema, ids in subtemas.items():
                self._ligar(f"tema:{tema}", f"sub:{tema}/{subtema}", "contem", mao_dupla=False)
                for rid in ids:
                    self._ligar(f"sub:{tema}/{subtema}", f"reg:{rid}", "contem", mao_dupla=False)
        for r in self.base.registros:
            for rel in r["relacionados"]:
                self._ligar(f"reg:{r['id']}", f"reg:{rel}", "relacionado")
        for a, b in self.base.temas_relacionados:
            self._ligar(f"tema:{a}", f"tema:{b}", "tema_relacionado")

    # ---------- consultas ----------
    def vizinhos(self, no, tipo=None):
        return [v for v, t in self.adjacencia.get(no, []) if tipo is None or t == tipo]

    def sugestoes_continuidade(self, id_registro, limite=3):
        """
        Próximos assuntos para continuar a consulta (BFS pelas arestas
        'relacionado'). Se faltar, completa com orientações do mesmo subtema.
        """
        inicio = f"reg:{id_registro}"
        visitados, fila, ordem = {inicio}, deque([inicio]), []
        while fila and len(ordem) < limite:
            atual = fila.popleft()
            for viz in self.vizinhos(atual, "relacionado"):
                if viz not in visitados:
                    visitados.add(viz)
                    ordem.append(viz[4:])
                    fila.append(viz)
        if len(ordem) < limite:
            r = self.base.por_id[id_registro]
            for irmao in self.base.por_tema[r["tema"]][r["subtema"]]:
                if irmao != id_registro and irmao not in ordem:
                    ordem.append(irmao)
        return ordem[:limite]

    def temas_proximos(self, tema):
        return [v[5:] for v in self.vizinhos(f"tema:{tema}", "tema_relacionado")]

    def total_arestas(self):
        return sum(len(v) for v in self.adjacencia.values())

    def arvore_texto(self):
        """Representação da hierarquia tema > subtema > orientação."""
        linhas = []
        for tema, subtemas in self.base.por_tema.items():
            linhas.append(f"{self.base.nome_tema(tema)}")
            for subtema, ids in subtemas.items():
                if not ids:
                    continue
                linhas.append(f"  - {self.base.nome_subtema(tema, subtema)}")
                for rid in ids:
                    linhas.append(f"      {rid}  {self.base.por_id[rid]['titulo']}")
        return "\n".join(linhas)

    def mermaid(self):
        """Diagrama Mermaid (renderizado pelo GitHub) das relações entre orientações."""
        linhas = ["graph LR"]
        for tema, subtemas in self.base.por_tema.items():
            linhas.append(f'  subgraph {tema}["{self.base.nome_tema(tema)}"]')
            for ids in subtemas.values():
                for rid in ids:
                    titulo = self.base.por_id[rid]["titulo"].split(" (")[0]
                    linhas.append(f'    {rid}["{rid}: {titulo}"]')
            linhas.append("  end")
        vistos = set()
        for r in self.base.registros:
            for rel in r["relacionados"]:
                par = tuple(sorted((r["id"], rel)))
                if par not in vistos:
                    vistos.add(par)
                    linhas.append(f"  {par[0]} --- {par[1]}")
        return "\n".join(linhas)
