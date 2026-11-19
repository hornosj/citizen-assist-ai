"""
Modelos de resposta (estratégias de prompt / instrução de resposta).

O protótipo não depende de um modelo de linguagem: cada "modelo" é uma
INSTRUÇÃO documentada (o texto que seria o prompt de sistema de uma IA) e uma
função que aplica essa instrução de forma determinística sobre o registro
recuperado da base. Assim a resposta nunca contém nada que não esteja na base.

  Modelo A - "Direto": instrução mínima (papel + citar a fonte).
  Modelo B - "Estruturado": papel, público, regras de linguagem simples,
             formato fixo em seções, fonte com data, aviso e continuidade.

A comparação entre os dois está em avaliacao.py e docs/modelos_de_prompt.md.
"""

import textwrap
from datetime import datetime

LARGURA = 76

INSTRUCAO_A = (
    "Você é um assistente de informações. Responda à pergunta usando a "
    "orientação encontrada na base e cite a fonte."
)

INSTRUCAO_B = """\
PAPEL: Você é o Citizen Assist AI, assistente de orientação cidadã. Você NÃO é
canal oficial de nenhum órgão público e não realiza atendimentos.
PÚBLICO: qualquer cidadão, inclusive quem não conhece termos técnicos.
REGRAS:
1. Use SOMENTE a orientação recuperada da base verificada; nunca invente
   prazos, valores, documentos ou requisitos.
2. Linguagem simples: frases curtas e diretas.
3. Formato fixo, sempre nesta ordem: RESPOSTA, COMO FAZER (passos numerados),
   FONTE CONSULTADA (órgão, título, link e data de verificação), ATENÇÃO e
   PARA CONTINUAR (assuntos relacionados).
4. Sempre cite a fonte e a data em que ela foi verificada.
5. Se a orientação exigir confirmação, diga o motivo e indique o canal oficial.
6. Se não houver orientação na base, diga isso claramente e sugira temas.
7. Não peça dados pessoais (CPF, endereço, telefone, e-mail)."""

MODELOS = {
    "A": {"nome": "Modelo A - Direto", "instrucao": INSTRUCAO_A},
    "B": {"nome": "Modelo B - Estruturado", "instrucao": INSTRUCAO_B},
}

AVISO_GERAL = (
    "Este assistente é um protótipo acadêmico e NÃO é canal oficial de nenhum "
    "órgão público. As orientações são resumos de fontes públicas e podem mudar."
)


def _quebrar(texto, recuo="  "):
    return textwrap.fill(texto, width=LARGURA, initial_indent=recuo, subsequent_indent=recuo)


def data_br(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%d/%m/%Y")


def formatar_modelo_a(registro, base=None, relacionados=None):
    linhas = [
        textwrap.fill("Resposta: " + registro["orientacao"], width=LARGURA),
        "Fonte: " + registro["referencia"]["url"],
    ]
    if registro.get("requer_confirmacao"):
        linhas.append("Confirme no canal oficial.")
    return "\n".join(linhas)


def formatar_modelo_b(registro, base, relacionados=None):
    ref = registro["referencia"]
    caminho = f"{base.nome_tema(registro['tema'])} > {base.nome_subtema(registro['tema'], registro['subtema'])}"
    linhas = [
        "-" * LARGURA,
        f"{registro['id']} | {registro['titulo']}",
        f"Tema: {caminho}",
        "-" * LARGURA,
        "RESPOSTA",
        _quebrar(registro["orientacao"]),
    ]
    if registro.get("passos"):
        linhas.append("COMO FAZER")
        for n, passo in enumerate(registro["passos"], start=1):
            linhas.append(textwrap.fill(passo, width=LARGURA, initial_indent=f"  {n}. ", subsequent_indent="     "))
    linhas += [
        "FONTE CONSULTADA",
        _quebrar(f"{ref['orgao']} - {ref['titulo']}"),
        "  " + ref["url"],
        f"  Verificada em {data_br(registro['data_verificacao'])}",
        "ATENÇÃO",
    ]
    if registro.get("requer_confirmacao"):
        motivo = registro.get("observacao_confirmacao", "As regras podem ter mudado.")
        linhas.append(_quebrar(f"Confirme os requisitos atualizados no canal oficial antes de ir. {motivo}"))
    else:
        linhas.append(_quebrar("Orientação informativa. Em caso de dúvida, consulte o canal oficial citado."))
    if relacionados:
        linhas.append("PARA CONTINUAR, VOCÊ TAMBÉM PODE CONSULTAR")
        for n, rid in enumerate(relacionados, start=1):
            linhas.append(f"  [{n}] {rid} - {base.por_id[rid]['titulo']}")
    return "\n".join(linhas)


FORMATADORES = {"A": formatar_modelo_a, "B": formatar_modelo_b}


def formatar_orientacao(registro, base, modelo="B", relacionados=None):
    return FORMATADORES[modelo](registro, base, relacionados)


# ---------- mensagens do sistema (iguais nos dois modelos) ----------

def msg_entrada_vazia():
    return ("Você não digitou nenhuma pergunta. Escreva sua dúvida em poucas palavras\n"
            "(ex.: \"como fazer o CPF\") ou volte ao menu e escolha um tema.")


def msg_entrada_invalida():
    return ("Não consegui entender a pergunta. Tente citar o documento, serviço ou\n"
            "direito que você procura (ex.: \"passaporte\", \"cartão do SUS\", \"meia-entrada\").")


def msg_ambigua(opcoes, base):
    linhas = ["Sua pergunta pode se referir a mais de um assunto. Qual destes você procura?"]
    for n, rid in enumerate(opcoes, start=1):
        linhas.append(f"  [{n}] {rid} - {base.por_id[rid]['titulo']}")
    return "\n".join(linhas)


def msg_sem_resposta(opcoes, temas, base, motivo=""):
    if motivo == "dado_local":
        linhas = [
            "Essa pergunta depende de informações locais ou do seu caso (horários,",
            "endereços, valores exatos, andamento de pedidos), que este assistente não tem.",
            "Para não passar uma informação errada, prefiro não responder.",
        ]
    else:
        linhas = [
            "Não encontrei na base uma orientação confiável para essa pergunta.",
            "Para não passar uma informação errada, prefiro não responder.",
        ]
    if opcoes:
        linhas.append("Assuntos parecidos que existem na base:")
        for n, rid in enumerate(opcoes, start=1):
            linhas.append(f"  [{n}] {rid} - {base.por_id[rid]['titulo']}")
    linhas.append("Temas sugeridos: " + "; ".join(base.nome_tema(t) for t in temas) + ".")
    linhas.append("Para outros assuntos, procure o portal oficial gov.br ou o órgão responsável.")
    return "\n".join(linhas)


def msg_dados_pessoais(tipos):
    return (f"Aviso de privacidade: sua pergunta parecia conter {', '.join(tipos)}. Não é\n"
            "preciso informar dados pessoais: eles foram removidos e não são guardados.")
