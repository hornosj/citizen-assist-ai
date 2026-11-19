# Teste de facilidade de uso

## Objetivo

Verificar se uma pessoa que não participou do projeto consegue, sozinha, encontrar orientações no assistente, entender a fonte e perceber os limites das respostas.

## Como aplicar (10 a 15 minutos)

1. Escolha um participante que **não** participou do desenvolvimento (familiar, colega). Explique que quem está sendo testado é o sistema, não a pessoa.
2. O observador (integrante da equipe) roda:

   ```bash
   python src/sistema.py --usabilidade
   ```

3. Informe só um **código** para o participante (P1, P2...). Não registre nome, idade exata ou outro dado pessoal.
4. Para cada tarefa, leia o enunciado em voz alta e deixe o participante usar o teclado. O observador **não ajuda**; só anota onde a pessoa hesitou.
5. Quando a pessoa disser que terminou, ela escolhe `[0] Terminei a tarefa`. O programa mede o tempo e o número de consultas e pergunta:
   - (observador) se concluiu: S, P (parcial) ou N;
   - (participante) a dificuldade, de 1 (muito fácil) a 5 (muito difícil);
   - um comentário curto sobre a dificuldade observada.
6. Ao final, o relatório é gerado em `docs/resultados_usabilidade.md` e os dados brutos ficam em `data/usabilidade.csv`. Para mais participantes, basta rodar de novo: os resultados se acumulam.

## Roteiro de tarefas

| Tarefa | Enunciado | O que avalia | Critério de sucesso |
|---|---|---|---|
| U1 | Descubra se a primeira via da Carteira de Identidade Nacional (novo RG) é paga. | Pergunta livre | Diz que a 1ª via é gratuita e aponta a fonte |
| U2 | Você comprou um produto pela internet e se arrependeu. Descubra em quantos dias pode desistir. | Pergunta com linguagem do dia a dia | Diz "7 dias" |
| U3 | Usando o **menu de temas** (sem digitar pergunta), encontre o telefone para emergência médica. | Navegação hierárquica | Chega ao SAMU 192 |
| U4 | Pergunte algo que o assistente provavelmente não sabe (ex.: IPTU) e diga o que ele fez. | Percepção do limite | Entende que o assistente avisou que não sabe e sugeriu outros temas |
| U5 | Abra a orientação sobre o CPF e, a partir dela, navegue para um assunto relacionado. | Navegação pelo grafo | Abre um assunto pela seção PARA CONTINUAR |

## Indicadores

- **Taxa de conclusão** = tarefas concluídas (S) / tarefas aplicadas;
- **Tempo médio por tarefa** (segundos);
- **Consultas por tarefa** (quantas orientações ou mensagens a pessoa abriu até concluir; quanto menor, mais direto);
- **Dificuldade média** (1 a 5).

## Resultados

> **A preencher pela equipe depois de aplicar o teste.** Os números saem prontos em `docs/resultados_usabilidade.md`. Copie aqui o resumo e escreva a interpretação:
>
> - Participante(s): P1 (perfil geral, ex.: "adulto, usa celular todo dia, nunca usou o sistema")
> - Taxa de conclusão: __%  | Tempo médio: __ s | Dificuldade média: __
> - Dificuldades observadas: ...
> - O que mudaríamos: ...

## Limitações deste teste

- Poucos participantes (1 a 3) não representam a população; servem para achar problemas grandes, não para medir com precisão.
- O participante sabe que está sendo observado e tende a se esforçar mais que no uso real.
- O tempo inclui a leitura do enunciado e o tempo de digitação, que varia de pessoa para pessoa.
- A interface é textual: pessoas com pouca familiaridade com computador podem ter mais dificuldade do que teriam num aplicativo.
