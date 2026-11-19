"""
Avaliação automática do assistente.

  - Executa as perguntas de data/perguntas_teste.json;
  - compara a resposta obtida com a esperada (acerto ou erro);
  - mede o tempo de cada consulta (média de várias repetições, em milissegundos);
  - calcula taxa de acerto geral e por tipo de pergunta;
  - compara os modelos de resposta A e B por critérios objetivos;
  - grava data/resultados_testes.csv, data/comparacao_modelos.csv e
    docs/resultados_testes.md.

Uso: python src/avaliacao.py   (ou opção 5 do menu de sistema.py)
"""

import csv
import json
import statistics
import time
from collections import Counter
from datetime import datetime

from base_conhecimento import RAIZ_PROJETO, carregar_base, ler_json
from busca import ENCONTRADA, MotorBusca
from navegacao import GrafoAssuntos
from respostas import MODELOS, formatar_orientacao

CAMINHO_PERGUNTAS = RAIZ_PROJETO / "data" / "perguntas_teste.json"
CAMINHO_RESULTADOS = RAIZ_PROJETO / "data" / "resultados_testes.csv"
CAMINHO_COMPARACAO = RAIZ_PROJETO / "data" / "comparacao_modelos.csv"
CAMINHO_RELATORIO = RAIZ_PROJETO / "docs" / "resultados_testes.md"
REPETICOES = 50  # cada consulta é repetida para a medida de tempo ficar estável

NOMES_TIPOS = {
    "direta": "Dúvidas diretas",
    "reformulacao": "Reformulações",
    "fora_do_tema": "Fora dos temas",
    "limitacao": "Limitações",
    "cega": "Às cegas lote 1 (usado nos ajustes)",
    "cega2": "Às cegas lote 2 (sem ajustes)",
}


def carregar_perguntas(caminho=CAMINHO_PERGUNTAS):
    dados = ler_json(caminho)
    perguntas = dados.get("perguntas", []) if isinstance(dados, dict) else []
    return [p for p in perguntas if {"id", "tipo", "pergunta", "esperado"} <= set(p)]


def obtido(resultado):
    """Resumo do que o assistente devolveu: id da orientação ou a situação."""
    return resultado.registro["id"] if resultado.status == ENCONTRADA else resultado.status


def classificar_erro(esperado, resposta, opcoes):
    """Separa erros perigosos (resposta errada) de erros seguros (não respondeu)."""
    eh_id = lambda v: v[:3] in ("DOC", "SER", "DIR", "COM")
    if resposta == esperado:
        return ""
    if eh_id(resposta):
        return "respondeu_errado" if eh_id(esperado) else "respondeu_fora_da_base"
    if resposta == "AMBIGUA":
        return "pediu_esclarecimento" + (" (certa entre as opcoes)" if esperado in opcoes else "")
    if eh_id(esperado):
        return "nao_respondeu" + (" (certa entre as sugestoes)" if esperado in opcoes else "")
    return "situacao_diferente"


def executar_testes(motor, perguntas, repeticoes=REPETICOES):
    linhas = []
    for p in perguntas:
        inicio = time.perf_counter()
        for _ in range(repeticoes):
            resultado = motor.buscar(p["pergunta"])
        tempo_ms = (time.perf_counter() - inicio) * 1000 / repeticoes
        resposta = obtido(resultado)
        melhor = resultado.candidatos[0] if resultado.candidatos else (0, 0, "-")
        linhas.append({
            "id": p["id"],
            "tipo": p["tipo"],
            "pergunta": p["pergunta"],
            "esperado": p["esperado"],
            "obtido": resposta,
            "acerto": "SIM" if resposta == p["esperado"] else "NAO",
            "tipo_erro": classificar_erro(p["esperado"], resposta, resultado.opcoes),
            "tempo_ms": round(tempo_ms, 4),
            "melhor_candidato": f"{melhor[2]} ({melhor[0]} pts, cobertura {melhor[1]:.0%})",
            "opcoes_oferecidas": " ".join(resultado.opcoes),
            "dados_pessoais_removidos": ", ".join(resultado.dados_pessoais),
            "obs": p.get("obs", ""),
        })
    return linhas


def indicadores(linhas):
    tempos = [l["tempo_ms"] for l in linhas]
    por_tipo = {}
    for tipo in dict.fromkeys(l["tipo"] for l in linhas):
        grupo = [l for l in linhas if l["tipo"] == tipo]
        acertos = sum(l["acerto"] == "SIM" for l in grupo)
        por_tipo[tipo] = (acertos, len(grupo))
    acertos = sum(l["acerto"] == "SIM" for l in linhas)
    return {
        "total": len(linhas),
        "acertos": acertos,
        "taxa_acerto": acertos / len(linhas) if linhas else 0,
        "tempo_medio_ms": statistics.mean(tempos) if tempos else 0,
        "tempo_mediano_ms": statistics.median(tempos) if tempos else 0,
        "tempo_maximo_ms": max(tempos) if tempos else 0,
        "por_tipo": por_tipo,
        "tipos_erro": Counter(l["tipo_erro"].split(" ")[0] for l in linhas if l["tipo_erro"]),
    }


# ---------- comparação dos modelos de resposta ----------

CRITERIOS = [
    ("cita_fonte", "Cita o link da fonte"),
    ("data_verificacao", "Mostra a data de verificação"),
    ("aviso_limite", "Traz aviso de limite/confirmação"),
    ("passo_a_passo", "Traz passos numerados"),
    ("continuidade", "Sugere assuntos para continuar"),
]


def avaliar_texto(texto, registro):
    return {
        "cita_fonte": registro["referencia"]["url"] in texto,
        "data_verificacao": "Verificada em" in texto,
        "aviso_limite": "Confirme" in texto or "canal oficial" in texto,
        "passo_a_passo": "  1. " in texto,
        "continuidade": "PARA CONTINUAR" in texto,
    }


def secoes(texto):
    """Sequência de seções presentes, para medir a consistência do formato."""
    marcadores = ["Resposta:", "Fonte:", "Confirme no canal", "RESPOSTA", "COMO FAZER",
                  "FONTE CONSULTADA", "ATENÇÃO", "PARA CONTINUAR"]
    return tuple(m for m in marcadores if m in texto)


def comparar_modelos(base, grafo, motor, perguntas):
    linhas, formatos = [], {m: [] for m in MODELOS}
    for p in perguntas:
        res = motor.buscar(p["pergunta"])
        if res.status != ENCONTRADA:
            continue  # sem orientação, as mensagens são iguais nos dois modelos
        relacionados = grafo.sugestoes_continuidade(res.registro["id"])
        for modelo in MODELOS:
            texto = formatar_orientacao(res.registro, base, modelo, relacionados)
            crit = avaliar_texto(texto, res.registro)
            formatos[modelo].append(secoes(texto))
            linhas.append({
                "pergunta_id": p["id"], "modelo": modelo, "orientacao": res.registro["id"],
                **{k: "SIM" if v else "NAO" for k, v in crit.items()},
                "nota_0a5": sum(crit.values()),
                "palavras": len(texto.split()),
            })
    resumo = {}
    for modelo in MODELOS:
        grupo = [l for l in linhas if l["modelo"] == modelo]
        if not grupo:
            continue
        formato_mais_comum, vezes = Counter(formatos[modelo]).most_common(1)[0]
        resumo[modelo] = {
            "respostas": len(grupo),
            "nota_media": statistics.mean(l["nota_0a5"] for l in grupo),
            "palavras_media": statistics.mean(l["palavras"] for l in grupo),
            "consistencia": vezes / len(grupo),
            **{k: sum(l[k] == "SIM" for l in grupo) / len(grupo) for k, _ in CRITERIOS},
        }
    return linhas, resumo


# ---------- gravação ----------

def gravar_csv(caminho, linhas):
    if not linhas:
        return
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", newline="", encoding="utf-8-sig") as arq:
        escritor = csv.DictWriter(arq, fieldnames=list(linhas[0]), delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)


def pct(valor):
    return f"{valor * 100:.1f}%".replace(".", ",")


def num(valor, casas=3):
    return f"{valor:.{casas}f}".replace(".", ",")


def gerar_relatorio(linhas, ind, comp_resumo, avisos_base):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    md = [
        "# Resultados dos testes (gerado automaticamente)",
        "",
        f"Gerado por `python src/avaliacao.py` em {agora}. "
        "Não edite à mão: rode o script de novo para atualizar.",
        "",
        "## Indicadores",
        "",
        "| Indicador | Valor |",
        "|---|---|",
        f"| Perguntas testadas | {ind['total']} |",
        f"| Respostas corretas | {ind['acertos']} |",
        f"| **Taxa de acerto** | **{pct(ind['taxa_acerto'])}** |",
        f"| Tempo médio de consulta | {num(ind['tempo_medio_ms'])} ms |",
        f"| Tempo mediano de consulta | {num(ind['tempo_mediano_ms'])} ms |",
        f"| Tempo máximo de consulta | {num(ind['tempo_maximo_ms'])} ms |",
        "",
        "### Acerto por tipo de pergunta",
        "",
        "| Tipo | Acertos | Taxa |",
        "|---|---|---|",
    ]
    for tipo, (ac, tot) in ind["por_tipo"].items():
        md.append(f"| {NOMES_TIPOS.get(tipo, tipo)} | {ac}/{tot} | {pct(ac / tot)} |")
    md += ["", "### Tipos de erro", "",
           "Respostas erradas (o assistente afirma algo que não responde a pergunta) são o erro mais "
           "grave; não responder ou pedir esclarecimento são erros seguros.", ""]
    md += [f"- {tipo}: {qtd}" for tipo, qtd in ind["tipos_erro"].items()] or ["- nenhum"]
    md += [
        "",
        "## Registro de cada pergunta",
        "",
        "| Id | Tipo | Pergunta | Esperado | Obtido | Acerto | Tempo (ms) |",
        "|---|---|---|---|---|---|---|",
    ]
    for l in linhas:
        pergunta = l["pergunta"].replace("|", "/") or "*(vazia)*"
        md.append(f"| {l['id']} | {l['tipo']} | {pergunta} | {l['esperado']} | {l['obtido']} | "
                  f"{l['acerto']} | {num(l['tempo_ms'], 4)} |")
    erros = [l for l in linhas if l["acerto"] == "NAO"]
    md += ["", "### Erros", ""]
    if erros:
        for l in erros:
            md.append(f"- **{l['id']}** \"{l['pergunta']}\": esperado `{l['esperado']}`, obtido "
                      f"`{l['obtido']}` - erro do tipo *{l['tipo_erro']}* "
                      f"(melhor candidato: {l['melhor_candidato']}).")
    else:
        md.append("- Nenhum erro neste conjunto de perguntas.")

    md += [
        "",
        "## Comparação dos modelos de resposta",
        "",
        "Critérios avaliados em cada resposta em que uma orientação foi encontrada "
        "(nota de 0 a 5 = soma dos critérios atendidos).",
        "",
        "| Critério | " + " | ".join(MODELOS[m]["nome"] for m in comp_resumo) + " |",
        "|---|" + "---|" * len(comp_resumo),
    ]
    for chave, nome in CRITERIOS:
        md.append(f"| {nome} | " + " | ".join(pct(comp_resumo[m][chave]) for m in comp_resumo) + " |")
    md.append("| **Nota média (0 a 5)** | " + " | ".join(f"**{num(comp_resumo[m]['nota_media'], 2)}**" for m in comp_resumo) + " |")
    md.append("| Consistência do formato | " + " | ".join(pct(comp_resumo[m]["consistencia"]) for m in comp_resumo) + " |")
    md.append("| Palavras por resposta (média) | " + " | ".join(num(comp_resumo[m]["palavras_media"], 0) for m in comp_resumo) + " |")
    md += ["", "Detalhe por resposta: `data/comparacao_modelos.csv`.", ""]
    if avisos_base:
        md += ["## Avisos da validação da base", ""] + [f"- {a}" for a in avisos_base] + [""]
    CAMINHO_RELATORIO.parent.mkdir(parents=True, exist_ok=True)
    CAMINHO_RELATORIO.write_text("\n".join(md), encoding="utf-8")


def rodar_avaliacao(base=None, imprimir=print):
    base = base or carregar_base()
    motor, grafo = MotorBusca(base), GrafoAssuntos(base)
    perguntas = carregar_perguntas()
    linhas = executar_testes(motor, perguntas)
    ind = indicadores(linhas)
    comp_linhas, comp_resumo = comparar_modelos(base, grafo, motor, perguntas)
    gravar_csv(CAMINHO_RESULTADOS, linhas)
    gravar_csv(CAMINHO_COMPARACAO, comp_linhas)
    gerar_relatorio(linhas, ind, comp_resumo, base.avisos)

    imprimir(f"{'Id':<4} {'Tipo':<13} {'Esperado':<17} {'Obtido':<17} {'Acerto':<6} Tempo(ms)")
    for l in linhas:
        imprimir(f"{l['id']:<4} {l['tipo']:<13} {l['esperado']:<17} {l['obtido']:<17} {l['acerto']:<6} {l['tempo_ms']:.4f}")
    imprimir("")
    imprimir(f"Taxa de acerto: {ind['acertos']}/{ind['total']} = {pct(ind['taxa_acerto'])}")
    for tipo, (ac, tot) in ind["por_tipo"].items():
        imprimir(f"  {NOMES_TIPOS.get(tipo, tipo):<16} {ac}/{tot} ({pct(ac / tot)})")
    imprimir(f"Tempo de consulta: média {num(ind['tempo_medio_ms'])} ms | "
             f"mediana {num(ind['tempo_mediano_ms'])} ms | máximo {num(ind['tempo_maximo_ms'])} ms")
    for m, r in comp_resumo.items():
        imprimir(f"{MODELOS[m]['nome']}: nota média {num(r['nota_media'], 2)}/5, "
                 f"consistência {pct(r['consistencia'])}, {num(r['palavras_media'], 0)} palavras")
    imprimir(f"\nArquivos gerados: {CAMINHO_RESULTADOS.relative_to(RAIZ_PROJETO)}, "
             f"{CAMINHO_COMPARACAO.relative_to(RAIZ_PROJETO)}, {CAMINHO_RELATORIO.relative_to(RAIZ_PROJETO)}")
    return ind


if __name__ == "__main__":
    import sys
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    rodar_avaliacao()
