# Lab Work 1: Benchmarking Algorithmic Growth Rates

**Name:** Hemant Lodhi  **Roll No.:** 25BME024

## Objective
Empirically investigate constant, logarithmic, linear, n log n, quadratic and exponential growth patterns in Python.

## Experimental setup
| Item | Value |
|---|---|
| Python / platform | CPython 3.13.18, Linux x86_64 (`Linux-6.18.44-fc-v726-x86_64-with-glibc2.39`) |
| Libraries | Standard library only; `matplotlib` used just for plotting |
| Timer | `time.perf_counter` (1 ns resolution) |
| Trials | 7 timed runs per (algorithm, n) after 1 warm-up run |
| Reported value | **Median** of the 7 trials (mean, stdev, min are in the CSV) |
| Input generation | `random.Random(2024 + n)`; created **outside** the timed region |
| Garbage collector | Disabled only while timing |

Input characteristics and input sizes

| Algorithm | Input | Sizes n | What is timed |
|---|---|---|---|
| List indexing | random list, 50,000 random indices | 2^10 … 2^20 | time per look-up |
| Binary search | sorted distinct list, 5,000 random keys (mostly absent) | 2^10 … 2^20 | time per search |
| Linear search | random list, key never present (worst case) | 10,000 … 640,000 | one full scan |
| Merge sort | random list | 1,000 … 128,000 | one sort |
| Double-loop pair counter | random list, count pairs i<j with a[i]+a[j] = 10^6 | 200 … 3,200 | one run |
| Subset enumeration | n random ints (1–100), count subsets with sum = half the total | 10 … 20 | one run |

Exponential enumeration is limited to n ≤ 20 (about one million subsets) because both time and memory double with every extra element. Before timing, the script checks every algorithm against a trusted reference (`sorted`, `itertools`).

## Comparison table
| Algorithm | Theoretical bound | Measured trend | Experimental limitations |
|---|---|---|---|
| List indexing | O(1) | Flat for n ≤ 16k (about 0.013 µs), then rises to about 0.05 µs at n = 1M (3.8x); log-log slope 0.21 | Loop overhead dominates; large lists no longer fit in CPU cache |
| Binary search | O(log n) | T grows with log n at first; T/log2 n rises from 0.099 to 0.198 at n = 1M; R² vs log2 n = 0.889 | Only 10–20 iterations per search; cache misses on large lists |
| Linear search | O(n) | log-log slope 1.07; R² vs n = 0.990; about 21–24 ns per element up to 320k | Worst case only; interpreter loop is slow per element |
| Merge sort | O(n log n) | log-log slope 1.13; R² vs n log n = 0.997; T/(n log2 n) ≈ 107–110 ns, 125 ns at n = 128k | Slicing and list allocation overhead; log factor hard to separate from n in a short range |
| Double-loop pair counter | O(n²) | log-log slope 2.05; R² = 1.000; T/n² ≈ 14–16 ns | n limited to 3,200 (5 points) |
| Subset enumeration | O(2ⁿ) | T(n+1)/T(n) averages 2.11 (ideal 2); R² vs 2ⁿ = 0.999 | n limited to 20; memory doubles with n |

Full timing data: `lab1_timing_data.csv` and `lab1_results.md`.
Plots: `lab1_time_vs_n.png` (T against n with fitted c·f(n)) and `lab1_normalised.png` (T/n, T/(n log2 n), T/n², T/2ⁿ, ...).

## Analysis
**Constants.** The theoretical bounds hide constant factors, and here they are large because everything runs in the interpreter. One loop step costs about 20 ns, so a linear scan of 640,000 items takes about 19 ms, and the pair counter spends about 30 ns per pair (T/n² is 14–16 ns and there are n²/2 pairs). Constants also explain why a "fast" O(log n) binary search (about 1 µs) is still slower per call than a single list look-up (about 0.013 µs): each search runs 10–20 loop iterations plus a function call.

**Lower-order terms.** Merge sort is the clearest case. Slicing, list creation and `extend` add extra O(n) work per level, and for small n the lower-order terms are visible. T/(n log2 n) is flat at about 107–110 ns for n up to 64,000. Over the short range tested (128x), n log n and n are hard to tell apart, which is why the log-log slope is 1.13 rather than 1.
**Interpreter overhead.** Python hides the cost of single operations behind loop and call overhead. The O(1) look-up is measured as "loop + look-up", so its absolute value mainly shows loop speed. This is why per-operation figures should be read as relative trends, not as the cost of a machine instruction.

**Input limits and memory effects.** For the O(1) and O(log n) cases the measured time is **not** flat or logarithmic over the whole range. After about 16,000 elements the list no longer fits in the fast CPU cache, so random access gets slower: look-up time rises from 0.013 µs to about 0.05 µs, and binary search runs 2x above its log-n shape at n = 1M. This is the memory hierarchy and not an algorithmic change, so the idealised O(1) and O(log n) models hold only while the data stays in cache. Exponential enumeration cannot be pushed past n ≈ 20 here, because n = 30 would need about a billion subset sums. The slow upward drift in T/2ⁿ (36 ns to 58 ns) comes from allocating larger and larger lists.

**Do the measurements agree with the expected growth classes?** Yes for linear, n log n, quadratic and exponential: the fitted R² values are 0.99–1.00 and the normalised plots are close to flat. The log-log slopes (1.07, 1.13, 2.05) are close to 1, 1 + a small log-factor, and 2. The exponential case doubles per extra element (average ratio 2.11). The O(1) and O(log n) cases agree only roughly, with the cache-related deviation described above.

## Deliverables
- Python source: `lab1_growth_rates.py`
- Experimental setup: this report (and the top of `lab1_results.md`)
- Timing data: `lab1_timing_data.csv`, `lab1_results.md`
- Plots: `lab1_time_vs_n.png`, `lab1_normalised.png`
- Comparison table: above
