"""
Teste de facilidade de uso (roteiro de tarefas).

Como aplicar:
  1. Uma pessoa que NÃO participou do projeto usa o assistente (participante).
  2. Um integrante da equipe conduz (observador): roda
         python src/sistema.py --usabilidade
     lê cada tarefa em voz alta e deixa o participante usar o menu sozinho.
  3. Ao terminar cada tarefa o participante escolhe [0] "Terminei a tarefa";
     o programa registra tempo, número de consultas, se concluiu e a nota de
     dificuldade (1 = muito fácil ... 5 = muito difícil).
  4. Resultados: data/usabilidade.csv  e  docs/resultados_usabilidade.md

Privacidade: o participante é identificado só por um código (P1, P2...).
Não registre nome, idade exata ou qualquer dado pessoal.
"""

import csv
import statistics
import time
from datetime import datetime

from base_conhecimento import RAIZ_PROJETO

CAMINHO_CSV = RAIZ_PROJETO / "data" / "usabilidade.csv"
CAMINHO_RELATORIO = RAIZ_PROJETO / "docs" / "resultados_usabilidade.md"

TAREFAS = [
    ("U1", "Descubra se a primeira via da Carteira de Identidade Nacional (novo RG) é paga."),
    ("U2", "Você comprou um produto pela internet e se arrependeu. Descubra em quantos dias pode desistir."),
    ("U3", "Usando o MENU DE TEMAS (sem digitar pergunta), encontre o telefone para emergência médica."),
    ("U4", "Pergunte algo que o assistente provavelmente não sabe (ex.: como pagar o IPTU) e diga o que ele fez."),
    ("U5", "Abra a orientação sobre o CPF e, a partir dela, navegue para um assunto relacionado."),
]

CAMPOS = ["data", "participante", "tarefa", "concluiu", "tempo_s", "consultas", "dificuldade_1a5", "comentario"]


def _perguntar(entrada, saida, rotulo, validas=None):
    while True:
        valor = entrada(rotulo).strip()
        if validas is None or valor.upper() in validas:
            return valor.upper() if validas else valor
        saida(f"Resposta inválida. Opções: {', '.join(sorted(validas))}")


def conduzir_teste(base, entrada=input, saida=print):
    from sistema import Assistente  # import local para evitar ciclo

    saida("\nTESTE DE FACILIDADE DE USO")
    saida("Use apenas um código para o participante (ex.: P1). Não registre nomes.")
    participante = _perguntar(entrada, saida, "Código do participante: ") or "P?"
    linhas = []
    for codigo, tarefa in TAREFAS:
        saida("\n" + "#" * 76)
        saida(f"TAREFA {codigo}: {tarefa}")
        saida("Quando terminar, escolha [0] Terminei a tarefa no menu.")
        saida("#" * 76)
        assistente = Assistente(base, entrada=entrada, saida=saida)
        inicio = time.perf_counter()
        assistente.menu(modo_tarefa=True)
        tempo = time.perf_counter() - inicio
        concluiu = _perguntar(entrada, saida, "(Observador) Concluiu? S=sim, P=parcial, N=não: ", {"S", "P", "N"})
        nota = _perguntar(entrada, saida, "(Participante) Dificuldade de 1 (muito fácil) a 5 (muito difícil): ",
                          {"1", "2", "3", "4", "5"})
        comentario = _perguntar(entrada, saida, "Comentário/dificuldade observada (opcional, sem dados pessoais): ")
        linhas.append({
            "data": datetime.now().strftime("%Y-%m-%d"), "participante": participante, "tarefa": codigo,
            "concluiu": concluiu, "tempo_s": round(tempo, 1), "consultas": assistente.consultas,
            "dificuldade_1a5": nota, "comentario": comentario.replace(";", ","),
        })
    gravar(linhas)
    gerar_relatorio(saida)


def gravar(linhas):
    novo = not CAMINHO_CSV.exists()
    with open(CAMINHO_CSV, "a", newline="", encoding="utf-8-sig") as arq:
        escritor = csv.DictWriter(arq, fieldnames=CAMPOS, delimiter=";")
        if novo:
            escritor.writeheader()
        escritor.writerows(linhas)


def ler():
    if not CAMINHO_CSV.exists():
        return []
    with open(CAMINHO_CSV, encoding="utf-8-sig") as arq:
        return list(csv.DictReader(arq, delimiter=";"))


def gerar_relatorio(saida=print):
    linhas = ler()
    if not linhas:
        saida("Ainda não há resultados de usabilidade registrados.")
        return
    participantes = sorted({l["participante"] for l in linhas})
    md = [
        "# Resultados do teste de facilidade de uso (gerado automaticamente)",
        "",
        f"Participantes: {len(participantes)} ({', '.join(participantes)}). "
        f"Atualizado em {datetime.now().strftime('%d/%m/%Y %H:%M')}.",
        "",
        "| Tarefa | Descrição | Conclusão (S) | Tempo médio (s) | Consultas (média) | Dificuldade média (1-5) |",
        "|---|---|---|---|---|---|",
    ]
    descricoes = dict(TAREFAS)
    for codigo, _ in TAREFAS:
        grupo = [l for l in linhas if l["tarefa"] == codigo]
        if not grupo:
            continue
        concl = sum(l["concluiu"] == "S" for l in grupo) / len(grupo)
        tempo = statistics.mean(float(l["tempo_s"]) for l in grupo)
        consultas = statistics.mean(int(l["consultas"]) for l in grupo)
        dif = statistics.mean(int(l["dificuldade_1a5"]) for l in grupo)
        md.append(f"| {codigo} | {descricoes[codigo]} | {concl:.0%} | {tempo:.1f} | {consultas:.1f} | {dif:.1f} |")
    total_concl = sum(l["concluiu"] == "S" for l in linhas) / len(linhas)
    md += [
        "",
        f"**Taxa de conclusão geral:** {total_concl:.0%}  ",
        f"**Tempo médio por tarefa:** {statistics.mean(float(l['tempo_s']) for l in linhas):.1f} s  ",
        f"**Dificuldade média:** {statistics.mean(int(l['dificuldade_1a5']) for l in linhas):.1f} (1 = muito fácil, 5 = muito difícil)",
        "",
        "## Comentários registrados",
        "",
    ]
    md += [f"- {l['participante']} / {l['tarefa']}: {l['comentario']}" for l in linhas if l["comentario"]] or ["- (nenhum)"]
    CAMINHO_RELATORIO.write_text("\n".join(md) + "\n", encoding="utf-8")
    saida("\n".join(md))
    saida(f"\nRelatório salvo em {CAMINHO_RELATORIO.relative_to(RAIZ_PROJETO)}")
