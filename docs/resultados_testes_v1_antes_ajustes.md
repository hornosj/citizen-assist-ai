# Resultados dos testes - versão 1 (ANTES dos ajustes)

> Registro histórico, mantido para mostrar a evolução. Foi a primeira execução com as perguntas às cegas (lote 1), antes de ajustar o radical, a regra de aceitação e o vocabulário. A versão atual está em [resultados_testes.md](resultados_testes.md).

Gerado por `python src/avaliacao.py` em 19/11/2026 12:08. Não edite à mão: rode o script de novo para atualizar.

## Indicadores

| Indicador | Valor |
|---|---|
| Perguntas testadas | 42 |
| Respostas corretas | 36 |
| **Taxa de acerto** | **85,7%** |
| Tempo médio de consulta | 0,270 ms |
| Tempo mediano de consulta | 0,235 ms |
| Tempo máximo de consulta | 1,085 ms |

### Acerto por tipo de pergunta

| Tipo | Acertos | Taxa |
|---|---|---|
| Dúvidas diretas | 8/8 | 100,0% |
| Reformulações | 10/10 | 100,0% |
| Fora dos temas | 3/3 | 100,0% |
| Limitações | 6/6 | 100,0% |
| Validação às cegas | 9/15 | 60,0% |

## Registro de cada pergunta

| Id | Tipo | Pergunta | Esperado | Obtido | Acerto | Tempo (ms) |
|---|---|---|---|---|---|---|
| T01 | direta | Como tirar a Carteira de Identidade Nacional? | DOC01 | DOC01 | SIM | 0,0258 |
| T02 | direta | Como faço para fazer meu CPF? | DOC02 | DOC02 | SIM | 0,0154 |
| T03 | direta | Como pedir o seguro-desemprego? | SER05 | SER05 | SIM | 0,0176 |
| T04 | direta | Como emitir o passaporte? | DOC05 | DOC05 | SIM | 0,2671 |
| T05 | direta | Onde consigo o cartão do SUS? | SER01 | SER01 | SIM | 0,0192 |
| T06 | direta | Comprei pela internet e me arrependi, posso devolver? | DIR01 | DIR01 | SIM | 0,4802 |
| T07 | direta | Qual o número para denunciar violência contra a mulher? | COM02 | COM02 | SIM | 0,0307 |
| T08 | direta | Quem tem direito a meia-entrada? | DIR06 | DIR06 | SIM | 0,0286 |
| T09 | reformulacao | fui mandado embora, e agora? como recebo o auxílio desemprego | SER05 | SER05 | SIM | 0,0282 |
| T10 | reformulacao | preciso do rg novo | DOC01 | DOC01 | SIM | 0,0123 |
| T11 | reformulacao | pasaporte pra viajar | DOC05 | DOC05 | SIM | 0,2315 |
| T12 | reformulacao | remédio de graça para pressão alta | SER02 | SER02 | SIM | 0,0345 |
| T13 | reformulacao | não tenho dinheiro para pagar advogado | DIR04 | DIR04 | SIM | 0,2292 |
| T14 | reformulacao | minha avó tem prioridade na fila do banco? | DIR05 | DIR05 | SIM | 0,0250 |
| T15 | reformulacao | quero reclamar de uma loja que não resolve meu problema | DIR02 | DIR02 | SIM | 0,0267 |
| T16 | reformulacao | como deixar minha conta do governo nível ouro | DOC07 | DOC07 | SIM | 0,2669 |
| T17 | reformulacao | vacina de criança onde tomar | SER03 | SER03 | SIM | 0,0176 |
| T18 | reformulacao | alguém passando mal, chamar ambulância | COM03 | COM03 | SIM | 0,2652 |
| T19 | fora_do_tema | Qual a receita de bolo de cenoura? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,2603 |
| T20 | fora_do_tema | Quem ganhou o jogo de futebol ontem? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,6659 |
| T21 | fora_do_tema | Como tirar a carteira de motorista (CNH)? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,2345 |
| T22 | limitacao | *(vazia)* | ENTRADA_VAZIA | ENTRADA_VAZIA | SIM | 0,0004 |
| T23 | limitacao | documento | AMBIGUA | AMBIGUA | SIM | 0,0180 |
| T24 | limitacao | ???!!! | ENTRADA_INVALIDA | ENTRADA_INVALIDA | SIM | 0,0028 |
| T25 | limitacao | Qual o horário de funcionamento do posto de saúde do meu bairro? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,6319 |
| T26 | limitacao | benefício | AMBIGUA | AMBIGUA | SIM | 0,0125 |
| T27 | limitacao | meu cpf é 123.456.789-00, como faço a carteira de trabalho digital? | DOC03 | DOC03 | SIM | 0,0382 |
| T28 | cega | quero tirar meu primeiro documento de viagem pra fora do pais, como faço? | DOC05 | SEM_RESPOSTA | NAO | 0,0412 |
| T29 | cega | meu RG é antigo, preciso trocar por aquele modelo novo com CPF? | DOC01 | DOC01 | SIM | 0,6506 |
| T30 | cega | comprei um tenis pela internet e nao gostei, posso devolver e ter o dinheiro de volta? | DIR01 | SEM_RESPOSTA | NAO | 0,5097 |
| T31 | cega | nao tenho dinheiro pra pagar advogado, onde consigo ajuda de graça? | DIR04 | DIR04 | SIM | 0,2360 |
| T32 | cega | fui demitido semana passada, tenho direito a alguma ajuda do governo? | SER05 | SEM_RESPOSTA | NAO | 0,4987 |
| T33 | cega | minha mae ta passando mal, desmaiou, pra onde ligo urgente?? | COM03 | SEM_RESPOSTA | NAO | 0,4969 |
| T34 | cega | completei 16 anos, como faço pra poder votar? | DOC04 | SEM_RESPOSTA | NAO | 0,4299 |
| T35 | cega | uma empresa usou meus dados sem eu autorizar, o que posso fazer? | DIR07 | DIR07 | SIM | 0,2501 |
| T36 | cega | onde consigo remedio de pressao mais barato ou de graça? | SER02 | SER02 | SIM | 0,2676 |
| T37 | cega | meu vizinho ta agredindo a esposa, tem algum numero pra denunciar? | COM02 | SEM_RESPOSTA | NAO | 0,9301 |
| T38 | cega | sou estudante, tenho direito de pagar metade no cinema? | DIR06 | DIR06 | SIM | 0,4367 |
| T39 | cega | como faço pra renovar minha CNH que venceu? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,5364 |
| T40 | cega | quando vence o IPTU do meu apartamento e como parcelar? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,4417 |
| T41 | cega | como matricular meu filho na escola publica do bairro? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,6627 |
| T42 | cega | recebi uma multa de transito injusta, como recorro? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 1,0851 |

### Erros

- **T28** "quero tirar meu primeiro documento de viagem pra fora do pais, como faço?": esperado `DOC05`, obtido `SEM_RESPOSTA` (melhor candidato: DOC04 (4 pts, cobertura 40%)).
- **T30** "comprei um tenis pela internet e nao gostei, posso devolver e ter o dinheiro de volta?": esperado `DIR01`, obtido `SEM_RESPOSTA` (melhor candidato: DIR01 (9 pts, cobertura 43%)).
- **T32** "fui demitido semana passada, tenho direito a alguma ajuda do governo?": esperado `SER05`, obtido `SEM_RESPOSTA` (melhor candidato: COM01 (3 pts, cobertura 20%)).
- **T33** "minha mae ta passando mal, desmaiou, pra onde ligo urgente??": esperado `COM03`, obtido `SEM_RESPOSTA` (melhor candidato: COM03 (11 pts, cobertura 43%)).
- **T34** "completei 16 anos, como faço pra poder votar?": esperado `DOC04`, obtido `SEM_RESPOSTA` (melhor candidato: DIR05 (3 pts, cobertura 20%)).
- **T37** "meu vizinho ta agredindo a esposa, tem algum numero pra denunciar?": esperado `COM02`, obtido `SEM_RESPOSTA` (melhor candidato: COM02 (4 pts, cobertura 33%)).

## Comparação dos modelos de resposta

Critérios avaliados em cada resposta em que uma orientação foi encontrada (nota de 0 a 5 = soma dos critérios atendidos).

| Critério | Modelo A - Direto | Modelo B - Estruturado |
|---|---|---|
| Cita o link da fonte | 100,0% | 100,0% |
| Mostra a data de verificação | 0,0% | 100,0% |
| Traz aviso de limite/confirmação | 54,2% | 100,0% |
| Traz passos numerados | 0,0% | 100,0% |
| Sugere assuntos para continuar | 0,0% | 100,0% |
| **Nota média (0 a 5)** | **1,54** | **5,00** |
| Consistência do formato | 54,2% | 100,0% |
| Palavras por resposta (média) | 58 | 179 |

Detalhe por resposta: `data/comparacao_modelos.csv`.
