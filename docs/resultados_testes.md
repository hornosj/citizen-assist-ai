# Resultados dos testes (gerado automaticamente)

Gerado por `python src/avaliacao.py` em 19/11/2026 12:15. Não edite à mão: rode o script de novo para atualizar.

## Indicadores

| Indicador | Valor |
|---|---|
| Perguntas testadas | 54 |
| Respostas corretas | 50 |
| **Taxa de acerto** | **92,6%** |
| Tempo médio de consulta | 0,225 ms |
| Tempo mediano de consulta | 0,150 ms |
| Tempo máximo de consulta | 1,032 ms |

### Acerto por tipo de pergunta

| Tipo | Acertos | Taxa |
|---|---|---|
| Dúvidas diretas | 8/8 | 100,0% |
| Reformulações | 10/10 | 100,0% |
| Fora dos temas | 3/3 | 100,0% |
| Limitações | 6/6 | 100,0% |
| Às cegas lote 1 (usado nos ajustes) | 14/15 | 93,3% |
| Às cegas lote 2 (sem ajustes) | 9/12 | 75,0% |

### Tipos de erro

Respostas erradas (o assistente afirma algo que não responde a pergunta) são o erro mais grave; não responder ou pedir esclarecimento são erros seguros.

- nao_respondeu: 2
- respondeu_fora_da_base: 1
- pediu_esclarecimento: 1

## Registro de cada pergunta

| Id | Tipo | Pergunta | Esperado | Obtido | Acerto | Tempo (ms) |
|---|---|---|---|---|---|---|
| T01 | direta | Como tirar a Carteira de Identidade Nacional? | DOC01 | DOC01 | SIM | 0,0376 |
| T02 | direta | Como faço para fazer meu CPF? | DOC02 | DOC02 | SIM | 0,0226 |
| T03 | direta | Como pedir o seguro-desemprego? | SER05 | SER05 | SIM | 0,0239 |
| T04 | direta | Como emitir o passaporte? | DOC05 | DOC05 | SIM | 0,0219 |
| T05 | direta | Onde consigo o cartão do SUS? | SER01 | SER01 | SIM | 0,0268 |
| T06 | direta | Comprei pela internet e me arrependi, posso devolver? | DIR01 | DIR01 | SIM | 0,2435 |
| T07 | direta | Qual o número para denunciar violência contra a mulher? | COM02 | COM02 | SIM | 0,0440 |
| T08 | direta | Quem tem direito a meia-entrada? | DIR06 | DIR06 | SIM | 0,0421 |
| T09 | reformulacao | fui mandado embora, e agora? como recebo o auxílio desemprego | SER05 | SER05 | SIM | 0,0412 |
| T10 | reformulacao | preciso do rg novo | DOC01 | DOC01 | SIM | 0,0185 |
| T11 | reformulacao | pasaporte pra viajar | DOC05 | DOC05 | SIM | 0,2309 |
| T12 | reformulacao | remédio de graça para pressão alta | SER02 | SER02 | SIM | 0,0380 |
| T13 | reformulacao | não tenho dinheiro para pagar advogado | DIR04 | DIR04 | SIM | 0,0332 |
| T14 | reformulacao | minha avó tem prioridade na fila do banco? | DIR05 | DIR05 | SIM | 0,0367 |
| T15 | reformulacao | quero reclamar de uma loja que não resolve meu problema | DIR02 | DIR02 | SIM | 0,0404 |
| T16 | reformulacao | como deixar minha conta do governo nível ouro | DOC07 | DOC07 | SIM | 0,0358 |
| T17 | reformulacao | vacina de criança onde tomar | SER03 | SER03 | SIM | 0,0260 |
| T18 | reformulacao | alguém passando mal, chamar ambulância | COM03 | COM03 | SIM | 0,0301 |
| T19 | fora_do_tema | Qual a receita de bolo de cenoura? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,2624 |
| T20 | fora_do_tema | Quem ganhou o jogo de futebol ontem? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,4644 |
| T21 | fora_do_tema | Como tirar a carteira de motorista (CNH)? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,2242 |
| T22 | limitacao | *(vazia)* | ENTRADA_VAZIA | ENTRADA_VAZIA | SIM | 0,0004 |
| T23 | limitacao | documento | AMBIGUA | AMBIGUA | SIM | 0,0250 |
| T24 | limitacao | ???!!! | ENTRADA_INVALIDA | ENTRADA_INVALIDA | SIM | 0,0029 |
| T25 | limitacao | Qual o horário de funcionamento do posto de saúde do meu bairro? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,6339 |
| T26 | limitacao | benefício | AMBIGUA | AMBIGUA | SIM | 0,0194 |
| T27 | limitacao | meu cpf é 123.456.789-00, como faço a carteira de trabalho digital? | DOC03 | DOC03 | SIM | 0,0533 |
| T28 | cega | quero tirar meu primeiro documento de viagem pra fora do pais, como faço? | DOC05 | DOC05 | SIM | 0,0583 |
| T29 | cega | meu RG é antigo, preciso trocar por aquele modelo novo com CPF? | DOC01 | DOC01 | SIM | 0,4350 |
| T30 | cega | comprei um tenis pela internet e nao gostei, posso devolver e ter o dinheiro de volta? | DIR01 | DIR01 | SIM | 0,0555 |
| T31 | cega | nao tenho dinheiro pra pagar advogado, onde consigo ajuda de graça? | DIR04 | DIR04 | SIM | 0,0507 |
| T32 | cega | fui demitido semana passada, tenho direito a alguma ajuda do governo? | SER05 | SEM_RESPOSTA | NAO | 0,5157 |
| T33 | cega | minha mae ta passando mal, desmaiou, pra onde ligo urgente?? | COM03 | COM03 | SIM | 0,2869 |
| T34 | cega | completei 16 anos, como faço pra poder votar? | DOC04 | DOC04 | SIM | 0,2566 |
| T35 | cega | uma empresa usou meus dados sem eu autorizar, o que posso fazer? | DIR07 | DIR07 | SIM | 0,2615 |
| T36 | cega | onde consigo remedio de pressao mais barato ou de graça? | SER02 | SER02 | SIM | 0,2658 |
| T37 | cega | meu vizinho ta agredindo a esposa, tem algum numero pra denunciar? | COM02 | COM02 | SIM | 0,2839 |
| T38 | cega | sou estudante, tenho direito de pagar metade no cinema? | DIR06 | DIR06 | SIM | 0,2463 |
| T39 | cega | como faço pra renovar minha CNH que venceu? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,4750 |
| T40 | cega | quando vence o IPTU do meu apartamento e como parcelar? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,4501 |
| T41 | cega | como matricular meu filho na escola publica do bairro? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,6669 |
| T42 | cega | recebi uma multa de transito injusta, como recorro? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 1,0324 |
| T43 | cega2 | oi, como faço pra tirar meu cpf pela primeira vez? nunca tive e preciso pra abrir conta | DOC02 | SEM_RESPOSTA | NAO | 0,0619 |
| T44 | cega2 | carteira de trabalho agora é só no celular? onde baixo o app | DOC03 | DOC03 | SIM | 0,2458 |
| T45 | cega2 | preciso da certidao de nascimento da minha filha mas nao tenho dinheiro, tem como tirar de graça?? | DOC06 | DOC06 | SIM | 0,0637 |
| T46 | cega2 | o que significa conta gov.br prata e ouro? to tentando entrar num serviço e pede nível maior | DOC07 | DOC07 | SIM | 0,5027 |
| T47 | cega2 | perdi meu cartao do sus, como faço pra tirar outro? preciso do numero pra consulta | SER01 | SER01 | SIM | 0,4944 |
| T48 | cega2 | Boa tarde. Quais vacinas meu neto de 2 anos precisa tomar e onde posso levar ele no posto de saúde? | SER03 | SER03 | SIM | 0,0750 |
| T49 | cega2 | como entro no cadunico pra receber o bolsa familia? moro de aluguel com mais 3 pessoas | SER04 | SER04 | SIM | 0,2764 |
| T50 | cega2 | quero ver extrato do meu beneficio no meu inss mas esqueci como acessa o aplicativo | SER06 | SER06 | SIM | 0,5374 |
| T51 | cega2 | comprei uma geladeira e a loja nao resolve o defeito ha dois meses, posso reclamar no consumidor gov br? | DIR02 | DIR02 | SIM | 0,5819 |
| T52 | cega2 | como faço para tirar o passe livre de ônibus intermunicipal para estudante? | SEM_RESPOSTA | SEM_RESPOSTA | SIM | 0,3357 |
| T53 | cega2 | qual o prazo pra eu pedir a aposentadoria por idade rural? meu pai tem 60 anos e sempre trabalhou na roça | SEM_RESPOSTA | DIR05 | NAO | 0,4755 |
| T54 | cega2 | como faço pra registrar um imóvel no cartório depois da compra, preciso de escritura? | SEM_RESPOSTA | AMBIGUA | NAO | 0,4830 |

### Erros

- **T32** "fui demitido semana passada, tenho direito a alguma ajuda do governo?": esperado `SER05`, obtido `SEM_RESPOSTA` - erro do tipo *nao_respondeu* (melhor candidato: COM01 (3 pts, cobertura 20%)).
- **T43** "oi, como faço pra tirar meu cpf pela primeira vez? nunca tive e preciso pra abrir conta": esperado `DOC02`, obtido `SEM_RESPOSTA` - erro do tipo *nao_respondeu (certa entre as sugestoes)* (melhor candidato: DOC02 (3 pts, cobertura 17%)).
- **T53** "qual o prazo pra eu pedir a aposentadoria por idade rural? meu pai tem 60 anos e sempre trabalhou na roça": esperado `SEM_RESPOSTA`, obtido `DIR05` - erro do tipo *respondeu_fora_da_base* (melhor candidato: DIR05 (8 pts, cobertura 20%)).
- **T54** "como faço pra registrar um imóvel no cartório depois da compra, preciso de escritura?": esperado `SEM_RESPOSTA`, obtido `AMBIGUA` - erro do tipo *pediu_esclarecimento* (melhor candidato: DOC01 (6 pts, cobertura 40%)).

## Comparação dos modelos de resposta

Critérios avaliados em cada resposta em que uma orientação foi encontrada (nota de 0 a 5 = soma dos critérios atendidos).

| Critério | Modelo A - Direto | Modelo B - Estruturado |
|---|---|---|
| Cita o link da fonte | 100,0% | 100,0% |
| Mostra a data de verificação | 0,0% | 100,0% |
| Traz aviso de limite/confirmação | 50,0% | 100,0% |
| Traz passos numerados | 0,0% | 100,0% |
| Sugere assuntos para continuar | 0,0% | 100,0% |
| **Nota média (0 a 5)** | **1,50** | **5,00** |
| Consistência do formato | 50,0% | 100,0% |
| Palavras por resposta (média) | 57 | 178 |

Detalhe por resposta: `data/comparacao_modelos.csv`.
