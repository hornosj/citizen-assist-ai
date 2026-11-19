# Grafo de assuntos (gerado por `python src/sistema.py --grafo`)

Cada caixa é uma orientação, agrupada pelo tema. Cada linha liga duas orientações relacionadas (campo `relacionados` da base). É por essas ligações que o assistente sugere "PARA CONTINUAR".

```mermaid
graph LR
  subgraph documentos["Documentos"]
    DOC01["DOC01: Carteira de Identidade Nacional"]
    DOC02["DOC02: Inscrição no CPF"]
    DOC03["DOC03: Carteira de Trabalho Digital"]
    DOC04["DOC04: Primeiro título de eleitor"]
    DOC05["DOC05: Passaporte comum"]
    DOC06["DOC06: Certidão de nascimento gratuita"]
    DOC07["DOC07: Conta gov.br e seus níveis"]
  end
  subgraph servicos["Serviços de saúde e assistência"]
    SER01["SER01: Cartão Nacional de Saúde"]
    SER02["SER02: Farmácia Popular"]
    SER03["SER03: Vacinação pelo SUS"]
    SER04["SER04: Cadastro Único"]
    SER05["SER05: Seguro-desemprego"]
    SER06["SER06: Serviços do INSS"]
  end
  subgraph direitos["Direitos do cidadão"]
    DIR01["DIR01: Direito de arrependimento em compras on-line"]
    DIR02["DIR02: Reclamar de uma empresa"]
    DIR03["DIR03: Juizado Especial Cível"]
    DIR04["DIR04: Assistência jurídica gratuita"]
    DIR05["DIR05: Atendimento prioritário à pessoa idosa"]
    DIR06["DIR06: Meia-entrada"]
    DIR07["DIR07: Direitos sobre seus dados pessoais"]
  end
  subgraph comunitario["Orientações comunitárias e canais de ajuda"]
    COM01["COM01: Disque 100"]
    COM02["COM02: Ligue 180"]
    COM03["COM03: SAMU 192"]
  end
  DOC01 --- DOC02
  DOC01 --- DOC07
  DOC01 --- DOC06
  DOC02 --- DOC07
  DOC02 --- DOC03
  DOC03 --- DOC07
  DOC03 --- SER05
  DOC04 --- DOC07
  DOC01 --- DOC04
  DIR04 --- DOC04
  DOC01 --- DOC05
  DOC05 --- DOC07
  DOC02 --- DOC05
  DOC02 --- DOC06
  DOC06 --- SER01
  DOC07 --- SER01
  DOC07 --- SER06
  SER01 --- SER03
  SER01 --- SER02
  SER02 --- SER04
  SER02 --- SER03
  COM03 --- SER03
  DIR06 --- SER04
  SER04 --- SER06
  SER05 --- SER06
  SER04 --- SER05
  DIR04 --- SER06
  DIR01 --- DIR02
  DIR01 --- DIR03
  DIR01 --- DIR07
  DIR02 --- DIR03
  DIR02 --- DIR04
  DIR03 --- DIR04
  COM01 --- DIR04
  DIR05 --- DIR06
  COM01 --- DIR05
  DIR05 --- SER06
  DIR02 --- DIR06
  DIR02 --- DIR07
  DIR07 --- DOC07
  COM01 --- COM02
  COM01 --- COM03
  COM02 --- DIR04
  COM02 --- COM03
  COM03 --- SER01
```
