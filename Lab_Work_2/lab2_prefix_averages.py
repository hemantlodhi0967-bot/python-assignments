"""
Lab Work: Prefix Averages - Quadratic versus Linear-Time Design
Name    : Hemant Lodhi
Roll No.: 25BME024

Problem
-------
Given a sequence S of n numbers, compute A where A[j] is the average of
S[0], S[1], ..., S[j].

    prefix_average1 : nested loop, recomputes every prefix sum   -> O(n^2)
    prefix_average2 : running sum updated once per new element   -> O(n)

What this script does
---------------------
1. Validates both implementations (singleton, positive, negative, mixed,
   empty input, floats) and compares them with exact Fraction arithmetic.
2. Counts additions to confirm the summation formulas
       prefix_average1 : n(n+1)/2 additions
       prefix_average2 : n additions
3. Shows a numerical-precision example.
4. Benchmarks both versions (repeated trials, median) and plots the trends
   against O(n^2) and O(n).

Run:  python lab2_prefix_averages.py
Output files (written next to this script):
    lab2_timing_data.csv, lab2_time_vs_n.png, lab2_normalised_speedup.png,
    lab2_results.md

Rules followed: Python 3 + standard library (matplotlib only for plotting),
seeded input generation, input generation outside the timed region,
repeated trials, and reported values are MEDIANS.
"""

import csv
import gc
import math
import os
import platform
import random
import statistics
import sys
import time
from fractions import Fraction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 2024
TRIALS = 7
TARGET_STEPS = 200_000   # for tiny n, repeat the call so one timing covers ~this many steps


# ----------------------------------------------------------------------------
# The two implementations
# ----------------------------------------------------------------------------
def prefix_average1(S):
    """Quadratic: for every j, add up S[0..j] again from scratch."""
    n = len(S)
    A = [0.0] * n
    for j in range(n):
        total = 0
        for i in range(j + 1):      # j + 1 additions
            total += S[i]
        A[j] = total / (j + 1)
    return A


def prefix_average2(S):
    """Linear: keep a running sum; each new element is added exactly once."""
    n = len(S)
    A = [0.0] * n
    total = 0
    for j in range(n):
        total += S[j]               # 1 addition
        A[j] = total / (j + 1)
    return A


# Instrumented copies - they return the answer AND the number of additions,
# so we can check the summation formulas experimentally.
def prefix_average1_counted(S):
    n, adds = len(S), 0
    A = [0.0] * n
    for j in range(n):
        total = 0
        for i in range(j + 1):
            total += S[i]
            adds += 1
        A[j] = total / (j + 1)
    return A, adds


def prefix_average2_counted(S):
    n, adds = len(S), 0
    A = [0.0] * n
    total = 0
    for j in range(n):
        total += S[j]
        adds += 1
        A[j] = total / (j + 1)
    return A, adds


def exact_prefix_averages(S):
    """Reference answer using exact rational arithmetic (no rounding at all)."""
    out, total = [], Fraction(0)
    for j, x in enumerate(S):
        total += Fraction(x)
        out.append(total / (j + 1))
    return out


# ----------------------------------------------------------------------------
# Part 1: validation
# ----------------------------------------------------------------------------
VALIDATION_CASES = [
    ("empty input", []),
    ("singleton", [7]),
    ("singleton negative", [-4]),
    ("positive values", [1, 2, 3, 4, 5]),
    ("negative values", [-1, -2, -3, -4]),
    ("mixed values", [3, -1, 4, -1, 5, -9, 2, 6]),
    ("all zeros", [0, 0, 0]),
    ("floats", [0.1, 0.2, 0.3, 0.4]),
]


def run_validation():
    rows = []
    for label, S in VALIDATION_CASES:
        a1, a2 = prefix_average1(S), prefix_average2(S)
        same = (a1 == a2)                       # bit-for-bit identical?
        exact = exact_prefix_averages(S)
        worst = max((abs(Fraction(x) - e) for x, e in zip(a1, exact)), default=Fraction(0))
        rows.append((label, S, a1, a2, same, float(worst)))
        assert same, f"outputs differ for {label}"
        assert len(a1) == len(S)
    # empty input: both must return an empty list and not raise
    assert prefix_average1([]) == [] and prefix_average2([]) == []
    # a larger random test
    rng = random.Random(SEED)
    big = [rng.randint(-1000, 1000) for _ in range(500)]
    assert prefix_average1(big) == prefix_average2(big)
    return rows


# ----------------------------------------------------------------------------
# Part 2: operation counts
# ----------------------------------------------------------------------------
def run_operation_counts(sizes=(0, 1, 2, 5, 10, 50, 100, 500)):
    rows = []
    for n in sizes:
        S = list(range(n))
        _, c1 = prefix_average1_counted(S)
        _, c2 = prefix_average2_counted(S)
        f1, f2 = n * (n + 1) // 2, n
        assert c1 == f1 and c2 == f2
        rows.append((n, c1, f1, c2, f2))
    return rows


# ----------------------------------------------------------------------------
# Part 3: numerical precision
# ----------------------------------------------------------------------------
def run_precision():
    rng = random.Random(SEED)
    # (a) random floats with very different magnitudes
    S = [rng.uniform(-1, 1) * 10 ** rng.randint(-8, 8) for _ in range(2000)]
    exact = exact_prefix_averages(S)
    a1 = prefix_average1(S)
    rel = max(abs((Fraction(x) - e) / e) for x, e in zip(a1, exact) if e != 0)

    # same data, but with a correctly rounded sum (math.fsum) for comparison
    fs = [math.fsum(S[: j + 1]) / (j + 1) for j in range(len(S))]
    rel_fsum = max(abs((Fraction(x) - e) / e) for x, e in zip(fs, exact) if e != 0)

    # (b) cancellation example: the "1.0" is lost when added to 1e16
    C = [1e16, 1.0, -1e16]
    return {
        "same_bits": prefix_average1(S) == prefix_average2(S),
        "max_rel_error_running": float(rel),
        "max_rel_error_fsum": float(rel_fsum),
        "cancel_data": C,
        "cancel_computed": prefix_average2(C),
        "cancel_exact": [float(x) for x in exact_prefix_averages(C)],
    }


# ----------------------------------------------------------------------------
# Part 4: benchmark
# ----------------------------------------------------------------------------
def make_input(n):
    rng = random.Random(SEED + n)
    return [rng.randint(-1000, 1000) for _ in range(n)]       # NOT timed


def measure(fn, S, work):
    """Median per-call time. For tiny inputs one call is shorter than the timer
    can resolve well, so the call is repeated `number` times inside one timing
    and the result divided by `number`. Input S already exists (not timed)."""
    number = max(1, TARGET_STEPS // max(work, 1))
    fn(S)                                      # warm-up
    times = []
    gc.disable()
    try:
        for _ in range(TRIALS):
            t0 = time.perf_counter()
            for _ in range(number):
                fn(S)
            t1 = time.perf_counter()
            times.append((t1 - t0) / number)
    finally:
        gc.enable()
    return times


COMMON_SIZES = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 4000]
LINEAR_ONLY_SIZES = [8000, 16000, 32000, 64000, 128000, 256000]


def run_benchmark():
    rows = []   # (n, algo, median, mean, stdev, min)
    med = {"avg1": {}, "avg2": {}}
    for n in COMMON_SIZES + LINEAR_ONLY_SIZES:
        S = make_input(n)
        if n in COMMON_SIZES:
            t = measure(prefix_average1, S, n * (n + 1) // 2)
            med["avg1"][n] = statistics.median(t)
            rows.append((n, "prefix_average1", statistics.median(t), statistics.mean(t),
                         statistics.stdev(t), min(t)))
        t = measure(prefix_average2, S, n)
        med["avg2"][n] = statistics.median(t)
        rows.append((n, "prefix_average2", statistics.median(t), statistics.mean(t),
                     statistics.stdev(t), min(t)))
        print(f"  n = {n:>7,}" +
              (f"   avg1 = {med['avg1'][n] * 1e6:>12.2f} µs" if n in med["avg1"] else " " * 28) +
              f"   avg2 = {med['avg2'][n] * 1e6:>10.2f} µs")
    return rows, med


def draw_plots(med, out_dir):
    ns1 = sorted(med["avg1"])
    ns2 = sorted(med["avg2"])
    t1 = [med["avg1"][n] * 1e3 for n in ns1]       # ms
    t2 = [med["avg2"][n] * 1e3 for n in ns2]

    # Figure 1: linear axes (left) and log-log with reference slopes (right)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    common = [n for n in ns2 if n in med["avg1"]]
    ax1.plot(common, [med["avg1"][n] * 1e3 for n in common], "o-", label="prefix_average1  (nested loop)")
    ax1.plot(common, [med["avg2"][n] * 1e3 for n in common], "s-", label="prefix_average2  (running sum)")
    ax1.set_xlabel("n")
    ax1.set_ylabel("time (ms)")
    ax1.set_title("Execution time vs n (linear axes)")
    ax1.grid(alpha=0.3)
    ax1.legend()

    ax2.loglog(ns1, t1, "o-", label="prefix_average1 (measured)")
    ax2.loglog(ns2, t2, "s-", label="prefix_average2 (measured)")
    n_ref = 1000
    ax2.loglog(ns1, [med["avg1"][n_ref] * 1e3 * (n / n_ref) ** 2 for n in ns1], "--", color="gray",
               label="O(n^2) reference")
    ax2.loglog(ns2, [med["avg2"][n_ref] * 1e3 * (n / n_ref) for n in ns2], ":", color="black",
               label="O(n) reference")
    ax2.set_xlabel("n (log scale)")
    ax2.set_ylabel("time (ms, log scale)")
    ax2.set_title("Log-log plot: slope 2 vs slope 1")
    ax2.grid(alpha=0.3, which="both")
    ax2.legend()
    fig.suptitle("Prefix averages: quadratic vs linear time")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "lab2_time_vs_n.png"), dpi=130)
    plt.close(fig)

    # Figure 2: normalised time (left) and speed-up ratio (right)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    ax1.semilogx(ns1, [med["avg1"][n] / (n * n) * 1e9 for n in ns1], "o-", label="T1(n) / n^2")
    ax1.semilogx(ns2, [med["avg2"][n] / n * 1e9 for n in ns2], "s-", label="T2(n) / n")
    ax1.set_ylim(bottom=0)
    ax1.set_xlabel("n (log scale)")
    ax1.set_ylabel("ns")
    ax1.set_title("Normalised time (flat = matches the bound)")
    ax1.grid(alpha=0.3)
    ax1.legend()

    ratio = [med["avg1"][n] / med["avg2"][n] for n in common]
    ax2.loglog(common, ratio, "o-", color="tab:green")
    ax2.axhline(1, color="gray", ls="--")
    ax2.set_xlabel("n (log scale)")
    ax2.set_ylabel("T1(n) / T2(n)")
    ax2.set_title("Speed-up of the running-sum method")
    ax2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "lab2_normalised_speedup.png"), dpi=130)
    plt.close(fig)


def first_n_with_ratio(med, threshold):
    for n in sorted(med["avg1"]):
        if med["avg1"][n] / med["avg2"][n] >= threshold:
            return n
    return None


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    env = {
        "Python version": sys.version.replace("\n", " "),
        "Platform": platform.platform(),
        "Timer": f"time.perf_counter (resolution {time.get_clock_info('perf_counter').resolution:.1e} s)",
        "Seed": SEED,
        "Trials": f"{TRIALS} per point (plus one warm-up); reported value = MEDIAN",
        "Input": "random integers in [-1000, 1000], generated outside the timed region",
        "Tiny inputs": f"call repeated ~{TARGET_STEPS:,}/work times inside one timing, result divided back to one call",
    }
    for k, v in env.items():
        print(f"{k:12}: {v}")

    print("\n[1] Validation")
    val = run_validation()
    for label, S, a1, a2, same, err in val:
        print(f"  {label:20} S={S}\n  {'':20} A1={a1}\n  {'':20} identical outputs: {same}, max |error| vs exact: {err:.2e}")

    print("\n[2] Operation counts (additions)")
    ops = run_operation_counts()
    for n, c1, f1, c2, f2 in ops:
        print(f"  n={n:>4}  avg1: counted={c1:>7} formula n(n+1)/2={f1:>7}   avg2: counted={c2:>4} formula n={f2:>4}")

    print("\n[3] Numerical precision")
    prec = run_precision()
    for k, v in prec.items():
        print(f"  {k}: {v}")

    print("\n[4] Benchmark")
    rows, med = run_benchmark()

    with open(os.path.join(out_dir, "lab2_timing_data.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "algorithm", "median_s", "mean_s", "stdev_s", "min_s", "trials"])
        for n, algo, m, mean, sd, mn in rows:
            w.writerow([n, algo, m, mean, sd, mn, TRIALS])

    draw_plots(med, out_dir)

    # slopes on the larger sizes (log-log fit)
    def slope(series, lo):
        ns = [n for n in sorted(series) if n >= lo]
        return statistics.linear_regression([math.log(n) for n in ns],
                                            [math.log(series[n]) for n in ns]).slope
    s1, s2 = slope(med["avg1"], 200), slope(med["avg2"], 200)
    thresholds = {t: first_n_with_ratio(med, t) for t in (1.5, 2, 10)}
    print(f"\nlog-log slope (n >= 200): prefix_average1 = {s1:.2f} (ideal 2), prefix_average2 = {s2:.2f} (ideal 1)")
    print("Smallest tested n where T1/T2 >= threshold:", thresholds)

    # ---- markdown results ------------------------------------------------------
    L = ["# Lab Work (Prefix Averages) - generated results", "", "## Environment and setup", ""]
    L += [f"- **{k}:** {v}" for k, v in env.items()]
    L += ["", "## Validation tests", "",
          "| Case | Input | Output (A) | Both methods identical? | Max abs error vs exact |",
          "|---|---|---|---|---|"]
    for label, S, a1, a2, same, err in val:
        L.append(f"| {label} | `{S}` | `{[round(x, 6) for x in a1]}` | {same} | {err:.1e} |")
    L += ["", "## Operation counts (additions)", "",
          "| n | prefix_average1 counted | n(n+1)/2 | prefix_average2 counted | n |", "|---|---|---|---|---|"]
    L += [f"| {n} | {c1} | {f1} | {c2} | {f2} |" for n, c1, f1, c2, f2 in ops]
    L += ["", "## Numerical precision", "",
          f"- Both methods add the elements in the same left-to-right order, so their outputs are bit-for-bit identical on random float data: **{prec['same_bits']}**.",
          f"- Max relative error of the running-sum averages vs exact arithmetic (2000 floats, magnitudes 1e-8..1e8): **{prec['max_rel_error_running']:.2e}**.",
          f"- Same data using `math.fsum` for every prefix: **{prec['max_rel_error_fsum']:.2e}**.",
          f"- Cancellation example `{prec['cancel_data']}`: computed `{prec['cancel_computed']}`, exact `{prec['cancel_exact']}`.",
          "", "## Timing table (median of trials)", "",
          "| n | prefix_average1 (µs) | prefix_average2 (µs) | T1 / T2 |", "|---|---|---|---|"]
    for n in COMMON_SIZES + LINEAR_ONLY_SIZES:
        a = med["avg1"].get(n)
        b = med["avg2"][n]
        L.append(f"| {n:,} | {a * 1e6:.2f} |" if a is not None else f"| {n:,} | (not run) |")
        L[-1] += f" {b * 1e6:.2f} | " + (f"{a / b:.1f} |" if a is not None else "- |")
    L += ["", f"- log-log slope for n >= 200: prefix_average1 = **{s1:.2f}** (O(n^2) -> 2), prefix_average2 = **{s2:.2f}** (O(n) -> 1)",
          f"- Smallest tested n with T1/T2 >= 1.5, 2, 10: **{thresholds[1.5]}, {thresholds[2]}, {thresholds[10]}**"]
    with open(os.path.join(out_dir, "lab2_results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    print("\nSaved: lab2_timing_data.csv, lab2_time_vs_n.png, lab2_normalised_speedup.png, lab2_results.md")


if __name__ == "__main__":
    main()
