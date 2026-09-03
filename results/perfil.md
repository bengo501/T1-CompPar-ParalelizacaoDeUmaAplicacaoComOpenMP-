# perfil de execução do smallpt sequencial

configuração do perfil: `-w 320 -h 240 -s 8`, binário `bin/smallpt_prof`
(gcc -O2 -fno-inline -fno-inline-functions -pg -DPROFILE).

## distribuição do tempo (gprof, tempo próprio)

| função              | % self | observações                                |
|---------------------|-------:|--------------------------------------------|
| v_dot               |  19.81 | produto escalar; chamado em cada intersecção e reflexão |
| v_ (construtor)     |  17.71 | criação de temporários; overhead de -fno-inline |
| v_sub               |  12.95 | vetores dentro de radiance                 |
| sphere_intersect    |  11.05 | 9 esferas por raio                         |
| radiance            |   9.52 | tempo próprio; total (com filhas) ≈ 97.9% |
| v_scl               |   8.57 |                                            |
| v_add               |   6.10 |                                            |
| intersect_scene     |   3.62 | laço sobre as 9 esferas                    |
| v_norm              |   2.48 |                                            |
| v_mul               |   2.10 |                                            |
| v_cross             |   2.10 |                                            |
| main                |   2.10 | inclui setup e o próprio loop em y         |
| rng_uniform+rng_next|   1.71 |                                            |
| clamp01, now_s, _init|  0.19 | não computacional                         |

## fração paralelizável e teto de amdahl

- todas as funções acima, exceto os 0.19% de setup/finalização, são chamadas
  de dentro do laço `for (int y = 0; y < a.h; ++y)` do `main`, que é o eixo
  paralelizado.
- fração paralelizável medida: f ≥ 0.98 (98%). o restante é setup da câmera,
  alocação do buffer, cálculo do checksum e escrita da imagem.
- teto de amdahl para 12 threads:
  - com f = 0.98: S_max = 1 / (0.02 + 0.98/12) ≈ 9.83
  - com f = 0.99: S_max = 1 / (0.01 + 0.99/12) ≈ 10.81
- teto de amdahl para 6 threads (núcleos físicos):
  - com f = 0.98: S_max ≈ 5.31
  - com f = 0.99: S_max ≈ 5.66

## justificativa do laço escolhido

o gprof confirma que o laço externo em y concentra a totalidade do tempo
útil. os pixels são independentes entre si (cada iteração escreve em uma
faixa disjunta do buffer c e usa um rng com estado local ao corpo do laço),
o que o torna candidato natural a paralelismo de dados sem necessidade de
`reduction`, `critical` ou `atomic` no laço quente.
