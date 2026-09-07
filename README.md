# NCAS — Núcleo Cognitivo da Aurora Siger

Fase 5 do projeto Aurora Siger (FIAP). Sistema em Python que registra, organiza, consulta e interpreta informações operacionais de uma colônia marciana, usando arquivos texto e JSON, uma regra booleana simplificada e prompts estruturados.

O projeto dá continuidade às fases anteriores da mesma colônia: os seis módulos (Habitat Alpha, MedBase, Reator Solar, BioLab, LogiStore e TerraBot) são os mesmos cadastrados na Fase 2, monitorados energeticamente na Fase 3 e conectados em rede na Fase 4.

## Como executar

```bash
python codigo_fonte.py
```

Não há dependências externas — o sistema usa apenas a biblioteca padrão do Python (`json`, `os` e `datetime`). O `registros_colonia.txt` é criado automaticamente no primeiro cadastro de registro.

## Estrutura dos arquivos

```
Aurora-Fase5/
├── codigo_fonte.py          # sistema completo
├── dados_colonia.json       # módulos da colônia + histórico de respostas
└── registros_colonia.txt    # log de ocorrências (gerado pelo sistema)
```

## Organização dos dados

A divisão entre os dois formatos segue o tipo de acesso necessário:

| Arquivo | Formato | Conteúdo | Por quê |
|---|---|---|---|
| `dados_colonia.json` | JSON | módulos e histórico de respostas | cada item tem vários campos relacionados, então precisa de estrutura hierárquica |
| `registros_colonia.txt` | TXT | log de ocorrências | cada linha é um evento independente, gravado em ordem cronológica |

O JSON é lido inteiro para a memória com `json.load()` e regravado com `json.dump()`. O TXT usa o modo append (`"a"`), que preserva o histórico e não exige reescrever o arquivo a cada nova linha.

## Regra lógica e simplificação booleana

A regra que decide se um módulo gera alerta foi escrita na forma negativa e simplificada com o teorema de De Morgan:

```
Original:      ALERTA = NOT (ATIVO AND NOT RISCO_ALTO)
De Morgan:     ALERTA = NOT ATIVO OR NOT (NOT RISCO_ALTO)
Dupla negação: ALERTA = NOT ATIVO OR RISCO_ALTO
Forma final:   ALERTA = INATIVO OR RISCO_ALTO
```

A forma original expressa a ideia de "só não gerar alerta quando o módulo está ativo e sem risco alto". A simplificação elimina a negação externa e traduz direto para uma linha de código, sem alterar o resultado: em ambas, o alerta deixa de ser gerado apenas quando o módulo está ativo **e** o risco não é alto.

A implementação está na função `gerar_alerta()`.

## Engenharia de prompts

O sistema monta três prompts para a mesma tarefa (classificar o módulo e gerar um relatório), variando apenas a técnica:

- **Zero-shot** — apenas a instrução, sem exemplos. O modelo decide sozinho o que caracteriza cada classificação.
- **Few-shot** — três exemplos calibram o critério e fixam o formato da resposta. Os módulos dos exemplos são fictícios de propósito, para que a resposta seja deduzida do padrão e não copiada.
- **Structured output** — define o esquema JSON exato da resposta, permitindo que o sistema processe a saída automaticamente.

A resposta é simulada localmente: a classificação vem da mesma regra booleana usada pelo sistema, e cada estilo devolve a resposta no formato que o seu prompt pediu. Não há chamada a API externa.

## Menu

| Opção | Função |
|---|---|
| 1 | Cadastrar registro |
| 2 | Consultar registros |
| 3 | Consultar módulos |
| 4 | Apagar registro |
| 5 | Limpar todos os registros |
| 6 | Analisar alertas (aplica a regra booleana) |
| 7 | Simular assistente inteligente |
| 8 | Histórico de respostas do assistente |
| 0 | Sair |

## Equipe

Ellen Kauane Rodrigues Alves, Rafael Gonçalves de Souza Pereira, Pietra Fanticelli e Victor de Camargo Gomes .
