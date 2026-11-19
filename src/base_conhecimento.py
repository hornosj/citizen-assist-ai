"""
Carga e validação da base de conhecimento (data/base_conhecimento.json).

A base é um arquivo JSON editável: para acrescentar ou corrigir uma orientação
basta editar o arquivo, sem mexer nas regras do programa. Este módulo:
  - lê o arquivo e trata arquivo ausente, vazio ou com JSON inválido;
  - confere os campos obrigatórios de cada registro;
  - descarta registros inconsistentes (mostrando o motivo) sem derrubar o programa;
  - organiza os registros em dicionários para consulta por id e por tema/subtema.
"""

import json
from datetime import date, datetime
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BASE = RAIZ_PROJETO / "data" / "base_conhecimento.json"

# Campos que todo registro precisa ter (requisito do desafio: identificador,
# tema, pergunta/palavras-chave, orientação, referência e data de verificação).
CAMPOS_OBRIGATORIOS = (
    "id", "tema", "subtema", "titulo", "pergunta",
    "palavras_chave", "orientacao", "referencia", "data_verificacao",
)
CAMPOS_REFERENCIA = ("orgao", "titulo", "url")

# Registros verificados há mais tempo que isso recebem aviso de revisão.
DIAS_PARA_REVISAO = 365


class ErroBase(Exception):
    """Erro que impede o uso da base (arquivo ausente, vazio, ilegível...)."""


class BaseConhecimento:
    """Guarda a base já validada e os índices em dicionários."""

    def __init__(self, temas, registros, sinonimos, temas_relacionados, avisos):
        self.temas = temas                          # {tema: {nome, descricao, subtemas}}
        self.registros = registros                  # lista de dicionários (ordem do arquivo)
        self.sinonimos = sinonimos                  # {palavra: [sinônimos]}
        self.temas_relacionados = temas_relacionados  # lista de pares [tema_a, tema_b]
        self.avisos = avisos                        # problemas encontrados na validação

        # Dicionário id -> registro: busca por identificador em O(1).
        self.por_id = {r["id"]: r for r in registros}

        # Hierarquia tema -> subtema -> [ids], na ordem do arquivo.
        self.por_tema = {}
        for chave_tema, tema in temas.items():
            self.por_tema[chave_tema] = {sub: [] for sub in tema.get("subtemas", {})}
        for r in registros:
            self.por_tema[r["tema"]][r["subtema"]].append(r["id"])

    def nome_tema(self, chave):
        return self.temas[chave]["nome"]

    def nome_subtema(self, tema, subtema):
        return self.temas[tema]["subtemas"][subtema]

    def temas_com_registros(self):
        """Lista de chaves de temas que têm ao menos uma orientação."""
        return [t for t, subs in self.por_tema.items() if any(subs.values())]


def ler_json(caminho):
    """Lê o arquivo JSON tratando os problemas mais comuns."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise ErroBase(f"Arquivo da base não encontrado: {caminho}")
    texto = caminho.read_text(encoding="utf-8").strip()
    if not texto:
        raise ErroBase(f"O arquivo da base está vazio: {caminho}")
    try:
        return json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ErroBase(
            f"O arquivo da base não é um JSON válido (linha {erro.lineno}, "
            f"coluna {erro.colno}): {erro.msg}"
        ) from erro


def validar_registro(registro, temas, ids_vistos, hoje):
    """
    Devolve (problemas_graves, alertas) de um registro.
    Problema grave -> o registro é descartado. Alerta -> o registro é mantido.
    """
    graves, alertas = [], []
    if not isinstance(registro, dict):
        return ["registro não é um objeto JSON"], alertas

    faltando = [c for c in CAMPOS_OBRIGATORIOS if c not in registro or registro[c] in ("", [], None)]
    if faltando:
        graves.append("campos obrigatórios ausentes ou vazios: " + ", ".join(faltando))
        return graves, alertas

    if registro["id"] in ids_vistos:
        graves.append("id repetido")

    tema, subtema = registro["tema"], registro["subtema"]
    if tema not in temas:
        graves.append(f"tema '{tema}' não está cadastrado em 'temas'")
    elif subtema not in temas[tema].get("subtemas", {}):
        graves.append(f"subtema '{subtema}' não existe no tema '{tema}'")

    if not isinstance(registro["palavras_chave"], list):
        graves.append("'palavras_chave' deve ser uma lista")

    ref = registro["referencia"]
    if not isinstance(ref, dict) or any(not ref.get(c) for c in CAMPOS_REFERENCIA):
        graves.append("referência incompleta (precisa de orgao, titulo e url)")
    elif not str(ref["url"]).startswith(("http://", "https://")):
        graves.append("URL da referência inválida")

    try:
        verificado_em = datetime.strptime(registro["data_verificacao"], "%Y-%m-%d").date()
        if verificado_em > hoje:
            graves.append("data de verificação no futuro")
        elif (hoje - verificado_em).days > DIAS_PARA_REVISAO:
            alertas.append(f"verificado há mais de {DIAS_PARA_REVISAO} dias: revisar a fonte")
    except (TypeError, ValueError):
        graves.append("data_verificacao deve estar no formato AAAA-MM-DD")

    return graves, alertas


def carregar_base(caminho=CAMINHO_BASE, hoje=None):
    """Lê, valida e devolve um objeto BaseConhecimento."""
    hoje = hoje or date.today()
    dados = ler_json(caminho)

    if not isinstance(dados, dict) or not isinstance(dados.get("orientacoes"), list):
        raise ErroBase("A base precisa ter uma lista 'orientacoes'.")
    temas = dados.get("temas")
    if not isinstance(temas, dict) or not temas:
        raise ErroBase("A base precisa ter o dicionário 'temas'.")

    avisos, registros, ids_vistos = [], [], set()
    for posicao, registro in enumerate(dados["orientacoes"], start=1):
        graves, alertas = validar_registro(registro, temas, ids_vistos, hoje)
        rotulo = registro.get("id", f"#{posicao}") if isinstance(registro, dict) else f"#{posicao}"
        if graves:
            avisos.append(f"Registro {rotulo} ignorado: " + "; ".join(graves))
            continue
        for alerta in alertas:
            avisos.append(f"Registro {rotulo}: {alerta}")
        registro.setdefault("passos", [])
        registro.setdefault("relacionados", [])
        registro.setdefault("requer_confirmacao", True)  # na dúvida, pede confirmação
        ids_vistos.add(registro["id"])
        registros.append(registro)

    if not registros:
        raise ErroBase("Nenhuma orientação válida foi encontrada na base.")

    # Relacionamentos que apontam para ids inexistentes são removidos.
    for r in registros:
        validos = [rel for rel in r["relacionados"] if rel in ids_vistos and rel != r["id"]]
        for rel in set(r["relacionados"]) - set(validos):
            avisos.append(f"Registro {r['id']}: relacionado '{rel}' não existe e foi ignorado")
        r["relacionados"] = validos

    relacionados = [
        par for par in dados.get("temas_relacionados", [])
        if isinstance(par, list) and len(par) == 2 and all(t in temas for t in par)
    ]
    sinonimos = dados.get("sinonimos", {}) if isinstance(dados.get("sinonimos"), dict) else {}

    return BaseConhecimento(temas, registros, sinonimos, relacionados, avisos)
