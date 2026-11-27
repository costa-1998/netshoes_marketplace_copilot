# Spec Delta

## Purpose

Define o que o copiloto pode e não pode recomendar a um seller, aplicando de forma determinística e auditável as travas de negócio do KAM Virtual — independentemente do que o modelo de linguagem sugira.

## ADDED Requirements

### Requirement: Granularidade de SKU filho exigida pelas análises

Toda análise de ruptura, preço, prazo, funil e Buy Box SHALL operar no nível de SKU filho. Quando o registro disponível é de granularidade `sku_pai`, a análise que exige SKU filho SHALL resultar em não avaliável, e SHALL NOT produzir recomendação a partir do dado agregado.

#### Scenario: Registro de SKU filho

- **WHEN** a análise recebe um registro de granularidade `sku_filho`
- **THEN** a regra é avaliada normalmente sobre o registro

#### Scenario: Registro de SKU pai em análise que exige SKU filho

- **WHEN** a análise recebe um registro de granularidade `sku_pai`
- **THEN** o resultado é não avaliável
- **AND** nenhuma recomendação é emitida a partir desse registro

### Requirement: Trava anti-canibalização 1P

Quando o SKU filho possui estoque próprio da Netshoes ativo na mesma data, o sistema SHALL sinalizar essa presença e SHALL NOT recomendar redução de preço nem entrada em campanha para disputar a Buy Box contra a própria Netshoes.

#### Scenario: 1P ativo com preço acima do concorrente

- **WHEN** o SKU filho tem 1P ativo e o preço praticado é maior que o preço de referência vencedor
- **THEN** a análise sinaliza a presença do 1P
- **AND** nenhuma recomendação de redução de preço ou de campanha é emitida para esse SKU filho

#### Scenario: 1P ativo com gargalo logístico

- **WHEN** o SKU filho tem 1P ativo e o desvio é de prazo, não de preço
- **THEN** a análise sinaliza a presença do 1P
- **AND** apenas recomendações que não disputem a Buy Box por preço são emitidas

#### Scenario: 1P inativo

- **WHEN** o SKU filho não tem 1P ativo
- **THEN** a trava não bloqueia a análise
- **AND** as demais regras decidem a recomendação

#### Scenario: Presença de 1P desconhecida

- **WHEN** o indicador de 1P ativo está ausente
- **THEN** o resultado é não avaliável
- **AND** nenhuma recomendação de disputa de preço é emitida

### Requirement: Priorização entre preço e logística na Buy Box

Quando o preço praticado não é maior que o preço de referência e a taxa de vitória de Buy Box está abaixo de 50% com desvio positivo de prazo, o diagnóstico SHALL apontar gargalo logístico e SHALL NOT recomendar redução de preço. Redução de preço SHALL ser recomendada apenas quando o preço praticado é maior que o preço de referência.

#### Scenario: Preço competitivo com Buy Box baixa

- **WHEN** o desvio de preço é menor ou igual a zero, a taxa de vitória de Buy Box é menor que 50% e o desvio de prazo é positivo
- **THEN** o diagnóstico aponta gargalo logístico de prazo ou frete
- **AND** nenhuma recomendação de redução de preço é emitida

#### Scenario: Preço acima do concorrente com margem disponível

- **WHEN** o desvio de preço é positivo e existe margem sustentável
- **THEN** a redução de preço é uma recomendação permitida

#### Scenario: Taxa de vitória de Buy Box indisponível

- **WHEN** a taxa de vitória de Buy Box está ausente
- **THEN** o resultado é não avaliável
- **AND** nenhuma recomendação de preço ou de logística é emitida com base nessa regra

### Requirement: Proteção contra ruptura em Curva A

Quando o SKU é de Curva A e a cobertura de estoque é de três dias ou menos, o sistema SHALL bloquear qualquer recomendação de redução de preço para acelerar giro e SHALL priorizar alerta de reposição de estoque.

#### Scenario: Curva A em ruptura iminente

- **WHEN** a curva do SKU é A e a cobertura é de três dias ou menos
- **THEN** qualquer recomendação de redução de preço é bloqueada
- **AND** a reposição de estoque é priorizada

#### Scenario: Curva A com cobertura suficiente

- **WHEN** a curva do SKU é A e a cobertura é maior que três dias
- **THEN** o bloqueio por ruptura não se aplica
- **AND** as demais regras decidem a recomendação

#### Scenario: Curva do SKU indisponível

- **WHEN** a curva do SKU está ausente
- **THEN** o resultado é não avaliável
- **AND** nenhuma recomendação de redução de preço é emitida com base nessa regra

### Requirement: Diagnóstico de abandono de funil e cancelamento

O sistema SHALL identificar queda acentuada entre as etapas do funil de conversão como indício de atrito de checkout, e SHALL sinalizar alerta operacional quando a razão entre cancelamentos e compras faturadas for maior que 0,15.

#### Scenario: Queda entre etapas do funil

- **WHEN** a conversão entre duas etapas consecutivas do funil cai de forma acentuada em relação à etapa anterior
- **THEN** o diagnóstico aponta atrito naquela etapa
- **AND** a etapa de maior queda é identificada

#### Scenario: Taxa de cancelamento acima do limite

- **WHEN** a razão entre cancelamentos e compras faturadas é maior que 0,15
- **THEN** um alerta operacional de ruptura fantasma ou atraso de expedição é emitido

#### Scenario: Etapa do funil ausente

- **WHEN** uma etapa necessária do funil está ausente
- **THEN** a análise daquela transição é não avaliável
- **AND** nenhum atrito é inventado para a etapa

### Requirement: Piso de rentabilidade na simulação de preço

Toda simulação que reduza o preço praticado para o preço de referência vencedor SHALL recalcular a rentabilidade projetada considerando o percentual de comissão vigente e SHALL rejeitar a simulação quando a rentabilidade projetada não permanecer acima de 5%.

#### Scenario: Simulação mantém rentabilidade acima do piso

- **WHEN** a simulação reduz o preço e a rentabilidade projetada permanece acima de 5%
- **THEN** a simulação é aceita
- **AND** a rentabilidade projetada é reportada

#### Scenario: Simulação viola o piso de rentabilidade

- **WHEN** a simulação reduz o preço e a rentabilidade projetada fica em 5% ou menos
- **THEN** a simulação é rejeitada
- **AND** o motivo da rejeição é reportado

#### Scenario: Dado de rentabilidade indisponível

- **WHEN** o percentual de comissão ou a margem necessária à simulação está ausente
- **THEN** o resultado é não avaliável
- **AND** nenhuma simulação aprovada é reportada

### Requirement: Limite de três recomendações priorizadas

Toda resposta final SHALL consolidar no máximo três recomendações, ordenadas por impacto financeiro estimado. Apenas recomendações aprovadas SHALL ocupar vaga; recomendações bloqueadas ou não avaliáveis SHALL NOT preencher vaga.

#### Scenario: Mais de três candidatas aprovadas

- **WHEN** existem mais de três recomendações aprovadas
- **THEN** apenas as três de maior impacto financeiro estimado são retornadas
- **AND** as demais são descartadas

#### Scenario: Empate na fronteira do corte

- **WHEN** duas recomendações empatam no impacto estimado na terceira posição
- **THEN** o desempate é determinístico
- **AND** o resultado é estável entre execuções com os mesmos dados

#### Scenario: Candidatas bloqueadas ou não avaliáveis

- **WHEN** existem recomendações bloqueadas ou não avaliáveis junto de aprovadas
- **THEN** apenas as aprovadas concorrem às vagas
- **AND** nenhuma recomendação bloqueada ou não avaliável é retornada

#### Scenario: Nenhuma candidata aprovada

- **WHEN** nenhuma recomendação é aprovada
- **THEN** a resposta não contém recomendações
- **AND** a ausência é explicada ao seller

### Requirement: Resultado de guardrail com motivo auditável

Todo resultado de guardrail SHALL ser um de três estados — aprovado, bloqueado ou não avaliável — acompanhado do identificador do guardrail e de um motivo legível. Um guardrail sem dado de suporte SHALL resultar em não avaliável, nunca em aprovação.

#### Scenario: Guardrail sem dado de suporte

- **WHEN** um guardrail não dispõe do dado necessário para decidir
- **THEN** o resultado é não avaliável
- **AND** o motivo identifica o dado ausente

#### Scenario: Guardrail explicitamente violado

- **WHEN** um guardrail identifica uma violação de regra de negócio
- **THEN** o resultado é bloqueado
- **AND** o motivo identifica a regra violada

#### Scenario: Auditoria da decisão

- **WHEN** um resultado de guardrail é consultado posteriormente
- **THEN** o estado, o identificador do guardrail e o motivo estão disponíveis
- **AND** a decisão pode ser reconstruída sem reexecutar o cálculo