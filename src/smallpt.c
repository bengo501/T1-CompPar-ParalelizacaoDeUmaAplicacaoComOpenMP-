// path tracer estilo smallpt (kevin beason, 2008), reescrito em c para o t1
// de computacao paralela. um unico arquivo serve para o binario sequencial
// (compilado sem -fopenmp) e para o paralelo (com -fopenmp). o laco quente
// e o das linhas da imagem; cada pixel e independente, entao nao ha condicao
// de corrida se o gerador de numeros aleatorios tiver estado por-thread.

#define _POSIX_C_SOURCE 200809L
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#ifdef _OPENMP
  #include <omp.h>
  static inline double now_s(void) { return omp_get_wtime(); }
#else
  static inline double now_s(void) {
      struct timespec t;
      clock_gettime(CLOCK_MONOTONIC, &t);
      return (double)t.tv_sec + (double)t.tv_nsec * 1e-9;
  }
#endif

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// no build de profile as funcoes precisam sobreviver a otimizacao para
// que o gprof consiga contabiliza-las; em release, `inline static` continua
// permitindo que o compilador as elimine em -O3.
#ifdef PROFILE
  #define SI __attribute__((noinline))
#else
  #define SI static inline
#endif

typedef struct { double x, y, z; } Vec;

SI Vec v_(double x, double y, double z) { Vec r = {x,y,z}; return r; }
SI Vec v_add(Vec a, Vec b)  { return v_(a.x+b.x, a.y+b.y, a.z+b.z); }
SI Vec v_sub(Vec a, Vec b)  { return v_(a.x-b.x, a.y-b.y, a.z-b.z); }
SI Vec v_scl(Vec a, double s){ return v_(a.x*s,   a.y*s,   a.z*s  ); }
SI Vec v_mul(Vec a, Vec b)  { return v_(a.x*b.x, a.y*b.y, a.z*b.z); }
SI double v_dot(Vec a, Vec b){ return a.x*b.x + a.y*b.y + a.z*b.z; }
SI Vec v_cross(Vec a, Vec b){
    return v_(a.y*b.z - a.z*b.y, a.z*b.x - a.x*b.z, a.x*b.y - a.y*b.x);
}
SI Vec v_norm(Vec a) {
    double n = 1.0 / sqrt(a.x*a.x + a.y*a.y + a.z*a.z);
    return v_(a.x*n, a.y*n, a.z*n);
}

typedef struct { Vec o, d; } Ray;
typedef enum { DIFF, SPEC, REFR } Refl_t;

typedef struct {
    double rad;
    Vec p, e, c;
    Refl_t refl;
} Sphere;

// intersecao esfera-raio: devolve a distancia t > 0, ou 0 se nao ha.
#ifdef PROFILE
__attribute__((noinline))
#else
static inline
#endif
double sphere_intersect(const Sphere* s, Ray r) {
    Vec op = v_sub(s->p, r.o);
    double eps = 1e-4;
    double b = v_dot(op, r.d);
    double det = b*b - v_dot(op, op) + s->rad * s->rad;
    if (det < 0) return 0;
    det = sqrt(det);
    double t = b - det;
    if (t > eps) return t;
    t = b + det;
    return (t > eps) ? t : 0.0;
}

// cena estilo cornell box do smallpt original: 9 esferas.
static const Sphere kScene[] = {
    { 1e5,  {  1e5+1, 40.8,      81.6}, {0,0,0}, {.75,.25,.25}, DIFF },
    { 1e5,  { -1e5+99,40.8,      81.6}, {0,0,0}, {.25,.25,.75}, DIFF },
    { 1e5,  { 50,     40.8,      1e5 }, {0,0,0}, {.75,.75,.75}, DIFF },
    { 1e5,  { 50,     40.8,     -1e5+170}, {0,0,0}, {0,0,0},    DIFF },
    { 1e5,  { 50,     1e5,       81.6}, {0,0,0}, {.75,.75,.75}, DIFF },
    { 1e5,  { 50,    -1e5+81.6,  81.6}, {0,0,0}, {.75,.75,.75}, DIFF },
    { 16.5, { 27,     16.5,      47  }, {0,0,0}, {.999,.999,.999}, SPEC },
    { 16.5, { 73,     16.5,      78  }, {0,0,0}, {.999,.999,.999}, REFR },
    { 600,  { 50,     681.6-.27, 81.6}, {12,12,12}, {0,0,0},    DIFF },
};
static const int kNumSpheres = (int)(sizeof(kScene) / sizeof(Sphere));

static inline double clamp01(double x) { return x < 0 ? 0 : (x > 1 ? 1 : x); }
static inline int    toInt   (double x) { return (int)(pow(clamp01(x), 1.0/2.2) * 255 + .5); }

#ifdef PROFILE
__attribute__((noinline))
#else
static inline
#endif
int intersect_scene(Ray r, double* t_out, int* id_out) {
    double inf = 1e20;
    double t = inf;
    int id = 0;
    for (int i = kNumSpheres; i--; ) {
        double d = sphere_intersect(&kScene[i], r);
        if (d && d < t) { t = d; id = i; }
    }
    *t_out = t; *id_out = id;
    return t < inf;
}

// gerador xorshift64 com estado por thread. usado no lugar de erand48 porque
// nao depende de estado global oculto e da resultado reprodutivel a partir da
// semente inicial.
typedef struct { uint64_t s; } Rng;

#ifdef PROFILE
__attribute__((noinline))
#else
static inline
#endif
uint64_t rng_next(Rng* r) {
    uint64_t x = r->s ? r->s : 0x1234567u;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    r->s = x;
    return x;
}
#ifdef PROFILE
__attribute__((noinline))
#else
static inline
#endif
double rng_uniform(Rng* r) {
    return (rng_next(r) >> 11) * (1.0 / (double)(1ULL << 53));
}

// radiancia iterativa (loop no lugar de recursao para nao estourar pilha em
// pixels muito reflexivos e para deixar mais claro o ponto de russian roulette).
#ifdef PROFILE
__attribute__((noinline))
#endif
static Vec radiance(Ray r, Rng* rng) {
    Vec cl = {0,0,0};
    Vec cf = {1,1,1};
    int depth = 0;
    while (1) {
        double t; int id = 0;
        if (!intersect_scene(r, &t, &id)) return cl;
        const Sphere* obj = &kScene[id];
        Vec x  = v_add(r.o, v_scl(r.d, t));
        Vec n  = v_norm(v_sub(x, obj->p));
        Vec nl = v_dot(n, r.d) < 0 ? n : v_scl(n, -1);
        Vec f  = obj->c;
        double p_max = (f.x > f.y && f.x > f.z) ? f.x : (f.y > f.z ? f.y : f.z);
        cl = v_add(cl, v_mul(cf, obj->e));
        if (++depth > 5) {
            if (depth > 64) return cl;
            if (rng_uniform(rng) < p_max) f = v_scl(f, 1.0 / p_max);
            else return cl;
        }
        cf = v_mul(cf, f);
        if (obj->refl == DIFF) {
            double r1 = 2 * M_PI * rng_uniform(rng);
            double r2 = rng_uniform(rng);
            double r2s = sqrt(r2);
            Vec w = nl;
            Vec u = v_norm(v_cross((fabs(w.x) > .1 ? v_(0,1,0) : v_(1,0,0)), w));
            Vec v = v_cross(w, u);
            Vec d = v_norm(v_add(v_add(v_scl(u, cos(r1) * r2s), v_scl(v, sin(r1) * r2s)),
                                 v_scl(w, sqrt(1 - r2))));
            r.o = x; r.d = d;
            continue;
        }
        if (obj->refl == SPEC) {
            Vec rd = v_sub(r.d, v_scl(n, 2 * v_dot(n, r.d)));
            r.o = x; r.d = rd;
            continue;
        }
        Ray reflRay; reflRay.o = x; reflRay.d = v_sub(r.d, v_scl(n, 2 * v_dot(n, r.d)));
        int into = v_dot(n, nl) > 0;
        double nc = 1, nt = 1.5;
        double nnt = into ? nc/nt : nt/nc;
        double ddn = v_dot(r.d, nl);
        double cos2t = 1 - nnt*nnt*(1 - ddn*ddn);
        if (cos2t < 0) { r = reflRay; continue; }
        Vec tdir = v_norm(v_sub(v_scl(r.d, nnt),
                                v_scl(n, (into ? 1 : -1) * (ddn*nnt + sqrt(cos2t)))));
        double a = nt - nc, b = nt + nc;
        double R0 = a*a / (b*b);
        double c_ = 1 - (into ? -ddn : v_dot(tdir, n));
        double Re = R0 + (1 - R0) * c_*c_*c_*c_*c_;
        double Tr = 1 - Re;
        double P = .25 + .5 * Re;
        double RP = Re / P, TP = Tr / (1 - P);
        if (depth > 2) {
            if (rng_uniform(rng) < P) { cf = v_scl(cf, RP); r = reflRay; }
            else                       { cf = v_scl(cf, TP); r.o = x; r.d = tdir; }
        } else {
            // escolha ponderada tambem nas primeiras profundidades, para o
            // laco iterativo continuar valido; o peso compensa a escolha
            // com probabilidade 1/2.
            if (rng_uniform(rng) < .5) { cf = v_scl(cf, Re / .5); r = reflRay; }
            else                        { cf = v_scl(cf, Tr / .5); r.o = x; r.d = tdir; }
        }
    }
}

typedef struct {
    int w, h, spp;
    int threads;                 // -1 = deixa openmp decidir (OMP_NUM_THREADS)
    const char* sched;           // NULL ou "static", "dynamic,K", "guided", ...
    int  profile_balance;
    const char* image_out;
    const char* version_label;
    uint64_t seed;
} Args;

static void usage(const char* argv0) {
    fprintf(stderr,
        "uso: %s [-w W] [-h H] [-s SPP] [-t THREADS] [--schedule POL[,CHUNK]]\n"
        "        [--profile-balance] [--image OUT.ppm] [--label NOME] [--seed N]\n"
        "\n"
        "  -w W          largura em pixels (padrao 320)\n"
        "  -h H          altura em pixels (padrao 240)\n"
        "  -s SPP        amostras por subpixel; total 4*spp por pixel (padrao 4)\n"
        "  -t THREADS    fixa OMP_NUM_THREADS via omp_set_num_threads\n"
        "                (evite usar; prefira a variavel de ambiente OMP_NUM_THREADS)\n"
        "  --schedule P  static | static,K | dynamic | dynamic,K | guided | guided,K\n"
        "  --profile-balance   imprime tempo e iteracoes por thread na stderr\n"
        "  --image OUT   grava a imagem em ppm p3 fora da regiao cronometrada\n"
        "  --label L     rotulo da linha csv (seq/omp/omp-static, ...)\n"
        "  --seed N      semente do gerador (padrao 12345)\n", argv0);
}

int main(int argc, char** argv) {
    Args a;
    a.w = 320; a.h = 240; a.spp = 4;
    a.threads = -1;
    a.sched = NULL;
    a.profile_balance = 0;
    a.image_out = NULL;
    a.version_label = "seq";
    a.seed = 12345;

    for (int i = 1; i < argc; ++i) {
        #define NEED(i) do { if ((i)+1 >= argc) { usage(argv[0]); return 2; } } while (0)
        if      (!strcmp(argv[i], "-w"))                 { NEED(i); a.w = atoi(argv[++i]); }
        else if (!strcmp(argv[i], "-h"))                 { NEED(i); a.h = atoi(argv[++i]); }
        else if (!strcmp(argv[i], "-s"))                 { NEED(i); a.spp = atoi(argv[++i]); }
        else if (!strcmp(argv[i], "-t"))                 { NEED(i); a.threads = atoi(argv[++i]); }
        else if (!strcmp(argv[i], "--schedule"))         { NEED(i); a.sched = argv[++i]; }
        else if (!strcmp(argv[i], "--profile-balance"))  { a.profile_balance = 1; }
        else if (!strcmp(argv[i], "--image"))            { NEED(i); a.image_out = argv[++i]; }
        else if (!strcmp(argv[i], "--label"))            { NEED(i); a.version_label = argv[++i]; }
        else if (!strcmp(argv[i], "--seed"))             { NEED(i); a.seed = (uint64_t)atoll(argv[++i]); }
        else if (!strcmp(argv[i], "--help") || !strcmp(argv[i], "-?")) { usage(argv[0]); return 0; }
        else { fprintf(stderr, "opcao desconhecida: %s\n", argv[i]); usage(argv[0]); return 2; }
        #undef NEED
    }

    if (a.w <= 0 || a.h <= 0 || a.spp <= 0) {
        fprintf(stderr, "erro: w, h, spp devem ser positivos\n");
        return 2;
    }

#ifdef _OPENMP
    if (a.threads > 0) omp_set_num_threads(a.threads);
    int threads_used = 0;
    int nprocs = omp_get_num_procs();
    #pragma omp parallel
    { if (omp_get_thread_num() == 0) threads_used = omp_get_num_threads(); }
    if (a.sched) setenv("OMP_SCHEDULE", a.sched, 1);
#else
    int threads_used = 1;
    int nprocs = 1;
#endif
    fprintf(stderr, "nprocs=%d threads_used=%d\n", nprocs, threads_used);

    // perfil por thread com padding para evitar false sharing quando threads
    // adjacentes gravam contadores adjacentes. este vetor e usado apenas para
    // a instrumentacao de balanceamento e nao entra na fase computacional
    // medida (por isso alocado antes de t0).
    typedef struct { double time; long iters; char pad[64 - sizeof(double) - sizeof(long)]; } ThreadStat;
    ThreadStat* stat = (ThreadStat*)calloc((size_t)threads_used, sizeof(ThreadStat));
    if (!stat) { fprintf(stderr, "erro: sem memoria (stat)\n"); return 1; }

    // t0 abre a fase computacional completa: setup da camera, alocacao do
    // buffer, laco paralelo e checksum. so a escrita PPM e o print do csv
    // ficam fora, conforme o enunciado permite (I/O). t_par e t_par_end
    // capturam o tempo isolado do trecho paralelizado, que e reportado como
    // medida complementar.
    double t0 = now_s();

    // camera: mesma do smallpt original, com aspect adaptado a wxh.
    Vec cam_o = v_(50, 52, 295.6);
    Vec cam_d = v_norm(v_(0, -0.042612, -1));
    Vec cx = v_(a.w * 0.5135 / a.h, 0, 0);
    Vec cy = v_scl(v_norm(v_cross(cx, cam_d)), 0.5135);

    Vec* c = (Vec*)calloc((size_t)a.w * (size_t)a.h, sizeof(Vec));
    if (!c) { fprintf(stderr, "erro: sem memoria\n"); return 1; }

    double t_par = now_s();

#ifdef _OPENMP
    // laco externo sobre linhas y da imagem: cada linha e independente
    // porque escreve em uma faixa disjunta do buffer c. schedule(runtime)
    // deixa a politica ser escolhida por OMP_SCHEDULE, o que permite comparar
    // static/dynamic/guided sem recompilar. o rng e local ao laco, portanto
    // private por construcao, e recebe uma semente unica por linha: assim o
    // resultado nao depende do numero de threads.
    #pragma omp parallel default(none) \
            shared(a, c, cam_o, cam_d, cx, cy, stat, threads_used)
    {
        double tt0 = omp_get_wtime();
        long   itcount = 0;
        int    tid     = omp_get_thread_num();

        // nowait: sem a barreira implicita do `for` o tempo capturado
        // apos o laco reflete a carga real da thread, nao o momento em
        // que a ultima thread chega. isso torna o perfil de
        // balanceamento honesto. como nao ha uso do buffer c dentro da
        // regiao paralela apos o laco, o nowait e seguro.
        #pragma omp for schedule(runtime) nowait
        for (int y = 0; y < a.h; ++y) {
            Rng rng; rng.s = a.seed ^ ((uint64_t)(y + 1) * 0x9E3779B97F4A7C15ULL);
            for (int x = 0; x < a.w; ++x) {
                Vec r_pixel = {0,0,0};
                for (int sy = 0; sy < 2; ++sy) {
                    for (int sx = 0; sx < 2; ++sx) {
                        Vec r_sub = {0,0,0};
                        for (int s = 0; s < a.spp; ++s) {
                            double r1 = 2 * rng_uniform(&rng);
                            double dx = r1 < 1 ? sqrt(r1) - 1 : 1 - sqrt(2 - r1);
                            double r2 = 2 * rng_uniform(&rng);
                            double dy = r2 < 1 ? sqrt(r2) - 1 : 1 - sqrt(2 - r2);
                            Vec d = v_add(v_add(v_scl(cx, (((sx + .5 + dx) / 2 + x) / a.w - .5)),
                                                v_scl(cy, (((sy + .5 + dy) / 2 + y) / a.h - .5))),
                                          cam_d);
                            Ray ray; ray.o = v_add(cam_o, v_scl(d, 140)); ray.d = v_norm(d);
                            r_sub = v_add(r_sub, v_scl(radiance(ray, &rng), 1.0 / a.spp));
                        }
                        r_pixel = v_add(r_pixel, v_scl(v_(clamp01(r_sub.x),
                                                          clamp01(r_sub.y),
                                                          clamp01(r_sub.z)), .25));
                    }
                }
                c[(size_t)y * a.w + x] = r_pixel;
            }
            itcount += a.w;
        }

        stat[tid].time  = omp_get_wtime() - tt0;
        stat[tid].iters = itcount;
    }
#else
    // versao sequencial: mesma logica, sem regiao paralela. este binario e o
    // T1 de referencia do relatorio.
    for (int y = 0; y < a.h; ++y) {
        Rng rng; rng.s = a.seed ^ ((uint64_t)(y + 1) * 0x9E3779B97F4A7C15ULL);
        for (int x = 0; x < a.w; ++x) {
            Vec r_pixel = {0,0,0};
            for (int sy = 0; sy < 2; ++sy) {
                for (int sx = 0; sx < 2; ++sx) {
                    Vec r_sub = {0,0,0};
                    for (int s = 0; s < a.spp; ++s) {
                        double r1 = 2 * rng_uniform(&rng);
                        double dx = r1 < 1 ? sqrt(r1) - 1 : 1 - sqrt(2 - r1);
                        double r2 = 2 * rng_uniform(&rng);
                        double dy = r2 < 1 ? sqrt(r2) - 1 : 1 - sqrt(2 - r2);
                        Vec d = v_add(v_add(v_scl(cx, (((sx + .5 + dx) / 2 + x) / a.w - .5)),
                                            v_scl(cy, (((sy + .5 + dy) / 2 + y) / a.h - .5))),
                                      cam_d);
                        Ray ray; ray.o = v_add(cam_o, v_scl(d, 140)); ray.d = v_norm(d);
                        r_sub = v_add(r_sub, v_scl(radiance(ray, &rng), 1.0 / a.spp));
                    }
                    r_pixel = v_add(r_pixel, v_scl(v_(clamp01(r_sub.x),
                                                      clamp01(r_sub.y),
                                                      clamp01(r_sub.z)), .25));
                }
            }
            c[(size_t)y * a.w + x] = r_pixel;
        }
    }
    stat[0].time  = now_s() - t_par;
    stat[0].iters = (long)a.w * (long)a.h;
#endif

    double t_par_end = now_s();
    double t_par_elapsed = t_par_end - t_par;

    double checksum = 0.0;
    size_t npix = (size_t)a.w * (size_t)a.h;
    for (size_t i = 0; i < npix; ++i) checksum += c[i].x + c[i].y + c[i].z;

    // t1 fecha a fase computacional completa. e este o tempo usado para
    // calcular speed-up e eficiencia; t_par_elapsed vai como coluna
    // complementar no csv, para diagnostico.
    double t1 = now_s();
    double elapsed = t1 - t0;

    // schedule pode conter virgula (ex: "static,32"); troca-se por '_' na
    // impressao para nao quebrar o csv.
    char sched_out[64];
    {
        const char* src = a.sched ? a.sched : "default";
        size_t n = strlen(src);
        if (n >= sizeof(sched_out)) n = sizeof(sched_out) - 1;
        for (size_t i = 0; i < n; ++i) sched_out[i] = (src[i] == ',') ? '_' : src[i];
        sched_out[n] = '\0';
    }
    // csv: time_s eh o tempo da fase computacional completa (usado no
    // speed-up e na eficiencia); time_par_s eh o tempo isolado do trecho
    // paralelizado, reportado como medida complementar conforme o
    // enunciado.
    printf("version,label,threads,schedule,w,h,spp,time_s,time_par_s,checksum\n");
    printf("csv,%s,%d,%s,%d,%d,%d,%.6f,%.6f,%.6f\n",
           a.version_label, threads_used,
           sched_out,
           a.w, a.h, a.spp, elapsed, t_par_elapsed, checksum);

    if (a.profile_balance) {
        fprintf(stderr, "# thread,time_s,iters\n");
        for (int t = 0; t < threads_used; ++t) {
            fprintf(stderr, "balance,%d,%.6f,%ld\n", t, stat[t].time, stat[t].iters);
        }
    }

    if (a.image_out) {
        FILE* f = fopen(a.image_out, "w");
        if (f) {
            fprintf(f, "P3\n%d %d\n%d\n", a.w, a.h, 255);
            for (int y = a.h - 1; y >= 0; --y) {
                for (int x = 0; x < a.w; ++x) {
                    Vec v = c[(size_t)y * a.w + x];
                    fprintf(f, "%d %d %d ", toInt(v.x), toInt(v.y), toInt(v.z));
                }
                fputc('\n', f);
            }
            fclose(f);
        }
    }

    free(c);
    free(stat);
    return 0;
}
