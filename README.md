# T1 -- Paralelizacao de uma aplicacao com OpenMP

Aluno: Bernardo Klein Heitz

path tracer estilo `smallpt` (kevin beason), reescrito em c11
(o padrao iso da linguagem c publicado em 2011; o gcc usa `-std=c11`).
o laco paralelizado e o das linhas da imagem.

## ambiente

- cpu: amd ryzen 5 3600 (6 nucleos fisicos, 12 threads), 3.6 ghz, l3 32 mb, 32 gb ram
- so: ubuntu 22.04 em wsl2 sobre windows 11
- gcc 11.4.0. flags: `-O3 -march=native -ffast-math -std=c11` (c11 = padrao iso c de 2011; a versao paralela acrescenta `-fopenmp`)
- entrada de referencia: `-w 800 -h 600 -s 32`
- threads: `OMP_NUM_THREADS` (nao `omp_set_num_threads`)

## reproduzir

```
make all
bash scripts/run_all.sh
python scripts/plot.py
cd report && pdflatex relatorio.tex
```

`run_all.sh` roda perfil, 7 politicas de scheduling, escalabilidade forte e fraca (10 repeticoes por ponto).

tempos brutos: `results/strong.csv`, `results/weak.csv`, `results/sched.csv`.
speed-up e eficiencia usam a coluna `time_s` (fase computacional completa).
o checksum rgb e identico entre 1 e 12 threads e entre todas as politicas.

## binario

```
OMP_NUM_THREADS=12 bin/smallpt_omp -w 800 -h 600 -s 32 --schedule dynamic,4
bin/smallpt_seq -w 800 -h 600 -s 32
```
