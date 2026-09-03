# decisões de instrumentação openmp

referência de arquivo: [src/smallpt.c](../src/smallpt.c)

## laço paralelizado e cláusulas

```
#pragma omp parallel default(none) \
        shared(a, c, cam_o, cam_d, cx, cy, stat, threads_used)
{
    ...
    #pragma omp for schedule(runtime)
    for (int y = 0; y < a.h; ++y) { ... }
}
```

- `default(none)`: obriga a listar explicitamente o escopo de cada variável,
  o que expõe se algo esqueceu de virar `private`.
- `shared`: apenas parâmetros de entrada (`a`, `cam_*`, `cx`, `cy`), o buffer
  `c` (cada thread escreve em posições disjuntas, indexadas por `y*w+x`) e
  o vetor `stat` de estatísticas por thread (também indexado por `tid`, sem
  falso compartilhamento graças ao padding de 64 bytes).
- `schedule(runtime)`: a política vem de `OMP_SCHEDULE`, o que permite
  comparar `static`, `dynamic`, `guided` sem recompilar. o padrão é
  `static` (opção `schedule(static)` sem chunk).
- não há `reduction`, `atomic` nem `critical` no laço quente porque não
  existe acumulador compartilhado: o checksum é calculado depois da região
  paralela (é setup/finalização, os 2% não-paralelos do gprof).

## escopo do rng

o gerador `Rng rng` é declarado dentro do corpo do laço em `y`, portanto
é automaticamente privado ao thread por construção da região paralela.
a semente vem de `a.seed ^ ((y+1) * 0x9E3779B97F4A7C15ULL)`: cada linha
tem semente própria, então a saída é reprodutível e não depende do número
de threads (confirmado por checksum idêntico em 1, 4 e 12 threads).

### alternativa considerada (não adotada)

um rng global compartilhado exigiria `critical` a cada `rng_next()`. isso
é a otimização que o enunciado pede para "descrever o efeito medido":
mesmo com o custo do critical, a serialização das ~46 milhões de chamadas
a `rng_next` reduziria o paralelismo a zero. a versão com rng por-linha
mantém eficiência de ~0.95 em 6 threads (ver `results/strong.csv`).

## granularidade

- unidade de trabalho: uma linha da imagem (a.w pixels).
- iterações totais no laço externo: `a.h` (600 para o experimento forte).
- 600 iterações e 12 threads dão 50 iterações por thread em `static` sem
  chunk. como o custo por linha é irregular (linhas que atravessam o
  espelho e o vidro fazem mais reflexões, linhas do fundo pretas terminam
  rápido), esse desbalanceamento é o objeto do estudo em
  [balanceamento](balanceamento.md).

## variáveis privadas por natureza

- `x`, `y`, `sx`, `sy`, `s`: variáveis de laço, privadas automaticamente.
- `r_pixel`, `r_sub`, `d`, `ray`: locais ao corpo do laço.
- `rng`: local ao corpo do laço em `y`.
- `tt0`, `itcount`, `tid`: locais à região paralela, portanto privados.
