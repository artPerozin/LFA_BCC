# TF — Linhas de Produção com Autômatos com Pilha

## Estrutura do projeto

```
fabrica_pda/
├── automato_pilha.py   # PDA genérico + saídas (Mealy estendido)
├── modelos_carros.py   # Definição dos 4 tipos e 13 modelos de carros
├── fabrica.py          # Motor de simulação da fábrica
└── main.py             # Script principal — 3 dias de produção
```

---

## Modelagem formal

### Autômato com Pilha (PDA)

Cada modelo de carro é descrito por um PDA:

```
M = (Q, Σ, Γ, δ, q₀, Z₀, F)
```

| Componente | Descrição |
|-----------|-----------|
| `Q` | Conjunto de estados (q0, q1, …, qN, qN_fim) |
| `Σ` | Símbolos de entrada = etapas de fabricação (CHASSI, MOTOR, …, FIM) |
| `Γ` | Alfabeto da pilha = `{Z}` (fundo de pilha) |
| `δ` | Função de transição (Transicao) |
| `q₀` | Estado inicial (`q0`) |
| `Z₀` | Símbolo inicial da pilha (`Z`) |
| `F` | Estado de aceitação (`qN_fim`) |

**Condição de aceitação:** estado em `F` **e** pilha vazia → `FINALIZADO`.

### Saídas (extensão Mealy)

Cada transição carrega uma string `saida` que descreve a etapa executada,
tornando o PDA um **Autômato com Saída** (estilo Mealy, estendido para PDA).

### Falhas

Etapas marcadas com `pode_falhar=True` podem gerar falha aleatória
(probabilidade configurável via `--taxa-falha`). Isso simula falhas reais
de linha: peças defeituosas, erros de montagem, equipamento com defeito.

---

## Tipos e modelos de carros

| Tipo   | Modelos            | Etapas |
|--------|--------------------|--------|
| SEDAN  | BASE, GL, GLS, SPORT | 6–11 |
| SUV    | ENTRY, AWD, PREMIUM  | 7–11 |
| PICKUP | CS, CD, CD-TURBO     | 7–10 |
| HATCH  | POP, CITY, RS        | 6–10 |

Modelos mais sofisticados herdam etapas dos básicos e adicionam novas.

---

## Como executar

```bash
# Log completo de cada etapa
python main.py

# Apenas relatórios finais (mais limpo)
python main.py --silencioso

# Resultado reprodutível (fixar semente)
python main.py --seed 42

# Ajustar probabilidade de falha (padrão 10%)
python main.py --taxa-falha 0.05

# Combinar opções
python main.py --silencioso --seed 99 --taxa-falha 0.15
```

---

## Instâncias independentes do PDA

Cada unidade de veículo é uma **instância independente** do PDA correspondente,
conforme solicitado no enunciado. Isso significa que 5 veículos SEDAN GL em
produção simultânea são 5 objetos `InstanciaPDA` distintos, cada um com sua
pilha, estado atual e histórico próprios.

---

## Relatórios

O sistema emite:
1. **Relatório diário** ao fim de cada turno — separado por tipo/modelo:
   - Veículos **finalizados** (atingiram o estado de aceitação)
   - Veículos com **falha** (detalhe da etapa que falhou)
   - Veículos **incompletos** por fim de expediente
2. **Relatório acumulado** ao final, com percentuais por modelo.
3. **Histórico de etapas** de um veículo específico (rastreabilidade completa).
