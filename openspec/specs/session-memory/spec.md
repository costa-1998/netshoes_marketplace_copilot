# session-memory Specification

## Purpose
Define como o copiloto mantém o estado conversacional de cada seller entre turnos, com isolamento entre sessões e expiração por inatividade, sem acoplar os chamadores a um armazenamento específico.

## Requirements

### Requirement: Isolamento entre sessões

O estado de uma sessão SHALL ser legível e gravável apenas pela própria chave de sessão. Uma leitura com chave diferente SHALL NOT retornar dados de outra sessão.

#### Scenario: Leitura da própria sessão

- **WHEN** um estado é gravado sob uma chave de sessão e lido com a mesma chave
- **THEN** o estado previamente gravado é retornado

#### Scenario: Leitura cruzada entre sessões

- **WHEN** um estado é gravado sob uma chave e lido com outra chave
- **THEN** a leitura indica ausência de estado
- **AND** nenhum dado da primeira sessão é exposto

#### Scenario: Sobrescrita da própria sessão

- **WHEN** um novo estado é gravado sob uma chave que já possui estado
- **THEN** a leitura subsequente retorna o estado mais recente

### Requirement: Expiração por inatividade

O estado de uma sessão SHALL expirar após um intervalo configurável contado a partir da última escrita. Uma escrita SHALL renovar o prazo de expiração.

#### Scenario: Sessão expirada

- **WHEN** o intervalo configurado transcorre desde a última escrita sem nova escrita
- **THEN** a leitura indica ausência de estado
- **AND** o estado expirado não é retornado

#### Scenario: Escrita renova o prazo

- **WHEN** uma nova escrita ocorre antes de o intervalo transcorrer
- **THEN** o prazo de expiração passa a contar da nova escrita
- **AND** a leitura dentro do novo prazo retorna o estado

### Requirement: Remoção explícita de sessão

O sistema SHALL permitir remover o estado de uma sessão por sua chave. Após a remoção, a leitura dessa chave SHALL indicar ausência de estado.

#### Scenario: Remoção de sessão existente

- **WHEN** a sessão é removida por sua chave
- **THEN** a leitura subsequente indica ausência de estado

#### Scenario: Remoção de sessão inexistente

- **WHEN** a remoção é solicitada para uma chave sem estado
- **THEN** a operação conclui sem erro
- **AND** nenhuma outra sessão é afetada

### Requirement: Ausência de estado é explícita

Uma leitura de sessão inexistente ou expirada SHALL retornar ausência explícita, distinguível de um estado vazio armazenado.

#### Scenario: Sessão nunca criada

- **WHEN** a leitura é feita para uma chave que nunca recebeu escrita
- **THEN** o resultado é ausência explícita
- **AND** o chamador consegue distinguir de um estado vazio
