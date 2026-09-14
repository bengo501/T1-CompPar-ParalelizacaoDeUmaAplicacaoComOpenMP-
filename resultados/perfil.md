# perfil de execução do smallpt sequencial

configuração do perfil: `-w 800 -h 600 -s 32` (mesma entrada e mesma
fase computacional do speed-up), binário `bin/smallpt_prof`
(gcc -O2 -fno-inline -fno-inline-functions -pg -DPROFILE).

## distribuição do tempo (gprof, tempo próprio)

| função              | % self | observações                                |
|---------------------|-------:|--------------------------------------------|
| sphere_intersect    |  31.24 | 9 esferas por raio                         |
| radiance            |  14.02 | tempo próprio; o restante cai nas filhas   |
| v_dot               |  11.93 | produto escalar                            |
| v_ (construtor)     |  10.50 | overhead visível por causa do -fno-inline  |
| v_norm              |   7.72 |                                            |
| v_sub               |   6.59 |                                            |
| intersect_scene     |   5.08 | laço sobre as 9 esferas                    |
| v_scl               |   4.19 |                                            |
| v_add               |   2.61 |                                            |
| main                |   1.75 | setup, checksum e overhead do laço em y    |
| rng_uniform         |   1.35 |                                            |
| v_cross             |   1.29 |                                            |
| v_mul               |   0.94 |                                            |
| rng_next            |   0.73 |                                            |
| _init, clamp01, now_s | 0.07 | fora do núcleo                             |

todas as funções acima, exceto `main` (1,75%), `_init`, `clamp01` e
`now_s` (~0,07%), são chamadas de dentro do laço `for (y = 0; y < h; ++y)`,
que é o eixo paralelizado. fração paralelizável pelo gprof: **f ≈ 0,982**.

## complemento: mesma fase no binário -O3

no binário de medição (`-O3`, sem `-pg`), a razão `time_par_s / time_s`
da versão sequencial de referência (10 execuções, mediana) é 0,99998.
isso confirma que setup da câmera, alocação e checksum são desprezíveis
na fase medida; o gprof infla um pouco a parcela de `main` por causa do
`-fno-inline`. o teto de amdahl usado no relatório é o do gprof (mais
conservador).

## teto de amdahl (f = 0,982)

- 6 threads (núcleos físicos): S_max = 1 / (0,018 + 0,982/6) ≈ 5,51
- 12 threads (processadores lógicos): S_max = 1 / (0,018 + 0,982/12) ≈ 10,00
- limite assintótico: S_∞ = 1 / (1 − f) ≈ 55,6

o speed-up observado em 12 threads (~7,44) fica bem abaixo de 10, então
a fração sequencial sozinha não explica a saturação.

## justificativa do laço escolhido

o gprof, na mesma entrada do speed-up, confirma que o laço externo em y
concentra a totalidade do tempo útil. os pixels são independentes entre
si (cada iteração escreve em uma faixa disjunta do buffer `c` e usa um
rng com estado local ao corpo do laço).
