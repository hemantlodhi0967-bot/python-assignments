# Lab Work (Prefix Averages) - generated results

## Environment and setup

- **Python version:** 3.13.18 (main, Oct 26 2026, 14:08:19) [Clang 23.1.3 ]
- **Platform:** Linux-6.18.44-fc-v726-x86_64-with-glibc2.39
- **Timer:** time.perf_counter (resolution 1.0e-09 s)
- **Seed:** 2024
- **Trials:** 7 per point (plus one warm-up); reported value = MEDIAN
- **Input:** random integers in [-1000, 1000], generated outside the timed region
- **Tiny inputs:** call repeated ~200,000/work times inside one timing, result divided back to one call

## Validation tests

| Case | Input | Output (A) | Both methods identical? | Max abs error vs exact |
|---|---|---|---|---|
| empty input | `[]` | `[]` | True | 0.0e+00 |
| singleton | `[7]` | `[7.0]` | True | 0.0e+00 |
| singleton negative | `[-4]` | `[-4.0]` | True | 0.0e+00 |
| positive values | `[1, 2, 3, 4, 5]` | `[1.0, 1.5, 2.0, 2.5, 3.0]` | True | 0.0e+00 |
| negative values | `[-1, -2, -3, -4]` | `[-1.0, -1.5, -2.0, -2.5]` | True | 0.0e+00 |
| mixed values | `[3, -1, 4, -1, 5, -9, 2, 6]` | `[3.0, 1.0, 2.0, 1.25, 2.0, 0.166667, 0.428571, 1.125]` | True | 2.4e-17 |
| all zeros | `[0, 0, 0]` | `[0.0, 0.0, 0.0]` | True | 0.0e+00 |
| floats | `[0.1, 0.2, 0.3, 0.4]` | `[0.1, 0.15, 0.2, 0.25]` | True | 3.7e-17 |

## Operation counts (additions)

| n | prefix_average1 counted | n(n+1)/2 | prefix_average2 counted | n |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 |
| 1 | 1 | 1 | 1 | 1 |
| 2 | 3 | 3 | 2 | 2 |
| 5 | 15 | 15 | 5 | 5 |
| 10 | 55 | 55 | 10 | 10 |
| 50 | 1275 | 1275 | 50 | 50 |
| 100 | 5050 | 5050 | 100 | 100 |
| 500 | 125250 | 125250 | 500 | 500 |

## Numerical precision

- Both methods add the elements in the same left-to-right order, so their outputs are bit-for-bit identical on random float data: **True**.
- Max relative error of the running-sum averages vs exact arithmetic (2000 floats, magnitudes 1e-8..1e8): **5.37e-12**.
- Same data using `math.fsum` for every prefix: **1.91e-16**.
- Cancellation example `[1e+16, 1.0, -1e+16]`: computed `[1e+16, 5000000000000000.0, 0.0]`, exact `[1e+16, 5000000000000000.0, 0.3333333333333333]`.

## Timing table (median of trials)

| n | prefix_average1 (µs) | prefix_average2 (µs) | T1 / T2 |
|---|---|---|---|
| 1 | 0.32 | 0.19 | 1.7 |
| 2 | 0.59 | 0.22 | 2.7 |
| 5 | 0.88 | 0.36 | 2.4 |
| 10 | 2.25 | 0.58 | 3.8 |
| 20 | 6.69 | 1.13 | 5.9 |
| 50 | 33.87 | 2.97 | 11.4 |
| 100 | 130.33 | 4.65 | 28.0 |
| 200 | 496.83 | 9.63 | 51.6 |
| 500 | 3289.14 | 30.31 | 108.5 |
| 1,000 | 14497.98 | 65.18 | 222.4 |
| 2,000 | 61403.87 | 131.85 | 465.7 |
| 4,000 | 262640.57 | 269.87 | 973.2 |
| 8,000 | (not run) | 547.00 | - |
| 16,000 | (not run) | 1095.33 | - |
| 32,000 | (not run) | 2425.38 | - |
| 64,000 | (not run) | 7659.78 | - |
| 128,000 | (not run) | 9101.66 | - |
| 256,000 | (not run) | 22103.84 | - |

- log-log slope for n >= 200: prefix_average1 = **2.10** (O(n^2) -> 2), prefix_average2 = **1.07** (O(n) -> 1)
- Smallest tested n with T1/T2 >= 1.5, 2, 10: **1, 2, 50**