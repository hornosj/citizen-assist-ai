"""
Motor de busca do Citizen Assist AI.

Estratégia (explicada em detalhes no README):
  1. Normalização: minúsculas, sem acentos e sem pontuação.
  2. Tokenização + remoção de palavras vazias (stopwords) e de verbos genéricos
     ("como", "fazer", "tirar"...), que não ajudam a distinguir um assunto do outro.
  3. Radical simplificado: corta plural e terminação de gênero
     (documentos -> document, idosa/idoso -> idos).
  4. Expansão da consulta: sinônimos da base (rg -> identidade) e correção de
     erros de digitação com difflib (pasaporte -> passaporte).
  5. Índice invertido (dicionário radical -> {id: peso}) montado a partir dos
     campos de cada registro, com pesos diferentes por campo.
  6. Pontuação = soma dos pesos das palavras da pergunta encontradas no registro
     + bônus quando uma palavra-chave composta aparece inteira na pergunta.
  7. Decisão: limiar mínimo de pontos e de cobertura; regra de ambiguidade quando
     dois registros empatam (diferença < 10%) ou a consulta tem uma única palavra
     genérica presente em vários registros.
"""

import difflib
import re
import unicodedata

# Situações possíveis de uma consulta.
ENCONTRADA = "ENCONTRADA"
AMBIGUA = "AMBIGUA"
SEM_RESPOSTA = "SEM_RESPOSTA"
ENTRADA_VAZIA = "ENTRADA_VAZIA"
ENTRADA_INVALIDA = "ENTRADA_INVALIDA"

# Peso de cada campo do registro no índice invertido.
PESOS_CAMPOS = {"titulo": 3, "palavras_chave": 3, "pergunta": 2, "subtema": 1, "tema": 1}
BONUS_FRASE = 2              # palavra-chave composta encontrada inteira na pergunta
PONTUACAO_MINIMA = 3         # abaixo disso a correspondência é fraca demais
COBERTURA_MINIMA = 0.5       # ao menos metade das palavras da pergunta reconhecidas
PONTUACAO_FORTE = 6          # ...ou 2+ palavras reconhecidas somando 6+ pontos
MARGEM_AMBIGUIDADE = 0.9     # 2º colocado com >= 90% dos pontos do 1º -> ambígua
REGISTROS_PALAVRA_GENERICA = 3  # palavra única presente em 3+ registros -> ambígua
TAMANHO_MAXIMO = 300         # caracteres aceitos em uma pergunta

STOPWORDS = set("""
a o as os um uma uns umas de da do das dos d em no na nos nas num numa por pelo pela
pelos pelas para pra pro pras pros com sem e ou que qual quais quem como onde quando
quanto quanta quantos quantas porque pq se eu me mim meu minha meus minhas seu sua seus
suas voce voces vc ele ela eles elas isso isto esse essa este esta aquele aquela ao aos
la aqui ai ja nao sim so tambem mais muito muita bem agora entao ola oi bom boa dia
tarde noite gostaria queria quero quer preciso precisa precisar posso pode podem
consigo consegue conseguir faco faz fazer feito tirar obter pedir solicitar saber sei
sobre ser sou e foi fui era estar estou esta tem tenho ter tive vai vou ir algum alguma
alguem coisa coisas ajuda ajudar favor informacao informacoes duvida duvidas tomar
pegar receber recebo usar ate apos depois antes contra poder ta to tava ne tipo
""".split())

# Pedidos de dados locais ou do caso pessoal: a base não tem como responder com
# segurança (horário do posto do bairro, valor exato do meu benefício...).
EXPRESSOES_FORA_DO_ESCOPO = [
    "horario", "funcionamento", "endereco", "perto de mim", "mais perto", "valor exato",
    "quanto vou receber", "minha situacao", "meu processo", "meu pedido", "andamento do meu",
]

# Padrões de dados pessoais que o assistente NÃO precisa e não deve guardar.
PADROES_DADOS_PESSOAIS = [
    ("CPF", re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")),
    ("e-mail", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")),
    ("telefone", re.compile(r"\(?\b\d{2}\)?\s?9?\d{4}-?\d{4}\b")),
]


def normalizar(texto):
    """Minúsculas, sem acentos e com pontuação trocada por espaço."""
    texto = unicodedata.normalize("NFD", str(texto).lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def radical(palavra):
    """Radical simplificado (stemming leve para o português)."""
    if len(palavra) <= 3 or palavra.isdigit():
        return palavra
    for sufixo, troca in (("coes", "cao"), ("oes", "ao"), ("aes", "ao"), ("ais", "al"), ("eis", "el")):
        if palavra.endswith(sufixo) and len(palavra) > len(sufixo) + 2:
            palavra = palavra[: -len(sufixo)] + troca
            break
    else:
        if palavra.endswith("s") and len(palavra) > 4:
            palavra = palavra[:-1]
    if palavra[-1] in "aoe" and len(palavra) > 4:
        palavra = palavra[:-1]
    # Terminações verbais comuns (denunciar/denúncia, desmaiou/desmaio, passando/passa).
    for sufixo in ("and", "end", "ind", "ar", "er", "ir", "ei", "ou"):
        if palavra.endswith(sufixo) and len(palavra) - len(sufixo) >= 3:
            palavra = palavra[: -len(sufixo)]
            break
    return palavra


def tokenizar(texto):
    """Texto -> lista de radicais, sem stopwords (mantém a ordem)."""
    return [radical(p) for p in normalizar(texto).split() if p not in STOPWORDS]


def mascarar_dados_pessoais(texto):
    """Troca CPF, e-mail e telefone por [omitido]. Devolve (texto, tipos encontrados)."""
    encontrados = []
    for nome, padrao in PADROES_DADOS_PESSOAIS:
        if padrao.search(texto):
            encontrados.append(nome)
            texto = padrao.sub("[omitido]", texto)
    return texto, encontrados


class ResultadoBusca:
    """Tudo o que a busca descobriu sobre uma consulta."""

    def __init__(self, status, consulta=""):
        self.status = status
        self.consulta = consulta
        self.registro = None          # registro escolhido (quando ENCONTRADA)
        self.candidatos = []          # [(pontos, cobertura, id)] em ordem decrescente
        self.opcoes = []              # ids oferecidos ao usuário (AMBIGUA / outras opções)
        self.sugestoes_temas = []     # temas sugeridos quando não há resposta
        self.motivo = ""              # "dado_local" quando pede dado local/pessoal
        self.correcoes = {}           # {palavra digitada: palavra corrigida}
        self.dados_pessoais = []      # tipos de dados pessoais removidos da pergunta
        self.tokens = []


class MotorBusca:
    """Índice invertido + ranking por pontuação."""

    def __init__(self, base):
        self.base = base
        self.indice = {}        # radical -> {id: peso}
        self.frases = {}        # id -> lista de palavras-chave compostas (radicais)
        self.sinonimos = {}     # radical -> {radicais sinônimos}
        self._montar_indice()
        self._montar_sinonimos()
        self.vocabulario = sorted(self.indice)

    # ---------- montagem ----------
    def _indexar(self, texto, id_registro, peso):
        for tok in tokenizar(texto):
            pesos = self.indice.setdefault(tok, {})
            pesos[id_registro] = max(pesos.get(id_registro, 0), peso)

    def _montar_indice(self):
        for r in self.base.registros:
            rid = r["id"]
            self._indexar(r["titulo"], rid, PESOS_CAMPOS["titulo"])
            self._indexar(r["pergunta"], rid, PESOS_CAMPOS["pergunta"])
            self._indexar(self.base.nome_tema(r["tema"]), rid, PESOS_CAMPOS["tema"])
            self._indexar(self.base.nome_subtema(r["tema"], r["subtema"]), rid, PESOS_CAMPOS["subtema"])
            self.frases[rid] = []
            for chave in r["palavras_chave"]:
                self._indexar(chave, rid, PESOS_CAMPOS["palavras_chave"])
                radicais = tokenizar(chave)
                if len(radicais) >= 2:
                    self.frases[rid].append(" ".join(radicais))

    def _montar_sinonimos(self):
        for palavra, lista in self.base.sinonimos.items():
            chave = radical(normalizar(palavra))
            for sinonimo in lista:
                self.sinonimos.setdefault(chave, set()).update(tokenizar(sinonimo))

    # ---------- consulta ----------
    def variantes(self, token, correcoes):
        """Formas aceitas para uma palavra: ela mesma, sinônimos ou correção."""
        formas = {token} | self.sinonimos.get(token, set())
        if token not in self.indice and not (formas - {token}) and len(token) >= 5:
            parecidas = difflib.get_close_matches(token, self.vocabulario, n=1, cutoff=0.8)
            if parecidas:
                correcoes[token] = parecidas[0]
                formas.add(parecidas[0])
        return formas

    def pontuar(self, tokens, correcoes):
        """Devolve {id: [pontos, palavras_cobertas]} para os registros tocados."""
        placar = {}
        texto_consulta = " " + " ".join(correcoes.get(t, t) for t in tokens) + " "
        for tok in dict.fromkeys(tokens):          # cada palavra conta uma vez
            melhores = {}
            for forma in self.variantes(tok, correcoes):
                for rid, peso in self.indice.get(forma, {}).items():
                    melhores[rid] = max(melhores.get(rid, 0), peso)
            for rid, peso in melhores.items():
                item = placar.setdefault(rid, [0, 0])
                item[0] += peso
                item[1] += 1
        for rid, item in placar.items():
            item[0] += BONUS_FRASE * sum(1 for f in self.frases[rid] if f" {f} " in texto_consulta)
        return placar

    def registros_com(self, tokens):
        """Ids que contêm alguma das palavras (usado para palavras genéricas)."""
        ids = set()
        for tok in tokens:
            for forma in self.variantes(tok, {}):
                ids.update(self.indice.get(forma, {}))
        return ids

    def buscar(self, texto):
        """Recebe a pergunta do usuário e devolve um ResultadoBusca."""
        texto = "" if texto is None else str(texto)
        if not texto.strip():
            return ResultadoBusca(ENTRADA_VAZIA)

        texto = texto.strip()[:TAMANHO_MAXIMO]
        texto, dados_pessoais = mascarar_dados_pessoais(texto)

        # Consulta direta por identificador (ex.: "DOC01").
        if texto.upper() in self.base.por_id:
            res = ResultadoBusca(ENCONTRADA, texto)
            res.registro = self.base.por_id[texto.upper()]
            res.dados_pessoais = dados_pessoais
            return res

        tokens = [t for t in tokenizar(texto.replace("[omitido]", " ")) if t]
        res = ResultadoBusca(ENTRADA_INVALIDA, texto)
        res.dados_pessoais = dados_pessoais
        res.tokens = tokens
        if not tokens:
            # Só símbolos ou só palavras genéricas ("como faço?").
            return res

        placar = self.pontuar(tokens, res.correcoes)
        candidatos = sorted(
            ((pts, cobertos / len(set(tokens)), rid) for rid, (pts, cobertos) in placar.items()),
            key=lambda c: (-c[0], -c[1], c[2]),
        )
        res.candidatos = candidatos
        validos = [c for c in candidatos if self._aceitavel(c, placar[c[2]][1])]

        # Pergunta sobre dado local/pessoal: avisa o limite em vez de arriscar.
        consulta_norm = f" {normalizar(texto)} "
        if any(f" {exp} " in consulta_norm for exp in EXPRESSOES_FORA_DO_ESCOPO):
            res.status = SEM_RESPOSTA
            res.motivo = "dado_local"
            res.opcoes = [rid for pts, _, rid in candidatos[:3] if pts > 0]
            res.sugestoes_temas = self._temas_sugeridos(res.opcoes)
            return res

        # Uma única palavra que aparece em vários registros: pergunta genérica.
        if len(set(tokens)) == 1 and validos:
            ids = self.registros_com(tokens)
            if len(ids) >= REGISTROS_PALAVRA_GENERICA:
                res.status = AMBIGUA
                res.opcoes = [rid for _, _, rid in candidatos if rid in ids][:5]
                return res

        if not validos:
            res.status = SEM_RESPOSTA
            res.opcoes = [rid for pts, _, rid in candidatos[:3] if pts > 0]
            res.sugestoes_temas = self._temas_sugeridos(res.opcoes)
            return res

        primeiro = validos[0]
        empatados = [c for c in validos[1:] if c[0] >= MARGEM_AMBIGUIDADE * primeiro[0]]
        if empatados:
            res.status = AMBIGUA
            res.opcoes = [primeiro[2]] + [c[2] for c in empatados][:3]
            return res

        res.status = ENCONTRADA
        res.registro = self.base.por_id[primeiro[2]]
        # Outras correspondências razoáveis viram "veja também".
        res.opcoes = [c[2] for c in validos[1:4] if c[0] >= 0.5 * primeiro[0]]
        return res

    @staticmethod
    def _aceitavel(candidato, palavras_cobertas):
        """
        Correspondência aceita quando tem pontos suficientes e:
          - cobre ao menos metade das palavras da pergunta; ou
          - em perguntas longas, acerta 2+ palavras com pontuação forte
            (palavras soltas como "tênis" ou "semana" não derrubam a busca).
        """
        pontos, cobertura, _ = candidato
        if pontos < PONTUACAO_MINIMA:
            return False
        return cobertura >= COBERTURA_MINIMA or (palavras_cobertas >= 2 and pontos >= PONTUACAO_FORTE)

    def _temas_sugeridos(self, ids_parciais):
        """Temas das correspondências parciais; sem nenhuma, todos os temas."""
        temas = []
        for rid in ids_parciais:
            tema = self.base.por_id[rid]["tema"]
            if tema not in temas:
                temas.append(tema)
        return temas or self.base.temas_com_registros()
