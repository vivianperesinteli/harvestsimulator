# Roteiro de Teste de Usabilidade
**Crop Decision Intelligence System — Grupo 2 · Inteli × Bayer CropScience**
Data: 16/06/2026 · Módulo 6 — Design, Sprint 4

---

## Contexto do teste

O simulador apoia produtores de soja de Mato Grosso na tomada de decisão sobre manejo da safra. O teste visa verificar:
- **Clareza:** o sistema hierarquiza e representa informações complexas de forma didática?
- **Eficiência:** as informações apresentadas são suficientes para embasar diferentes tomadas de decisão?

**Acesso:** https://empathetic-passion-production.up.railway.app
Login: `demo` · Senha: `demo123`

---

## Divisão de funções por estação

| Função | Responsabilidade |
|---|---|
| **Mediador(a)** | Apresenta o contexto, lê as tarefas em voz alta, faz as perguntas de follow-up, não interfere nas ações do usuário |
| **Secretário(a) nº 1** | Anota na planilha o que o usuário faz, onde hesita, o que fala, erros e comentários espontâneos — em tempo real |
| **Secretário(a) nº 2** | Monitora aspectos técnicos (sistema rodando, cronômetro por tarefa), compila observações ao final e registra métricas quantitativas |

---

## Perfil do participante (leia em voz alta antes de começar)

> "Você é um produtor de soja de Sorriso, MT. Você tem uma propriedade de tamanho médio (entre 50 e 200 hectares), solo argiloso bem estruturado e pH adequado. A previsão climática para esta safra é de **La Niña** — ou seja, risco de veranicos prolongados. Você nunca usou esta ferramenta antes. Vamos pedir que você realize algumas tarefas e, enquanto faz isso, pense em voz alta — diga o que está vendo, o que está pensando e o que está tentando fazer."

---

## Tarefas

### Tarefa 1 — Configurar o campo e rodar a simulação
**Tempo estimado:** 5–8 min

**Descrição para o mediador:**
> "Com base no perfil que acabei de ler, preencha as informações do seu campo e tome as decisões de manejo da sua safra. Quando estiver satisfeito com as escolhas, rode a simulação."

**Etapas esperadas pelo sistema:**
1. Preencher o Contexto do Campo (região, textura, pH, drenagem, tipo de solo, área, previsão climática)
2. Preencher as Decisões de Manejo (janela de plantio no calendário, cultivar, TSI, densidade, manejo de doenças, semeadora)
3. Revisar os dados na tela de revisão
4. Clicar em "Confirmar & Simular"

**O que observar e anotar:**
- O usuário entende que há 3 etapas (indicador de progresso)?
- Consegue usar o calendário interativo para escolher a janela de plantio?
- Entende os termos técnicos (TSI, ENSO, Latossolo)? Hesita em algum?
- Lê as dicas de contexto abaixo de cada campo ("input-help")?
- Revisa os dados antes de confirmar ou clica direto?

**Perguntas de follow-up (após concluir):**
- "Alguma pergunta foi difícil de responder? Por quê?"
- "Você entendeu o que cada campo pede de você?"

---

### Tarefa 2 — Interpretar os resultados e explicar a recomendação principal
**Tempo estimado:** 5–7 min

**Descrição para o mediador:**
> "Olhando para os resultados que aparecem agora, me diga: qual é a melhor recomendação para a sua safra? O que ela significa na prática? O sistema está te ajudando a tomar uma decisão ou apenas apresentando dados?"

**Etapas esperadas pelo sistema:**
- Usuário lê os quatro cartões de métricas no topo (referência regional, ponto de partida do campo, produtividade esperada, melhor cenário)
- Lê o card de recomendação #1 (janela, densidade, manejo de doenças, produtividade esperada, intervalo de 90%, risco)
- Localiza a diferença entre a sua escolha e a recomendação top

**O que observar e anotar:**
- Consegue localizar a recomendação principal sem auxílio?
- Entende a diferença entre "ponto de partida do campo" e "produtividade esperada"?
- Interpreta corretamente o intervalo de 90% (P5–P95)?
- Lê os cenários climáticos dentro do card (Seca / Normal / Úmido)?
- Abre o expander "Como aplicar"?
- Percebe e entende os critérios de decisão tags (Bayes EV, Wald etc.)?

**Perguntas de follow-up:**
- "O que você faria de diferente na sua safra depois de ver isso?"
- "Alguma informação estava faltando para você tomar uma decisão?"
- "Você confiaria nessa recomendação? Por quê?"

---

### Tarefa 3 — Avaliar o risco via Monte Carlo
**Tempo estimado:** 4–6 min

**Descrição para o mediador:**
> "O sistema tem uma seção de simulação de risco. Encontre-a, rode uma simulação e me diga: qual a chance da sua safra ficar abaixo da média histórica de Mato Grosso?"

**Etapas esperadas pelo sistema:**
1. Navegar até "Monte Carlo" pelo menu lateral
2. Configurar o número de iterações e o limiar de risco
3. Clicar em "Rodar Monte Carlo"
4. Ler o histograma, o P5/P95, e o percentual de risco

**O que observar e anotar:**
- Encontra a página Monte Carlo sem ajuda?
- Entende o que é o "limiar de risco" (slider)?
- Consegue ler o histograma e identificar a probabilidade de ficar abaixo da referência?
- Interpreta o tornado chart (qual variável mais impacta o resultado)?
- Confunde média da simulação com produtividade esperada dos resultados?

**Perguntas de follow-up:**
- "O que o gráfico de barras (tornado) está dizendo?"
- "Com base nessa análise, você mudaria alguma decisão de manejo?"

---

### Tarefa 4 — Avaliar o impacto de atualizar cultivar ou semeadora
**Tempo estimado:** 3–5 min

**Descrição para o mediador:**
> "Você está pensando em investir em uma semeadora de maior precisão na próxima safra. Descubra no sistema o quanto isso mudaria a sua produtividade esperada."

**Etapas esperadas pelo sistema:**
- Usuário localiza a seção "O que muda se você atualizar cultivar, TSI ou semeadora?" nos resultados
- Lê o card de Semeadora com o delta estimado (ex: +2,0 sc/ha)
- Expande as opções para ver todas as alternativas

**O que observar e anotar:**
- Localiza a seção de potencial de upgrade sem indicação?
- Entende que o delta é uma estimativa do modelo e não uma garantia?
- Percebe o aviso de "consulte seu agrônomo"?
- Consegue comparar as opções de semeadora entre si?

**Perguntas de follow-up:**
- "Essa informação seria útil para uma decisão real de investimento? O que você precisaria saber a mais?"

---

### Tarefa 5 — Exportar o relatório da recomendação
**Tempo estimado:** 2–3 min

**Descrição para o mediador:**
> "Você quer compartilhar essa análise com o seu agrônomo. Como você faria isso usando o sistema?"

**Etapas esperadas pelo sistema:**
- Usuário localiza os botões de exportação (PDF individual por recomendação ou Relatório Completo)
- Clica em "⬇ Relatório Completo (PDF)" ou "⬇ Download PDF #1"
- O arquivo é gerado e baixado

**O que observar e anotar:**
- Localiza os botões de export sem ajuda?
- Tenta usar o botão de CSV ou de impressão em vez de PDF?
- Compreende a diferença entre "PDF da recomendação #1" e "Relatório Completo"?

**Perguntas de follow-up:**
- "Para quem você enviaria esse relatório?"
- "O PDF contém o que você precisaria para uma conversa com o agrônomo?"

---

## Pergunta final (após todas as tarefas)

> "Em uma palavra ou frase, como você descreveria a experiência de usar esse sistema?"

> "Se você pudesse mudar uma coisa, o que seria?"

---

## Métricas quantitativas (Secretário nº 2 registra)

| Métrica | Tarefa 1 | Tarefa 2 | Tarefa 3 | Tarefa 4 | Tarefa 5 |
|---|---|---|---|---|---|
| Tempo de conclusão (min) | | | | | |
| Concluiu sem ajuda? (S/N) | | | | | |
| Nº de hesitações/erros | | | | | |
| Pediu ajuda ou clareza? (S/N) | | | | | |

**Escala de satisfação pós-teste (1–5 para o usuário responder):**
- Facilidade geral de uso: ___
- Clareza das informações: ___
- Confiança para tomar uma decisão: ___

---

## Observações gerais (espaço livre para o Secretário nº 1)

```
Tarefa 1:


Tarefa 2:


Tarefa 3:


Tarefa 4:


Tarefa 5:


Impressões gerais:
```
