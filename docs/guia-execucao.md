# Guia de execução e reprodução

## 1. Escopo

Este guia executa o projeto localmente no Windows PowerShell, sem serviços pagos,
sem dados pessoais e com `LLM_ENABLED=false`.

## 2. Pré-requisitos

- Windows com PowerShell;
- Python 3.10 ou superior;
- Node.js `^20.19.0` ou `>=22.12.0`;
- npm;
- Git opcional para clonar o repositório.

Versões usadas na validação final:

```text
Python 3.14.3
Node.js v24.11.1
npm 11.14.1
```

## 3. Instalação do backend

Na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[test]"
```

Não copie `.env.example` se não precisar mudar os padrões. A LLM já inicia
desabilitada.

## 4. Instalação do frontend

```powershell
Set-Location frontend
npm install
Set-Location ..
```

`package-lock.json` fixa a árvore resolvida para reprodução.

## 5. Iniciar a aplicação

### Terminal 1 — API

```powershell
Set-Location "C:\caminho\para\ai-ecommerce-support-capstone-starter"
.\.venv\Scripts\Activate.ps1
$env:LLM_ENABLED = "false"
python -m uvicorn backend.app.main:app --reload
```

Verificação:

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/health"
```

### Terminal 2 — interface

```powershell
Set-Location "C:\caminho\para\ai-ecommerce-support-capstone-starter\frontend"
npm run dev
```

Acesse `http://127.0.0.1:5173`.

Se necessário, selecione explicitamente a API:

```powershell
$env:VITE_API_URL = "http://127.0.0.1:8000"
npm run dev
```

## 6. Usar a API

### Rastreio genérico

```powershell
$body = @{ message = "Onde vejo o rastreio?" } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/support/messages" `
  -ContentType "application/json" `
  -Body $body
```

Resultado esperado: `route=regra`, `intent=entrega`,
`requires_human=false` e `rule_id=FAQ-TRACKING-001`.

### Caso sem política

```powershell
$body = @{ message = "Meu cartão foi recusado mesmo com limite" } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/support/messages" `
  -ContentType "application/json" `
  -Body $body
```

Resultado esperado: intenção de pagamento, rota humana e motivo de ausência de
resposta autorizada.

### Fora de escopo ou baixa confiança

```powershell
$body = @{ message = "Qual a temperatura prevista para Marte amanhã?" } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/support/messages" `
  -ContentType "application/json" `
  -Body $body
```

Resultado esperado: intenção desconhecida e escalonamento.

## 7. Testes backend

```powershell
python -m pytest
```

O comando deve encontrar os testes em `backend/tests` conforme `pyproject.toml`.

## 8. Experimentos ML

```powershell
python scripts/evaluate_ml.py
python scripts/compare_routing.py
```

Os scripts imprimem JSON no terminal e não sobrescrevem dados ou métricas.

## 9. Testes e build frontend

```powershell
Set-Location frontend
npm test
npm run build
```

O build estático é gerado em `frontend/dist`, ignorado pelo Git.

## 10. Configurações experimentais

```powershell
$env:ML_CONFIDENCE_THRESHOLD = "0.35"
$env:ML_MIN_KNOWN_TOKEN_RATIO = "0.20"
```

Alterar esses valores muda o roteamento e invalida comparações diretas com os
resultados registrados.

## 11. LLM opcional

Não habilite a LLM para reproduzir o capstone. O modo avaliado é:

```powershell
$env:LLM_ENABLED = "false"
```

O adaptador real existe para experimento futuro, mas não foi validado contra um
provedor. Habilitá-lo exige autorização, URL, chave, modelo, taxas e limites. Não
salve chaves em arquivos versionados.

## 12. Solução de problemas

### Política de execução bloqueia ativação

Use o Python do ambiente diretamente:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

### Frontend indica API indisponível

Confirme `http://127.0.0.1:8000/health`, a porta 8000 e `VITE_API_URL`. O backend
aceita CORS somente das origens locais na porta 5173.

### Métricas diferentes

Confirme dataset sem alterações, seed 42, dependências instaladas e execução a
partir da raiz. Não altere thresholds ou configuração do pipeline.

### Build incompatível com Node

Use uma versão permitida pelo Vite instalado: `^20.19.0` ou `>=22.12.0`.

## 13. Checklist de reprodução

- [ ] LLM desabilitada;
- [ ] backend responde `/health`;
- [ ] frontend abre na porta 5173;
- [ ] 41 testes backend passam;
- [ ] 6 testes frontend passam;
- [ ] build Vite conclui;
- [ ] avaliação retorna 13/19 e macro F1 0,689;
- [ ] comparação identifica ML bruto como diagnóstico;
- [ ] nenhum segredo ou dado pessoal foi adicionado.
