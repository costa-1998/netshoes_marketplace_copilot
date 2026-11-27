# seller-data Specification

## Purpose
Define como o copiloto lê a performance diária por SKU filho de um seller, garantindo que todo dado entregue ao domínio seja isolado por seller, tenha granularidade declarada e não invente informação quando a origem não a fornece.

## Requirements

### Requirement: Leitura sempre isolada por seller

Toda leitura de performance SHALL exigir um identificador de seller e SHALL NOT executar sem ele. A leitura SHALL retornar apenas registros pertencentes ao seller solicitado.

#### Scenario: Leitura de seller existente

- **WHEN** a leitura é solicitada para um seller que possui registros na origem
- **THEN** a resposta contém apenas registros desse seller
- **AND** nenhum registro de outro seller é exposto

#### Scenario: Leitura sem identificador de seller

- **WHEN** a leitura é solicitada sem identificador de seller
- **THEN** a operação é rejeitada antes de qualquer acesso à fonte de dados
- **AND** nenhum registro é retornado

#### Scenario: Seller inexistente

- **WHEN** a leitura é solicitada para um seller que não possui registros
- **THEN** a resposta é uma coleção vazia
- **AND** nenhum erro é levantado

### Requirement: Janela temporal explícita

Toda leitura SHALL receber data inicial e data final explícitas. A leitura SHALL rejeitar uma janela cuja data inicial seja posterior à data final, sem acessar a fonte.

#### Scenario: Janela válida

- **WHEN** a leitura recebe data inicial anterior ou igual à data final
- **THEN** apenas registros dentro da janela inclusiva são retornados

#### Scenario: Janela invertida

- **WHEN** a leitura recebe data inicial posterior à data final
- **THEN** a operação é rejeitada
- **AND** nenhuma leitura de arquivo ou de tabela ocorre

#### Scenario: Janela sem registros

- **WHEN** a janela é válida mas não cobre nenhuma data com dados
- **THEN** a resposta é uma coleção vazia

### Requirement: Granularidade declarada por registro

Todo registro SHALL declarar sua granularidade como `sku_filho` ou `sku_pai`. Um registro de granularidade `sku_filho` SHALL conter o identificador do SKU filho; a ausência desse identificador SHALL ser rejeitada na construção do registro.

#### Scenario: Registro de SKU filho completo

- **WHEN** um registro declara granularidade `sku_filho` e traz o identificador do SKU filho
- **THEN** o registro é aceito
- **AND** a granularidade fica disponível para as regras que a exigem

#### Scenario: Registro de SKU filho sem identificador

- **WHEN** um registro declara granularidade `sku_filho` sem identificador de SKU filho
- **THEN** a construção do registro é rejeitada

#### Scenario: Registro de SKU pai

- **WHEN** a origem entrega dados apenas no nível de SKU pai
- **THEN** o registro é aceito com granularidade `sku_pai`
- **AND** o identificador de SKU filho permanece ausente

### Requirement: Normalização de ausência e ruído numérico

A camada de leitura SHALL normalizar valores antes de expor o registro: texto vazio SHALL virar ausência, e resíduo de ponto flutuante próximo de zero SHALL ser tratado como zero. A conversão de zero em ausência SHALL ser decidida por coluna, nunca por tipo.

#### Scenario: Texto vazio

- **WHEN** uma coluna textual chega vazia
- **THEN** o campo correspondente é exposto como ausente
- **AND** não é exposto como string vazia

#### Scenario: Resíduo de ponto flutuante

- **WHEN** uma coluna numérica chega com valor cujo módulo é menor que `1e-9`
- **THEN** o valor é exposto como zero exato

#### Scenario: Zero com significado de ausência

- **WHEN** uma coluna cuja semântica de zero é "não medido" chega com valor zero
- **THEN** o campo correspondente é exposto como ausente

#### Scenario: Zero com significado de valor

- **WHEN** uma coluna monetária cuja semântica de zero é "dia sem venda" chega com valor zero
- **THEN** o valor zero é preservado

### Requirement: Campos sem origem permanecem ausentes

Quando a origem não fornece uma coluna necessária a uma regra de negócio, o campo correspondente SHALL ser exposto como ausente. O sistema SHALL NOT derivar esse campo de outra coluna sem uma derivação declarada.

#### Scenario: Campo sem origem declarada

- **WHEN** o modelo exige um campo que não existe na origem e não possui derivação declarada
- **THEN** o campo é exposto como ausente
- **AND** nenhum valor é inventado a partir de outra coluna

### Requirement: Fonte de dados indisponível falha de forma explícita

Uma implementação de leitura cujo backend não está implementado SHALL falhar levantando erro que nomeia a limitação. Ela SHALL NOT retornar coleção vazia, para não ser confundida com "seller sem dados".

#### Scenario: Backend não implementado

- **WHEN** a leitura é solicitada a uma implementação cujo backend ainda não foi implementado
- **THEN** a operação levanta erro com mensagem não vazia que identifica a limitação
- **AND** nenhuma coleção vazia é retornada

### Requirement: Guarda contra contaminação entre sellers

Se a fonte devolver um registro cujo identificador de seller difere do solicitado, a leitura SHALL descartar esse registro e SHALL registrar a inconsistência. O registro contaminado SHALL NOT chegar ao domínio.

#### Scenario: Registro de outro seller na resposta

- **WHEN** a fonte devolve um registro cujo identificador de seller difere do solicitado
- **THEN** o registro é descartado
- **AND** a inconsistência é registrada
- **AND** os demais registros válidos são retornados
