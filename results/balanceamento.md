# balanceamento de carga

configuração: `w=800 h=600 spp=32`, 12 threads, `bin/smallpt_omp`
(gcc -O3 -march=native -ffast-math -fopenmp). **10 execuções por política**.

## tempos totais por política (mediana, min, max de 10 execuções)

| política          | mediana [s] | min [s] | max [s] |
|-------------------|------------:|--------:|--------:|
| static (padrão)   | 9.556       | 7.573   | 11.779  |
| static,32         | 8.389       | 7.425   | 10.494  |
| static,4          | 7.658       | 7.259   |  8.287  |
| dynamic           | 7.297       | 7.210   |  7.933  |
| dynamic,32        | 7.199       | 7.157   |  7.608  |
| **dynamic,4**     | **7.164**   | 7.006   |  7.354  |
| guided            | 7.231       | 6.935   |  7.385  |

**vencedor: `dynamic,4` (mediana 7.16 s) — com `guided` em segundo lugar
(7.23 s) e `dynamic,32` em terceiro (7.20 s). `static` sem chunk ficou em
último com 9.56 s e altíssima dispersão.**

## amostras completas (ordenadas)

```
static      7.57 8.30 8.56 9.07 9.47 9.65 9.81 10.29 10.69 11.78
static,32   7.42 7.81 7.86 7.90 8.37 8.41 8.46 8.62  8.80 10.49
static,4    7.26 7.37 7.46 7.50 7.66 7.66 7.67 8.14  8.23  8.29
dynamic     7.21 7.24 7.25 7.28 7.29 7.30 7.34 7.36  7.41  7.93
dynamic,32  7.16 7.16 7.17 7.17 7.18 7.22 7.29 7.29  7.31  7.61
dynamic,4   7.01 7.07 7.09 7.14 7.15 7.17 7.23 7.24  7.27  7.35
guided      6.93 6.95 7.13 7.21 7.21 7.25 7.26 7.27  7.34  7.39
```

## análise

com 3 repetições, tínhamos visto `static` como campeão. com 10
repetições fica claro que `static` sem chunk é **muito volátil** nesta
máquina: as amostras vão de 7.57 até 11.78 s (dispersão de 4.2 s).
`static,32` melhora bastante (7.42 a 10.49) e `static,4` melhora ainda
mais (7.26 a 8.29), mas nenhuma das três variantes de static compete
com o topo.

por que `static` perde? o WSL2/Windows não oferece a mesma latência
determinística de um Linux nativo: threads são preemptadas ocasionalmente
por outros processos do sistema. em `static` sem chunk, cada thread
recebe um bloco contíguo de 50 linhas e ninguém pode ajudá-la; se uma
thread é atrasada, o programa espera. em `dynamic,4` ou `guided`, quando
uma thread termina o bloco atual, ela pega outro imediatamente, o que
"absorve" o atraso de qualquer thread que tenha sido preemptada.

a inefficiency interna (perfil por thread) continua abaixo de 1% em
todas as políticas, o que confirma que **o desbalanceamento não vem
da variância intrínseca do algoritmo**, mas sim do ambiente de
execução. essa distinção só ficou visível com 10 repetições.

**decisão: usar `schedule(dynamic, 4)` nas escalabilidades forte e
fraca.** justificada por medição: menor mediana, menor variação, e
comportamento mais robusto a interferências do sistema. É importante
enfatizar que esta é uma decisão *empírica*: o path tracer tem carga
levemente heterogênea por profundidade de recursão, mas o fator dominante
para preferir dynamic aqui é a robustez a preempção, não a
heterogeneidade da carga.
