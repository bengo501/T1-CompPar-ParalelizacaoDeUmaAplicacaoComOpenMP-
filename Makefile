# makefile do t1 - path tracer smallpt para computacao paralela
# tres alvos com flags identicas de otimizacao. -std=c11 pede ao gcc o
# padrao iso c de 2011. o binario sequencial nao usa -fopenmp (esse e o
# T1 de referencia); o paralelo usa -fopenmp; o de profile usa -pg para
# o gprof e -O2 para evitar demais inlining.

CC       ?= gcc
STD       = -std=c11
WARN      = -Wall -Wextra -Wno-unused-parameter
OPT       = -O3 -march=native -ffast-math
INC       = -Isrc
LIBS      = -lm

SRC       = src/smallpt.c
BIN_DIR   = bin

BIN_SEQ   = $(BIN_DIR)/smallpt_seq
BIN_OMP   = $(BIN_DIR)/smallpt_omp
BIN_PROF  = $(BIN_DIR)/smallpt_prof

.PHONY: all clean seq omp prof dirs

all: seq omp

seq:  dirs $(BIN_SEQ)
omp:  dirs $(BIN_OMP)
prof: dirs $(BIN_PROF)

dirs:
	@mkdir -p $(BIN_DIR) results

$(BIN_SEQ): $(SRC)
	$(CC) $(STD) $(WARN) $(OPT) $(INC) $< -o $@ $(LIBS)

$(BIN_OMP): $(SRC)
	$(CC) $(STD) $(WARN) $(OPT) -fopenmp $(INC) $< -o $@ $(LIBS)

# -O2 -fno-inline preserva os simbolos das funcoes quentes (radiance,
# sphere_intersect, ...) sem deprimir tanto o desempenho a ponto de o
# perfil deixar de ser representativo. -DPROFILE remove os inline
# manuais das operacoes vetoriais.
$(BIN_PROF): $(SRC)
	$(CC) $(STD) $(WARN) -O2 -fno-inline -fno-inline-functions -fno-inline-small-functions -pg -DPROFILE $(INC) $< -o $@ $(LIBS)

clean:
	rm -rf $(BIN_DIR) results/*.csv results/*.txt gmon.out
