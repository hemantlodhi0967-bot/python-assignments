# Lab Work: Prefix Averages - Quadratic versus Linear-Time Design

**Name:** Hemant Lodhi  **Roll No.:** 25BME024

## Objective
Show how a running-sum strategy reduces the prefix-average computation from quadratic to linear time.

Given S[0..n-1], the prefix average is A[j] = (S[0] + S[1] + ... + S[j]) / (j + 1).

## Implementations
- `prefix_average1(S)`: nested loop; for every j it adds S[0..j] again from scratch.
- `prefix_average2(S)`: one running sum; each element is added exactly once.

## Setup
CPython 3.13.18 on Linux x86_64; standard library only (matplotlib for plots). Inputs are random integers in [-1000, 1000] from `random.Random(2024 + n)`, created outside the timed region. 7 trials per point after a warm-up, and **reported values are medians**. For tiny n, one call is too short to time reliably, so it is repeated inside one timing and divided back to one call.

## Validation tests
Singleton, singleton negative, positive, negative, mixed, all-zero, float and **empty** inputs. Both methods give identical output for every case (the script asserts this), and both return `[]` for empty input without raising an error. Both also agree exactly on a random list of 500 numbers. Results are checked against exact `Fraction` arithmetic, and the largest error was about 4e-17 (floats case). The full table is in `lab2_results.md`.

## Derivation of operation counts
Count additions (the dominant operation); `c` terms are constant costs.

**prefix_average1.** For index j (counting from 1 to n) the inner loop does j additions:

```
additions = Σ_{j=1}^{n} j = n(n+1)/2 = n²/2 + n/2
divisions = n
T1(n) = c1·n(n+1)/2 + c2·n + c3 = O(n²)
```

**prefix_average2.** One addition and one division per element:

```
additions = Σ_{j=1}^{n} 1 = n
divisions = n
T2(n) = c4·n + c5 = O(n)
```

**Check by counting.** The instrumented versions in the script count the additions for n = 0, 1, 2, 5, 10, 50, 100, 500. They match the formulas exactly (for example n = 100: 5050 = 100·101/2 for method 1, and 100 for method 2).

## Benchmark results (median)
| n | prefix_average1 | prefix_average2 | T1 / T2 |
|---|---|---|---|
| 10 | 2.25 µs | 0.58 µs | 3.9 |
| 50 | 33.9 µs | 2.97 µs | 11.4 |
| 100 | 130 µs | 4.65 µs | 28 |
| 1,000 | 14.5 ms | 65.2 µs | 222 |
| 4,000 | 263 ms | 270 µs | 973 |
| 256,000 | not run (would take hours) | 22.1 ms | - |

Full data: `lab2_timing_data.csv` and `lab2_results.md`. Plots: `lab2_time_vs_n.png` (linear and log-log with O(n²) and O(n) reference lines) and `lab2_normalised_speedup.png` (T1/n², T2/n and the speed-up ratio).

## Analysis
**Growth rates.** On a log-log plot for n ≥ 200, `prefix_average1` has slope 2.10 and `prefix_average2` has slope 1.07, in line with O(n²) and O(n). The normalised curves T1/n² (about 13–17 ns) and T2/n (about 45–70 ns, with a few noisy points at large n) become roughly flat once n is above about 20, so the bounds fit. For small n the lower-order and fixed costs (function call, list creation) still dominate, which is why the curves start high.

**Constants and lower-order terms.** Per element, method 2 is more expensive than one inner step of method 1 (about 60 ns against about 30 ns, since T1/n² counts n²/2 steps), because it does an extra division, indexing and a list assignment in each pass. The quadratic method wins nothing, though, because it repeats the inner work n/2 times on average.

**When does the improved method become measurably faster?** Already at n = 1 the nested version is slower (about 1.7x), because of the overhead of creating the inner `range` loop. The gap becomes large quickly: at least 2x at n = 2, **10x at n = 50**, 28x at n = 100 and about 1000x at n = 4,000. For sequences of more than a few dozen elements the running-sum method is clearly the better choice.

**Numerical precision.** Both methods add the elements in the same left-to-right order, so on floating-point data their outputs are bit-for-bit identical; the running sum does not make the result less accurate than recomputing. Both still carry normal rounding error: for 2,000 random floats of very different magnitudes (1e-8 to 1e8), the largest relative error against exact arithmetic was about 5e-12. Summing each prefix with `math.fsum` brings that down to about 2e-16. Cancellation is the worst case: for `[1e16, 1.0, -1e16]` the third average should be 1/3, but both methods return 0.0 because the 1.0 is lost when added to 1e16. For integer data Python's integers are exact, so only the final division rounds.

## Deliverables
- Source code: `lab2_prefix_averages.py`
- Validation tests: built into the script (also in `lab2_results.md`)
- Derivations: above (copy these by hand if handwritten notes are required)
- Timing table and plot: above, `lab2_timing_data.csv`, `lab2_time_vs_n.png`, `lab2_normalised_speedup.png`
