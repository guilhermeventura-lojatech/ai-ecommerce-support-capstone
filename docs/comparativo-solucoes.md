# Comparação de alternativas

| Alternativa | Benefícios | Limites / riscos | Custo relativo no caso |
| --- | --- | --- | --- |
| Regras | Previsibilidade, auditoria, simplicidade | Fragilidade diante da variação linguística | Baixo |
| Classificador ML | Roteamento de intenções, escala | Precisa de exemplos rotulados e manutenção | Médio |
| LLM | Linguagem natural, adaptação contextual | Alucinações, custo e governança | Alto |

## Cinco critérios de decisão
1. **Previsibilidade:** perguntas recorrentes favorecem regras.
2. **Necessidade semântica:** ambiguidades favorecem interpretação por LLM.
3. **Complexidade:** agentes autônomos seriam excessivos para o caso.
4. **Volume de dados:** 25 mil tickets/mês tornam ML plausível, mas rótulos e acesso precisam ser verificados.
5. **Explicabilidade:** atendimento exige consistência, rastreabilidade e políticas autorizadas.

## Recomendação
Combinar regras, classificação e LLM controlado em arquitetura híbrida, com atendimento humano para exceções e baixa confiança.
