# Modelos de prompt (instruções de resposta)

O protótipo não usa um modelo de linguagem pago. Cada "modelo" de resposta é composto por:

1. **Uma instrução escrita** (o texto que seria o *prompt de sistema* de uma IA generativa);
2. **Uma função em Python** (`src/respostas.py`) que aplica essa instrução de forma determinística sobre a orientação encontrada na base.

Com isso, a resposta **nunca contém nada que não esteja na base verificada**: a "IA" do protótipo decide *o que mostrar e como mostrar*, mas não inventa conteúdo.

## Modelo A: Direto (instrução mínima)

```text
Você é um assistente de informações. Responda à pergunta usando a orientação
encontrada na base e cite a fonte.
```

Estratégia: definir só o **papel** e a **obrigação de citar a fonte**. Exemplo de saída:

```text
Resposta: A inscrição no CPF é gratuita quando feita diretamente pela Receita
Federal, pela página do serviço no gov.br. Se for feita em unidades
conveniadas (...), é cobrada uma taxa de R$ 7,00. Não é preciso usar intermediários.
Fonte: https://www.gov.br/pt-br/servicos/inscrever-no-cpf
```

## Modelo B: Estruturado (instrução completa) — **modelo adotado**

```text
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
7. Não peça dados pessoais (CPF, endereço, telefone, e-mail).
```

Estratégias de prompt usadas: **papel** (persona e o que ela *não* é), **público-alvo**, **restrição de fonte** (só a base), **formato de saída fixo**, **obrigação de citar fonte e data**, **regra de recusa** (quando não houver base) e **regra de privacidade**.

Exemplo de saída (`python src/sistema.py --pergunta "como fazer o CPF"`):

```text
----------------------------------------------------------------------------
DOC02 | Inscrição no CPF
Tema: Documentos > Identificação civil (CIN e CPF)
----------------------------------------------------------------------------
RESPOSTA
  A inscrição no CPF é gratuita quando feita diretamente pela Receita
  Federal (...). Não é preciso usar intermediários.
COMO FAZER
  1. Acesse no gov.br o serviço "Inscrever Cidadão no Cadastro de Pessoas
     Físicas (CPF)".
  2. Preencha os dados pedidos e siga as instruções da página.
  3. Se preferir atendimento presencial, procure uma unidade conveniada.
FONTE CONSULTADA
  Receita Federal (gov.br) - Inscrever Cidadão no Cadastro de Pessoas Físicas (CPF)
  https://www.gov.br/pt-br/servicos/inscrever-no-cpf
  Verificada em 19/11/2026
ATENÇÃO
  Orientação informativa. Em caso de dúvida, consulte o canal oficial citado.
PARA CONTINUAR, VOCÊ TAMBÉM PODE CONSULTAR
  [1] DOC01 - Carteira de Identidade Nacional (CIN, o novo RG)
  [2] DOC07 - Conta gov.br e seus níveis
  [3] DOC03 - Carteira de Trabalho Digital
```

## Comparação objetiva

`src/avaliacao.py` aplica os dois modelos a todas as perguntas de teste em que uma orientação foi encontrada e verifica, em cada resposta, cinco critérios (nota de 0 a 5). Resultado da execução registrada em [resultados_testes.md](resultados_testes.md):

| Critério | Modelo A | Modelo B |
|---|---|---|
| Cita o link da fonte | 100% | 100% |
| Mostra a data de verificação | 0% | 100% |
| Traz aviso de limite/confirmação | 50% (só quando a orientação exige) | 100% |
| Traz passos numerados | 0% | 100% |
| Sugere assuntos para continuar | 0% | 100% |
| **Nota média (0 a 5)** | **1,50** | **5,00** |
| Consistência do formato (respostas com a mesma estrutura) | 50% | 100% |
| Palavras por resposta (média) | 57 | 178 |

## Justificativa da escolha

O **Modelo B** foi adotado como padrão porque:

- **É mais claro:** separa "o que é" (RESPOSTA) de "o que fazer" (COMO FAZER), e os passos numerados facilitam seguir a orientação;
- **É mais consistente:** 100% das respostas têm a mesma estrutura; no Modelo A, metade tem a linha de aviso e metade não, o que confunde quem usa;
- **É mais confiável:** mostra a data de verificação (o cidadão sabe se a informação pode estar velha) e sempre lembra que o assistente não é canal oficial;
- **Facilita a navegação:** a seção PARA CONTINUAR liga o assunto aos relacionados (grafo).

**Custo do Modelo B:** a resposta é cerca de 3 vezes mais longa (178 contra 57 palavras). Para leitores de tela ou celulares isso pesa, e por isso o Modelo A continua disponível no menu (opção 4) e pela linha de comando (`--modelo A`). Uma melhoria possível é um modo "resumo" que mostra só RESPOSTA e FONTE e oferece "ver passo a passo".

## Se um modelo de linguagem fosse conectado

A instrução do Modelo B foi escrita para ser usada como *prompt de sistema*. O fluxo seguro seria:

1. A busca da base (já implementada) recupera a orientação;
2. Só esse texto é enviado ao modelo como contexto, junto com a instrução B;
3. A resposta do modelo é **conferida** antes de ser mostrada: precisa conter o link da fonte do registro e não pode trazer números (valores, prazos) que não estejam no registro; se falhar, mostra-se a resposta determinística do Modelo B.
