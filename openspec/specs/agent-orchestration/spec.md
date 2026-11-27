# agent-orchestration Specification

## Purpose
Define como o copiloto encadeia roteamento, análise especializada e consolidação em um fluxo único, mantendo o seller do contexto em todas as etapas e permanecendo executável sem dependência de rede.

## Requirements

### Requirement: Estado de execução com seller obrigatório

O fluxo SHALL transportar um estado tipado que inclui o identificador do seller, a mensagem do usuário, o especialista selecionado, as recomendações propostas, os resultados de guardrail, a resposta final, o erro e um identificador de correlação. O identificador do seller SHALL ser obrigatório para iniciar a execução.

#### Scenario: Execução com seller presente

- **WHEN** o fluxo inicia com identificador de seller no estado
- **THEN** a execução prossegue
- **AND** o identificador do seller permanece disponível em todas as etapas

#### Scenario: Execução sem seller

- **WHEN** o fluxo inicia sem identificador de seller
- **THEN** a execução é interrompida
- **AND** nenhuma consulta de dados é realizada

### Requirement: Roteamento determinístico por intenção

O fluxo SHALL selecionar o especialista a partir da intenção da mensagem por regra determinística, sem chamada a modelo de linguagem. Uma intenção não reconhecida SHALL ser encaminhada para um caminho explícito de resposta padrão, não para erro.

#### Scenario: Intenção reconhecida

- **WHEN** a mensagem corresponde a uma intenção suportada
- **THEN** o especialista correspondente é selecionado
- **AND** a mesma mensagem sempre seleciona o mesmo especialista

#### Scenario: Intenção não reconhecida

- **WHEN** a mensagem não corresponde a nenhuma intenção suportada
- **THEN** o fluxo segue o caminho de resposta padrão
- **AND** a execução não falha

### Requirement: Ferramentas recebem seller do estado

Ferramentas determinísticas SHALL receber o identificador do seller do estado da execução e SHALL NOT aceitá-lo como parâmetro fornecido pelo modelo ou pelo texto do usuário.

#### Scenario: Chamada de ferramenta pelo fluxo

- **WHEN** o fluxo invoca uma ferramenta de análise
- **THEN** o identificador do seller é fornecido pelo estado
- **AND** a assinatura da ferramenta não expõe o identificador do seller como entrada do chamador

### Requirement: Execução completa sem dependência de rede

O fluxo SHALL concluir de ponta a ponta produzindo resposta e estado final sem realizar chamada a serviço externo de modelo de linguagem ou de dados remotos.

#### Scenario: Execução offline

- **WHEN** o fluxo é executado com o backend local de dados
- **THEN** a execução conclui com resposta preenchida
- **AND** nenhuma chamada de rede é realizada

### Requirement: Falha em etapa é registrada no estado

Quando uma etapa do fluxo levanta erro, o fluxo SHALL registrar a falha no estado e SHALL devolver uma resposta de erro controlada, sem propagar a exceção bruta ao chamador.

#### Scenario: Erro em etapa de análise

- **WHEN** uma etapa levanta erro durante a execução
- **THEN** o estado final registra a falha
- **AND** o chamador recebe resposta de erro controlada
- **AND** o identificador de correlação permite localizar a falha no log

### Requirement: Consolidação aplica guardrails e Top 3

Antes de devolver a resposta, o fluxo SHALL remover recomendações bloqueadas ou não avaliáveis e SHALL limitar o resultado às três de maior impacto financeiro estimado.

#### Scenario: Especialista propõe recomendação bloqueada

- **WHEN** o especialista propõe uma recomendação bloqueada por guardrail junto de outras aprovadas
- **THEN** a recomendação bloqueada é removida da resposta
- **AND** as aprovadas permanecem elegíveis

#### Scenario: Especialista propõe mais de três candidatas

- **WHEN** o especialista propõe mais de três recomendações aprovadas
- **THEN** a resposta final contém no máximo três
- **AND** são as de maior impacto financeiro estimado
