#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <errno.h>
#include <math.h>

typedef struct { unsigned a, b; } Edge;
static uint32_t random_state;
static uint32_t next_random(void) {
    uint32_t x = random_state;
    x ^= x << 13; x ^= x >> 17; x ^= x << 5;
    return random_state = x;
}
static unsigned below(unsigned bound) {
    uint32_t limit = (UINT32_MAX / bound) * bound;
    for (;;) {
        uint32_t x = next_random() - 1;
        if (x < limit) return x % bound;
    }
}
static int compare_edges(const void *p, const void *q) {
    const Edge *a = p, *b = q;
    if (a->a != b->a) return a->a < b->a ? -1 : 1;
    return (a->b > b->b) - (a->b < b->b);
}
static void add_edge(unsigned a, unsigned b, unsigned n, unsigned char *seen,
                     Edge *edges, unsigned *count) {
    if (a == b) return;
    if (a > b) { unsigned tmp = a; a = b; b = tmp; }
    size_t index = (size_t)a * n + b;
    if (!seen[index]) { seen[index] = 1; edges[(*count)++] = (Edge){a,b}; }
}
static int parse(const char *s, unsigned long *out) {
    if (!*s) return 0;
    for (const char *p = s; *p; ++p) if (*p < '0' || *p > '9') return 0;
    errno = 0; char *end;
    *out = strtoul(s, &end, 10);
    return !errno && !*end;
}
int main(int argc, char **argv) {
    unsigned long p[5];
    if (argc != 6) goto invalid;
    for (int j = 0; j < 5; ++j) if (!parse(argv[j+1], &p[j])) goto invalid;
    if (p[0]<2 || p[0]>2000 || p[1]>4 || p[2]>100 || p[3]<1 || p[3]>100 ||
        p[4]<1 || p[4]>UINT32_MAX) goto invalid;
    unsigned n=(unsigned)p[0], shortcuts=(unsigned)p[1], beta=(unsigned)p[2], gamma=(unsigned)p[3];
    random_state=(uint32_t)p[4];
    unsigned capacity=n*(shortcuts+1), count=0;
    unsigned char *seen=calloc((size_t)n*n,1), *state=calloc(n,1);
    Edge *edges=malloc((size_t)capacity*sizeof(*edges));
    unsigned *targets=malloc((size_t)capacity*sizeof(*targets));
    if (!seen || !state || !edges || !targets) {
        free(seen); free(state); free(edges); free(targets);
        fputs("allocation failed\n",stderr); return 1;
    }
    for (unsigned j=0;j<n;++j) add_edge(j,(j+1)%n,n,seen,edges,&count);
    for (unsigned j=0;j<n*shortcuts;++j) {
        unsigned a=below(n), b=below(n);
        add_edge(a,b,n,seen,edges,&count);
    }
    free(seen); qsort(edges,count,sizeof(*edges),compare_edges);
    state[0]=1;
    unsigned s=n-1, infected=1, recovered=0, step=0;
    double time=0;
    puts("event,time,node,transition,S,I,R");
    printf("0,0.000000000000,0,initial,%u,1,0\n",s);
    while (infected) {
        unsigned si=0;
        for (unsigned j=0;j<count;++j) {
            unsigned a=edges[j].a, b=edges[j].b;
            if (state[a]==1 && state[b]==0) targets[si++]=b;
            else if (state[b]==1 && state[a]==0) targets[si++]=a;
        }
        unsigned rate=beta*si+gamma*infected;
        time += -log(next_random()/4294967296.0)/rate;
        unsigned ticket=below(rate), node=0;
        const char *transition;
        if (ticket < beta*si) {
            node=targets[ticket/beta]; state[node]=1; --s; ++infected;
            transition="infect";
        } else {
            unsigned index=(ticket-beta*si)/gamma;
            for (node=0;node<n;++node) if (state[node]==1) {
                if (index==0) break;
                --index;
            }
            state[node]=2; --infected; ++recovered; transition="recover";
        }
        printf("%u,%.12f,%u,%s,%u,%u,%u\n",++step,time,node,transition,s,infected,recovered);
    }
    free(state); free(edges); free(targets);
    return ferror(stdout) ? 1 : 0;
invalid:
    fputs("usage: faultline N shortcuts beta gamma seed\nlimits: N=2..2000, shortcuts=0..4, beta=0..100, gamma=1..100, seed=1..4294967295\n",stderr);
    return 2;
}
