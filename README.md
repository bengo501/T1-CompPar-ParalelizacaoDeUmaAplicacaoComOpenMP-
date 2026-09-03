# T1 -- Paralelizacao de uma aplicacao com OpenMP

paralelizacao com OpenMP de um path tracer estilo `smallpt` (kevin beason),
reescrito em C11. o laco paralelizado e o das linhas da imagem; cada linha
e uma unidade de trabalho independente, escrita numa faixa disjunta do
buffer de saida, com gerador xorshift64 privado por linha.

grupo: **nomes dos integrantes**

## como reproduzir os resultados

toda a bateria roda em WSL2 (ubuntu 22.04) com `gcc 11.4` e `make`. os
graficos sao gerados pelo `python 3.10` do windows com `matplotlib`.

### 1. compilar

```
make all           # gera bin/smallpt_seq (sem -fopenmp) e bin/smallpt_omp
make prof          # gera bin/smallpt_prof (com -pg para o gprof)
```

flags usadas (identicas nos dois binarios computacionais):
`-O3 -march=native -ffast-math -std=c11 -Wall`.
o binario paralelo acrescenta apenas `-fopenmp`.

### 2. medir

```
bash scripts/profile.sh          # perfil com gprof (~30s)
bash scripts/run_sched.sh        # 7 politicas de scheduling em 12 threads
bash scripts/run_strong.sh       # escalabilidade forte, 1..12 threads
bash scripts/run_weak.sh         # escalabilidade fraca, 1..12 threads
bash scripts/summarize_balance.sh
```

parametros ajustaveis pelas variaveis `W`, `H`, `SPP`, `REPS`, `THREADS`,
`SPP_BASE`. defaults reproduzem exatamente a Tabela do relatorio:
- forte: `W=800 H=600 SPP=32`
- fraca: `W=800 H=600 SPP_BASE=8`, spp escala como `SPP_BASE*p`
- schedule: `W=800 H=600 SPP=32` em 12 threads.

todas as execucoes usam `OMP_NUM_THREADS` (variavel de ambiente), nao
`omp_set_num_threads`, e escrevem `results/*.csv` com uma linha por
execucao no formato:
```
version,label,threads,schedule,w,h,spp,time_s,checksum
```
o `checksum` bate em todas as contagens de threads e em todas as
politicas de scheduling, o que valida a paralelizacao.

### 3. graficos

```
python scripts/plot.py
```
le `results/strong.csv` e `results/weak.csv` e gera:
- `results/speedup.pdf` -- speed-up com reta ideal e faixa min/max
- `results/efficiency.pdf` -- eficiencia forte e fraca no mesmo grafico

o script tambem grava versoes `.png` para pre-visualizacao.

### 4. relatorio

`report/relatorio.tex` e um documento LaTeX de 2 paginas (coluna dupla
na pagina 1, coluna simples na pagina 2) que segue exatamente o formato
exigido no enunciado.

compilar (fora da maquina de teste, se necessario):
```
cd report
pdflatex relatorio.tex
```
ou subir em Overleaf.

## estrutura

```
Makefile             alvos seq / omp / prof / clean
src/
  smallpt.c          um unico arquivo, cobre sequencial e paralelo
scripts/
  calib.sh           varre tamanhos para calibrar o tempo sequencial
  profile.sh         gprof
  run_sched.sh       comparacao de politicas de scheduling
  run_strong.sh      escalabilidade forte
  run_weak.sh        escalabilidade fraca
  balance_only.sh    so as amostras de --profile-balance
  summarize_balance.sh
  plot.py            graficos matplotlib
results/
  perfil.md          fracao paralelizavel + teto de amdahl
  otimizacoes.md     decisoes de escopo e clausulas
  balanceamento.md   analise das politicas de scheduling
  strong.csv         tabela da escalabilidade forte
  weak.csv           tabela da escalabilidade fraca
  sched.csv          tempos por politica
  balance.csv        tempo e iteracoes por thread por politica
  gprof.txt          saida completa do gprof
  speedup.pdf/png    grafico da escalabilidade forte
  efficiency.pdf/png grafico das duas eficiencias
report/
  relatorio.tex      pdf final (compilar com pdflatex)
```

## ambiente da medicao (colocado no relatorio tambem)

- CPU: AMD Ryzen 5 3600 (6 nucleos fisicos, 12 threads logicas, 3.6 GHz)
- L3: 32 MB. RAM: 32 GB DDR4.
- OS: Ubuntu 22.04 em WSL2 sobre Windows 10.
- gcc: 11.4.0. flags: `-O3 -march=native -ffast-math -std=c11`, mais
  `-fopenmp` na versao paralela.

## como o binario e usado

```
bin/smallpt_omp -w 800 -h 600 -s 32 --schedule static --label omp
OMP_NUM_THREADS=8 bin/smallpt_omp -w 800 -h 600 -s 32
bin/smallpt_omp -w 320 -h 240 -s 4 --image saida.ppm --profile-balance
```

opcoes:
- `-w W -h H -s SPP`   dimensoes da imagem e amostras por subpixel (o
  numero total por pixel e `4*SPP`).
- `-t N`               fixa `omp_set_num_threads(N)`; prefira
  `OMP_NUM_THREADS` no ambiente.
- `--schedule POL`     `static | static,K | dynamic | dynamic,K | guided`;
  interno usa `schedule(runtime)` e define `OMP_SCHEDULE`.
- `--profile-balance`  imprime tempo e iteracoes por thread em stderr.
- `--image OUT.ppm`    grava a imagem (fora da regiao cronometrada).
- `--label L`          rotulo da linha csv (util em varreduras).

## uso de ferramentas de IA

um assistente de IA foi usado para revisar o arnes de medicao, o
script de plotagem e a estrutura do relatorio. cada decisao de codigo
foi verificada com medicao e pode ser reproduzida com os comandos acima.
