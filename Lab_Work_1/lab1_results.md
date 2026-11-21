# Lab Work 1 - generated results

## Environment and experimental setup

- **Python version:** 3.13.18 (main, Oct 26 2026, 14:08:19) [Clang 23.1.3 ]
- **Implementation:** CPython
- **Platform:** Linux-6.18.44-fc-v726-x86_64-with-glibc2.39
- **Machine / processor:** x86_64 / x86_64
- **Timer:** time.perf_counter (resolution 1.0e-09 s)
- **Seed:** 2024
- **Trials per point:** 7 (plus one warm-up)
- **Reported statistic:** MEDIAN of the trials (mean, stdev and min also saved in the CSV)
- **GC during timing:** disabled

Input data: pseudo-random integers from `random.Random(SEED + n)`; data generation is outside the timed region.

## Comparison table

| Algorithm | Theoretical bound | Measured trend | Experimental limitations |
|---|---|---|---|
| List indexing | O(1) | log-log slope = 0.21; max/min time over the whole range = 3.82x (n grows 1024x) | Loop overhead is much bigger than the look-up itself; cache misses on big lists can add a small upward drift. |
| Binary search | O(log n) | log-log slope = 0.19; R^2 of T vs log2(n) = 0.8889 | Only 10-20 loop iterations per search, so call/interpreter overhead dominates; cache misses on large lists make growth look slightly faster than log n. |
| Linear search | O(n) | log-log slope = 1.07; R^2 of T vs n = 0.9902 | Worst case only (key absent); best and average cases are different. Per-element cost is large because the loop runs in the interpreter. |
| Merge sort | O(n log n) | log-log slope = 1.13; R^2 of T vs n log2(n) = 0.9970 | Slicing and list allocation add constant-factor and memory overhead; over a short range of n the log n factor is hard to separate from plain n. |
| Double-loop pair counter | O(n^2) | log-log slope = 2.05; R^2 of T vs n^2 = 1.0000 | n is capped at 3200 to keep the run short, so only five points; the inner loop overhead sets the constant. |
| Subset enumeration | O(2^n) | log-log slope = 10.75; R^2 of T vs 2^n = 0.9987; T(n+1)/T(n) averages 2.11 (ideal 2) | Only small n (10-20) is feasible: memory grows as 2^n (about 1 million sums at n = 20). Allocation cost makes the ratio between steps slightly irregular. |

## Timing data (median of trials)

### List indexing - O(1)  (µs per look-up)

| n | median | normalised T(n) |
|---|---|---|
| 1,024 | 0.0165 | 0.016509 |
| 2,048 | 0.0139 | 0.013875 |
| 4,096 | 0.0130 | 0.012985 |
| 8,192 | 0.0133 | 0.013283 |
| 16,384 | 0.0135 | 0.013529 |
| 32,768 | 0.0185 | 0.018488 |
| 65,536 | 0.0254 | 0.025386 |
| 131,072 | 0.0339 | 0.033904 |
| 262,144 | 0.0371 | 0.037109 |
| 524,288 | 0.0474 | 0.047386 |
| 1,048,576 | 0.0496 | 0.049571 |

### Binary search - O(log n)  (µs per search)

| n | median | normalised T(n)/log2(n) |
|---|---|---|
| 1,024 | 0.9949 | 0.099489 |
| 2,048 | 1.1090 | 0.100817 |
| 4,096 | 1.1968 | 0.099736 |
| 8,192 | 1.3975 | 0.107498 |
| 16,384 | 1.5649 | 0.111778 |
| 32,768 | 1.7216 | 0.114776 |
| 65,536 | 1.8703 | 0.116894 |
| 131,072 | 2.2187 | 0.130513 |
| 262,144 | 2.6177 | 0.145430 |
| 524,288 | 2.9422 | 0.154854 |
| 1,048,576 | 3.9519 | 0.197594 |

### Linear search - O(n)  (ms per search)

| n | median | normalised T(n)/n |
|---|---|---|
| 10,000 | 0.2116 | 0.000021 |
| 20,000 | 0.4315 | 0.000022 |
| 40,000 | 0.9012 | 0.000023 |
| 80,000 | 1.9293 | 0.000024 |
| 160,000 | 3.7474 | 0.000023 |
| 320,000 | 7.6930 | 0.000024 |
| 640,000 | 19.1688 | 0.000030 |

### Merge sort - O(n log n)  (ms per sort)

| n | median | normalised T(n)/(n log2 n) |
|---|---|---|
| 1,000 | 1.0903 | 0.000109 |
| 2,000 | 2.3535 | 0.000107 |
| 4,000 | 5.1294 | 0.000107 |
| 8,000 | 11.4284 | 0.000110 |
| 16,000 | 23.9821 | 0.000107 |
| 32,000 | 52.5423 | 0.000110 |
| 64,000 | 112.5966 | 0.000110 |
| 128,000 | 271.0260 | 0.000125 |

### Double-loop pair counter - O(n^2)  (ms per run)

| n | median | normalised T(n)/n^2 |
|---|---|---|
| 200 | 0.5470 | 0.000014 |
| 400 | 2.3551 | 0.000015 |
| 800 | 9.8541 | 0.000015 |
| 1,600 | 39.4619 | 0.000015 |
| 3,200 | 161.3391 | 0.000016 |

### Subset enumeration - O(2^n)  (ms per run)

| n | median | normalised T(n)/2^n |
|---|---|---|
| 10 | 0.0369 | 0.000036 |
| 11 | 0.0809 | 0.000039 |
| 12 | 0.1598 | 0.000039 |
| 13 | 0.3297 | 0.000040 |
| 14 | 0.6233 | 0.000038 |
| 15 | 1.5141 | 0.000046 |
| 16 | 3.2382 | 0.000049 |
| 17 | 6.6600 | 0.000051 |
| 18 | 13.4021 | 0.000051 |
| 19 | 31.6438 | 0.000060 |
| 20 | 61.3306 | 0.000058 |
