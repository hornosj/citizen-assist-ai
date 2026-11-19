# Uso de inteligência artificial no projeto

## Onde a IA foi usada

| Etapa | Como a IA ajudou | Validação feita pela equipe |
|---|---|---|
| Planejamento da arquitetura | Assistente de código (Claude Code) sugeriu a divisão em módulos (`base_conhecimento`, `busca`, `navegacao`, `respostas`, `avaliacao`, `usabilidade`) e a estratégia de busca por índice invertido. | A equipe leu e executou cada módulo, rodou os 17 testes automáticos (`python -m unittest discover tests`) e conferiu se a estratégia usa só conteúdos das fases estudadas (listas, dicionários, arquivos, algoritmos de busca, avaliação). |
| Redação dos resumos da base | A IA redigiu as orientações resumidas a partir das páginas oficiais. | Cada resumo foi conferido com a página oficial (link no campo `referencia.url`). Os links foram abertos em 19/11/2026 (data registrada em `data_verificacao`). Quando um dado varia (por estado ou município) ou pode mudar (taxas, prazos), o registro foi marcado com `requer_confirmacao: true`. |
| Elaboração dos prompts | A IA ajudou a escrever e comparar os dois modelos de instrução (A e B). | A comparação não foi feita "no olho": `src/avaliacao.py` mede critérios objetivos em todas as respostas (ver `docs/modelos_de_prompt.md`). |
| Perguntas de teste às cegas | Dois agentes de IA independentes escreveram perguntas recebendo **só os títulos** dos assuntos, sem ver as palavras-chave da base (lotes 1 e 2, T28 a T54). | Usado para evitar que o teste fosse feito sob medida para o sistema. O lote 1 revelou erros (60% de acerto) e foi usado para melhorar o sistema; o lote 2 foi rodado uma única vez, sem ajustes depois, e é a estimativa mais honesta (75%). |
| Revisão de texto | Revisão de ortografia e clareza do README e das mensagens do sistema. | Leitura final pela equipe. |

## O que a IA NÃO faz no protótipo

- O assistente **não chama nenhuma IA generativa** durante o uso. As respostas são montadas a partir da base verificada por regras em Python. Isso foi uma decisão de projeto: em orientação cidadã, uma resposta inventada (alucinação) pode prejudicar alguém, e a regra do desafio pede que respostas de modelos externos sejam confrontadas com a base.
- Nenhum dado de usuário é enviado para serviços externos.

## Problemas encontrados na validação crítica

- **Informação desatualizada ou variável:** algumas páginas oficiais mudam (taxas do passaporte, regras do título de eleitor perto das eleições). Por isso cada registro tem data de verificação e o sistema avisa quando um registro passa de 365 dias sem revisão.
- **Página que bloqueia acesso automático:** o site do TSE recusou o acesso automatizado (erro 403) durante a conferência; o conteúdo foi confirmado pela busca e pela página de notícias do próprio TSE. Recomenda-se que a equipe abra o link manualmente antes da entrega.
- **Avaliação otimista:** na primeira rodada, as perguntas escritas pela própria equipe deram 100% de acerto. Só com as perguntas às cegas apareceram os erros reais. Lição: quem constrói o sistema não deve ser o único a escrever os testes.

## Responsabilidade

A equipe entende o funcionamento de todas as partes do código e é responsável pelo conteúdo entregue. As fontes citadas são públicas e oficiais; o assistente informa em todas as telas que não é canal oficial.
