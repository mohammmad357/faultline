"""Deterministic cross-language network SIR, using the direct SSA method."""
import math
import sys


class RNG:
    def __init__(self, seed):
        self.state = seed

    def next(self):
        x = self.state
        x ^= (x << 13) & 0xffffffff
        x ^= x >> 17
        x ^= (x << 5) & 0xffffffff
        self.state = x
        return x

    def below(self, bound):
        # Nonzero xorshift visits 1..2^32-1, not 0..2^32-1.
        limit = (0xffffffff // bound) * bound
        while True:
            x = self.next() - 1
            if x < limit:
                return x % bound


def graph(n, shortcuts, rng):
    edges = {tuple(sorted((i, (i + 1) % n))) for i in range(n)}
    for _ in range(n * shortcuts):
        a, b = rng.below(n), rng.below(n)
        if a != b:
            edges.add(tuple(sorted((a, b))))
    return sorted(edges)


def simulate(n, shortcuts, beta, gamma, seed):
    rng = RNG(seed)
    edges = graph(n, shortcuts, rng)
    state = [0] * n
    state[0] = 1
    s, infected, recovered, time = n - 1, 1, 0, 0.0
    yield (0, time, 0, 'initial', s, infected, recovered)
    step = 0
    while infected:
        targets = [b if state[a] == 1 else a for a, b in edges
                   if {state[a], state[b]} == {0, 1}]
        rate = beta * len(targets) + gamma * infected
        time += -math.log(rng.next() / 4294967296.0) / rate
        ticket = rng.below(rate)
        if ticket < beta * len(targets):
            node = targets[ticket // beta]
            state[node] = 1
            s -= 1
            infected += 1
            transition = 'infect'
        else:
            ticket = (ticket - beta * len(targets)) // gamma
            node = [i for i, value in enumerate(state) if value == 1][ticket]
            state[node] = 2
            infected -= 1
            recovered += 1
            transition = 'recover'
        step += 1
        yield (step, time, node, transition, s, infected, recovered)


def parameters(args):
    if len(args) != 5 or any(not x.isascii() or not x.isdecimal() for x in args):
        raise ValueError('expected five unsigned decimal integers')
    n, shortcuts, beta, gamma, seed = map(int, args)
    if not (2 <= n <= 2000 and 0 <= shortcuts <= 4 and 0 <= beta <= 100
            and 1 <= gamma <= 100 and 1 <= seed <= 0xffffffff):
        raise ValueError('limits: N=2..2000, shortcuts=0..4, beta=0..100, gamma=1..100, seed=1..4294967295')
    return n, shortcuts, beta, gamma, seed


def main():
    try:
        args = parameters(sys.argv[1:])
    except ValueError as error:
        print(f'usage: faultline N shortcuts beta gamma seed\n{error}', file=sys.stderr)
        return 2
    print('event,time,node,transition,S,I,R')
    for step, time, node, transition, s, i, r in simulate(*args):
        print(f'{step},{time:.12f},{node},{transition},{s},{i},{r}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
