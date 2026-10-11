import csv
import io
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'python'))
from faultline import RNG, graph, simulate

C_BINARY = os.environ.get('FAULTLINE_C', str(ROOT / 'build' / ('faultline.exe' if os.name == 'nt' else 'faultline')))


def run_c(args):
    result = subprocess.run([C_BINARY, *map(str, args)], capture_output=True, text=True, check=True)
    return list(csv.DictReader(io.StringIO(result.stdout)))


class Tests(unittest.TestCase):
    def test_rng_known_vector(self):
        rng = RNG(1)
        self.assertEqual([rng.next() for _ in range(5)],
                         [270369, 67634689, 2647435461, 307599695, 2398689233])

    def test_300_cross_language_paths_and_replay(self):
        source = random.Random(8128)
        cases = [(2, 0, 0, 1, 1), (2, 4, 100, 100, 0xffffffff), (2000, 0, 0, 1, 19)]
        cases += [(source.randint(2, 100), source.randrange(5), source.randrange(11),
                   source.randint(1, 10), source.randint(1, 0xffffffff)) for _ in range(297)]
        for args in cases:
            with self.subTest(args=args):
                rows = list(simulate(*args))
                c_rows = run_c(args)
                self.assertEqual(len(rows), len(c_rows))
                n, shortcuts, _, _, seed = args
                edges = graph(n, shortcuts, RNG(seed))
                state = [0] * n
                state[0] = 1
                previous_time = 0
                for row, other in zip(rows, c_rows):
                    event, time, node, transition, s, i, r = row
                    self.assertEqual((event, node, transition, s, i, r),
                                     (int(other['event']), int(other['node']), other['transition'],
                                      int(other['S']), int(other['I']), int(other['R'])))
                    self.assertTrue(math.isclose(time, float(other['time']), rel_tol=1e-11, abs_tol=2e-12))
                    if event:
                        self.assertGreater(time, previous_time)
                        if transition == 'infect':
                            self.assertEqual(state[node], 0)
                            self.assertTrue(any((a == node and state[b] == 1) or
                                                (b == node and state[a] == 1) for a, b in edges))
                            state[node] = 1
                        else:
                            self.assertEqual(state[node], 1)
                            state[node] = 2
                    self.assertEqual((s, i, r), tuple(state.count(k) for k in range(3)))
                    self.assertEqual(s + i + r, n)
                    previous_time = time
                self.assertEqual(rows[-1][5], 0)
                self.assertLessEqual(len(rows), 2*n)

    def test_no_transmission_analytical_time(self):
        for seed in (1, 5, 42, 0xffffffff):
            rng = RNG(seed)
            graph(20, 0, rng)
            expected = -math.log(rng.next() / 4294967296.0) / 7
            rows = list(simulate(20, 0, 0, 7, seed))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[-1][1], expected)
            self.assertEqual(rows[-1][-3:], (19, 0, 1))

    def test_two_node_first_event_distribution(self):
        source = random.Random(991)
        infections = sum(list(simulate(2, 0, 3, 1, source.randint(1, 0xffffffff)))[1][3] == 'infect'
                         for _ in range(2000))
        # Analytical P(first event is infection)=3/(3+1). Loose deterministic smoke bound.
        self.assertTrue(0.70 < infections/2000 < 0.80, infections)

    def test_graph_invariants(self):
        for n in (2, 3, 17, 100):
            edges = graph(n, 4, RNG(42))
            self.assertEqual(edges, sorted(set(edges)))
            self.assertTrue(all(0 <= a < b < n for a, b in edges))
            self.assertTrue(all(tuple(sorted((a, (a+1)%n))) in edges for a in range(n)))

    def test_invalid_cli(self):
        for args in ([], ['2','0','1','1','0'], ['2001','0','1','1','1'],
                     ['2','5','1','1','1'], ['2','0','1','0','1'], ['2','0','101','1','1'],
                     ['2','0','1','1','4294967296'], ['2','0','1','1','-1'],
                     ['2','0','1','1','1x'], ['2','0','1','1','١']):
            for command in ([sys.executable, str(ROOT/'python/faultline.py')], [C_BINARY]):
                result = subprocess.run([*command, *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, (command,args,result.stderr))
                self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
