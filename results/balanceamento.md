# balanceamento de carga

configuração: `w=800 h=600 spp=32`, 12 threads, `bin/smallpt_omp`
(gcc -O3 -march=native -ffast-math -fopenmp).

## tempos totais por política (mediana de 3 execuções)

| política          | mediana [s] | min [s] | max [s] |
|-------------------|------------:|--------:|--------:|
| static (padrão)   | 7.238       | 7.218   | 7.383   |
| static,32         | 7.356       | 7.299   | 7.372   |
| static,4          | 7.328       | 7.290   | 7.395   |
| dynamic           | 7.384       | 7.372   | 7.455   |
| dynamic,32        | 7.377       | 7.344   | 7.506   |
| dynamic,4         | 7.329       | 7.321   | 7.501   |
| guided            | 7.421       | 7.317   | 7.557   |

**vencedor: `static` (padrão), ~7.24s.**

## desbalanceamento medido por thread (com nowait)

o campo `time_s` mostra o tempo real de cada thread dentro do laço em y;
o campo `imbalance = max - min` é a diferença entre a thread mais lenta e
a mais rápida.

| política   | min [s] | media [s] | max [s] | imbalance [s] | ineficiência |
|------------|--------:|----------:|--------:|--------------:|-------------:|
| static     | 7.074   | 7.117     | 7.148   | 0.074         | 0.4%         |
| static,32  | 7.560   | 7.593     | 7.627   | 0.067         | 0.4%         |
| static,4   | 7.473   | 7.526     | 7.554   | 0.081         | 0.4%         |
| dynamic    | 8.209   | 8.239     | 8.295   | 0.086         | 0.7%         |
| dynamic,32 | 7.558   | 7.610     | 7.649   | 0.091         | 0.5%         |
| dynamic,4  | 7.439   | 7.472     | 7.504   | 0.064         | 0.4%         |
| guided     | 7.532   | 7.594     | 7.633   | 0.101         | 0.5%         |

## conclusão

era plausível esperar que `dynamic` vencesse: os raios que atingem a
esfera de vidro e a de espelho fazem muitas reflexões e refrações antes
de sair da cena, e essa profundidade extra não está distribuída
uniformemente entre pixels. mas o experimento contradiz a intuição.

com 600 linhas divididas por 12 threads, cada thread do `static` recebe
50 linhas contíguas: essa granularidade é grossa o suficiente para
diluir a variância de profundidade dentro de cada bloco (uma linha
"cara" costuma vir junto de linhas próximas na imagem, então acaba
"puxando" o resto do bloco também). a ineficiência de balanceamento
medida fica em torno de 0.5% em todas as políticas — abaixo do ruído
de execução.

sem desbalanceamento aparente, o que sobra é o overhead: `dynamic` sem
chunk paga uma sincronização por linha e fica ~2% mais lento; `guided`
começa com blocos grandes e diminui, o que introduz irregularidade sem
ganho; as variantes com chunk (`static,32`, `dynamic,4`) ficam
essencialmente empatadas com o `static` sem chunk (diferenças de 1-2%,
dentro da variação de execução).

**decisão: usar `schedule(static)` (padrão) nas escalabilidades forte
e fraca.** essa política é justificada por medição, não por default.
