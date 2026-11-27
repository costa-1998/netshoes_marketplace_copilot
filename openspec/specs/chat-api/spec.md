# chat-api Specification

## Purpose
Define a superfície HTTP pela qual o seller interage com o copiloto, garantindo contexto de sessão confiável, health check que distingue dependência indisponível e respostas de erro que não vazam detalhe interno.

## Requirements

### Requirement: Health check com diagnóstico de dependência

O serviço SHALL expor um endpoint de saúde que reporta os backends de dados e de memória em uso. Quando uma dependência selecionada não está operacional, o endpoint SHALL reportar indisponibilidade nomeando a dependência.

#### Scenario: Serviço saudável

- **WHEN** o health check é consultado com todos os backends operacionais
- **THEN** a resposta indica serviço disponível
- **AND** os backends em uso são reportados

#### Scenario: Dependência selecionada indisponível

- **WHEN** o health check é consultado com um backend selecionado que não está implementado
- **THEN** a resposta indica indisponibilidade
- **AND** a dependência indisponível é nomeada

### Requirement: Endpoint de conversa

O serviço SHALL expor um endpoint de conversa que recebe a mensagem do seller e devolve a resposta consolidada. A mensagem vazia SHALL ser rejeitada com erro de validação.

#### Scenario: Mensagem válida

- **WHEN** o endpoint recebe uma mensagem não vazia
- **THEN** a resposta contém a resposta do copiloto
- **AND** a resposta respeita o limite de três recomendações

#### Scenario: Mensagem vazia

- **WHEN** o endpoint recebe mensagem vazia
- **THEN** a requisição é rejeitada com erro de validação
- **AND** o fluxo de análise não é executado

### Requirement: Seller derivado do contexto da sessão

O serviço SHALL derivar o identificador do seller do contexto de sessão, e SHALL criar uma sessão quando não houver uma. Um identificador de seller presente no corpo da requisição SHALL NOT sobrescrever o valor da sessão.

#### Scenario: Sessão existente

- **WHEN** a requisição chega com uma sessão ativa
- **THEN** o seller da sessão é usado na análise

#### Scenario: Sessão ausente

- **WHEN** a requisição chega sem sessão ativa
- **THEN** uma sessão é criada
- **AND** o seller associado a ela é usado na análise

#### Scenario: Seller divergente no corpo da requisição

- **WHEN** o corpo da requisição contém um identificador de seller diferente do da sessão
- **THEN** o valor da sessão prevalece
- **AND** o valor do corpo é ignorado

### Requirement: Erros sem vazamento de detalhe interno

O serviço SHALL mapear erros de domínio para respostas de erro do cliente e falhas inesperadas para erro interno, sempre com um identificador de correlação e sem stack trace, nome de tabela, caminho de arquivo ou credencial no corpo da resposta.

#### Scenario: Erro de domínio

- **WHEN** uma requisição viola uma regra de domínio
- **THEN** a resposta é um erro de cliente
- **AND** a mensagem é legível e não expõe detalhe interno

#### Scenario: Falha inesperada

- **WHEN** uma falha não tratada ocorre durante a requisição
- **THEN** a resposta é um erro interno com identificador de correlação
- **AND** o corpo não contém stack trace, nome de tabela, caminho de arquivo ou credencial

### Requirement: Configuração inválida impede a inicialização

O serviço SHALL validar a configuração na criação e SHALL falhar ao iniciar quando um backend configurado está fora dos valores aceitos.

#### Scenario: Configuração válida

- **WHEN** o serviço é criado com backends válidos
- **THEN** a criação conclui
- **AND** o health check responde com sucesso

#### Scenario: Configuração inválida

- **WHEN** o serviço é criado com um backend fora dos valores aceitos
- **THEN** a criação falha
- **AND** a mensagem lista os valores aceitos

### Requirement: Portas resolvidas por configuração

As rotas SHALL obter as implementações de dados e de memória a partir da configuração, e SHALL NOT instanciá-las diretamente.

#### Scenario: Resolução por backend configurado

- **WHEN** o backend de dados está configurado como local
- **THEN** a rota usa a implementação local
- **AND** quando configurado como BigQuery, a rota usa a implementação correspondente
