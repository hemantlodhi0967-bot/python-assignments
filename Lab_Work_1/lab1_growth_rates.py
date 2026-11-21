"""
Lab Work 1: Benchmarking Algorithmic Growth Rates
Name    : Hemant Lodhi
Roll No.: 25BME024

What this script does
---------------------
Times six representative operations whose running times belong to different
growth classes, saves the timing data, draws the plots and writes a
comparison table.

    List indexing ........ O(1)
    Binary search ........ O(log n)
    Linear search ........ O(n)
    Merge sort ........... O(n log n)
    Double-loop pairs .... O(n^2)
    Subset enumeration ... O(2^n)   (small n only)

Experimental rules followed
---------------------------
* Python 3 + standard library only (matplotlib is used ONLY for plotting).
* Input generation happens OUTSIDE the timed region (see measure()).
* Every input is generated from a fixed seed, so runs are reproducible.
* Every measurement is repeated TRIALS times (after one warm-up call).
* Reported value = MEDIAN of the trials (mean/stdev/min are also saved).
* Garbage collection is switched off while timing to reduce noise.

Run:  python lab1_growth_rates.py
Output files (written next to this script):
    lab1_timing_data.csv, lab1_time_vs_n.png, lab1_normalised.png,
    lab1_results.md
"""

import csv
import gc
import itertools
import math
import os
import platform
import random
import statistics
import sys
import time

import matplotlib

matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# Experimental settings
# ----------------------------------------------------------------------------
SEED = 2024          # base seed for reproducible input generation
TRIALS = 7           # repeated timed runs for every (algorithm, n)
Q_INDEX = 50_000     # index look-ups per timed run (time reported per look-up)
Q_BINARY = 5_000     # binary searches per timed run (time reported per search)


# ----------------------------------------------------------------------------
# Algorithms under test
# ----------------------------------------------------------------------------
def run_index(a, indices):
    """O(1): many list look-ups. Time is divided by the number of look-ups."""
    for i in indices:
        a[i]


def binary_search(a, key):
    """O(log n): iterative binary search on a sorted list."""
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == key:
            return mid
        if a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def run_binary(a, keys):
    for key in keys:
        binary_search(a, key)


def linear_search(a, key):
    """O(n): scan from the left. We always search for a missing key (worst case)."""
    for i in range(len(a)):
        if a[i] == key:
            return i
    return -1


def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def merge_sort(a):
    """O(n log n): classic top-down merge sort (returns a new list)."""
    if len(a) <= 1:
        return a[:]
    mid = len(a) // 2
    return merge(merge_sort(a[:mid]), merge_sort(a[mid:]))


def count_pairs(a, target):
    """O(n^2): count pairs i < j with a[i] + a[j] == target using two loops."""
    n = len(a)
    count = 0
    for i in range(n):
        ai = a[i]
        for j in range(i + 1, n):
            if ai + a[j] == target:
                count += 1
    return count


def subset_sum_count(arr, target):
    """O(2^n): enumerate ALL subset sums and count those equal to target.
    Each element doubles the list of sums, so the total work is about 2^(n+1)."""
    sums = [0]
    for x in arr:
        sums.extend([s + x for s in sums])
    return sum(1 for s in sums if s == target)


# ----------------------------------------------------------------------------
# Input generators  (called OUTSIDE the timed region)
# Each returns (arguments_for_run_function, divisor_for_per_call_time)
# ----------------------------------------------------------------------------
def make_index(n):
    rng = random.Random(SEED + n)
    a = [rng.randrange(1_000_000) for _ in range(n)]
    indices = [rng.randrange(n) for _ in range(Q_INDEX)]
    return (a, indices), Q_INDEX


def make_binary(n):
    rng = random.Random(SEED + n)
    a = sorted(rng.sample(range(10 * n), n))          # sorted, distinct values
    keys = [rng.randrange(10 * n) for _ in range(Q_BINARY)]  # mostly absent keys
    return (a, keys), Q_BINARY


def make_linear(n):
    rng = random.Random(SEED + n)
    a = [rng.randrange(1_000_000) for _ in range(n)]
    return (a, -1), 1                                 # -1 never occurs: full scan


def make_merge(n):
    rng = random.Random(SEED + n)
    return ([rng.randrange(1_000_000) for _ in range(n)],), 1


def make_pairs(n):
    rng = random.Random(SEED + n)
    return ([rng.randrange(1_000_000) for _ in range(n)], 1_000_000), 1


def make_subset(n):
    rng = random.Random(SEED + n)
    arr = [rng.randint(1, 100) for _ in range(n)]
    return (arr, sum(arr) // 2), 1


# ----------------------------------------------------------------------------
# Correctness checks (not timed) - make sure we are timing correct algorithms
# ----------------------------------------------------------------------------
def self_check():
    rng = random.Random(1)
    # binary / linear search
    a = sorted(rng.sample(range(1000), 200))
    for key in a:
        assert a[binary_search(a, key)] == key
        assert a[linear_search(a, key)] == key
    assert binary_search(a, -5) == -1 and linear_search(a, -5) == -1
    # merge sort
    for n in (0, 1, 2, 17, 500):
        data = [rng.randrange(100) for _ in range(n)]
        assert merge_sort(data) == sorted(data)
    # pair counter vs brute force with itertools
    data = [rng.randrange(20) for _ in range(60)]
    brute = sum(1 for x, y in itertools.combinations(data, 2) if x + y == 20)
    assert count_pairs(data, 20) == brute
    # subset enumeration vs itertools
    arr = [rng.randint(1, 9) for _ in range(10)]
    tgt = sum(arr) // 2
    brute = sum(1 for r in range(len(arr) + 1)
                for c in itertools.combinations(arr, r) if sum(c) == tgt)
    assert subset_sum_count(arr, tgt) == brute
    print("Self-check passed: all algorithms give correct answers.\n")


# ----------------------------------------------------------------------------
# Timing helper
# ----------------------------------------------------------------------------
def measure(run, args, divisor):
    """Time run(*args) TRIALS times. Input already exists, so generation is NOT
    included. Returns a list of per-call times in seconds."""
    run(*args)                    # warm-up (not recorded)
    times = []
    gc.disable()
    try:
        for _ in range(TRIALS):
            t0 = time.perf_counter()
            run(*args)
            t1 = time.perf_counter()
            times.append((t1 - t0) / divisor)
    finally:
        gc.enable()
    return times


LOG2 = math.log2

EXPERIMENTS = [
    dict(key="index", name="List indexing", bound="O(1)",
         f=lambda n: 1.0, f_label="1", norm_label="T(n)",
         sizes=[2 ** k for k in range(10, 21)],
         make=make_index, run=run_index,
         timed="seconds per look-up", unit="µs per look-up", scale=1e6,
         logx=True, logy=False,
         limit="Loop overhead is much bigger than the look-up itself; cache "
               "misses on big lists can add a small upward drift."),
    dict(key="binary", name="Binary search", bound="O(log n)",
         f=lambda n: LOG2(n), f_label="log2(n)", norm_label="T(n)/log2(n)",
         sizes=[2 ** k for k in range(10, 21)],
         make=make_binary, run=run_binary,
         timed="seconds per search", unit="µs per search", scale=1e6,
         logx=True, logy=False,
         limit="Only 10-20 loop iterations per search, so call/interpreter "
               "overhead dominates; cache misses on large lists make growth "
               "look slightly faster than log n."),
    dict(key="linear", name="Linear search", bound="O(n)",
         f=lambda n: float(n), f_label="n", norm_label="T(n)/n",
         sizes=[10_000 * 2 ** k for k in range(0, 7)],
         make=make_linear, run=lambda a, k: linear_search(a, k),
         timed="seconds per search (worst case)", unit="ms per search", scale=1e3,
         logx=False, logy=False,
         limit="Worst case only (key absent); best and average cases are "
               "different. Per-element cost is large because the loop runs in "
               "the interpreter."),
    dict(key="mergesort", name="Merge sort", bound="O(n log n)",
         f=lambda n: n * LOG2(n), f_label="n log2(n)", norm_label="T(n)/(n log2 n)",
         sizes=[1_000 * 2 ** k for k in range(0, 8)],
         make=make_merge, run=lambda a: merge_sort(a),
         timed="seconds per sort", unit="ms per sort", scale=1e3,
         logx=False, logy=False,
         limit="Slicing and list allocation add constant-factor and memory "
               "overhead; over a short range of n the log n factor is hard to "
               "separate from plain n."),
    dict(key="pairs", name="Double-loop pair counter", bound="O(n^2)",
         f=lambda n: float(n * n), f_label="n^2", norm_label="T(n)/n^2",
         sizes=[200, 400, 800, 1_600, 3_200],
         make=make_pairs, run=lambda a, t: count_pairs(a, t),
         timed="seconds per run", unit="ms per run", scale=1e3,
         logx=False, logy=False,
         limit="n is capped at 3200 to keep the run short, so only five "
               "points; the inner loop overhead sets the constant."),
    dict(key="subsets", name="Subset enumeration", bound="O(2^n)",
         f=lambda n: 2.0 ** n, f_label="2^n", norm_label="T(n)/2^n",
         sizes=list(range(10, 21)),
         make=make_subset, run=lambda a, t: subset_sum_count(a, t),
         timed="seconds per run", unit="ms per run", scale=1e3,
         logx=False, logy=True,
         limit="Only small n (10-20) is feasible: memory grows as 2^n "
               "(about 1 million sums at n = 20). Allocation cost makes the "
               "ratio between steps slightly irregular."),
]


# ----------------------------------------------------------------------------
# Analysis helpers
# ----------------------------------------------------------------------------
def fit_through_origin(xs, ys):
    return sum(x * y for x, y in zip(xs, ys)) / sum(x * x for x in xs)


def trend_summary(exp, ns, ts):
    """Return (text, slope) describing the measured trend."""
    slope = statistics.linear_regression([math.log(n) for n in ns],
                                         [math.log(t) for t in ts]).slope
    fs = [exp["f"](n) for n in ns]
    if exp["key"] == "index":
        spread = max(ts) / min(ts)
        return (f"log-log slope = {slope:.2f}; max/min time over the whole range "
                f"= {spread:.2f}x (n grows {ns[-1] // ns[0]}x)"), slope
    r2 = statistics.correlation(fs, ts) ** 2
    text = f"log-log slope = {slope:.2f}; R^2 of T vs {exp['f_label']} = {r2:.4f}"
    if exp["key"] == "subsets":
        ratios = [ts[i + 1] / ts[i] for i in range(len(ts) - 1)]
        text += f"; T(n+1)/T(n) averages {statistics.mean(ratios):.2f} (ideal 2)"
    return text, slope


def environment_info():
    return {
        "Python version": sys.version.replace("\n", " "),
        "Implementation": platform.python_implementation(),
        "Platform": platform.platform(),
        "Machine / processor": f"{platform.machine()} / {platform.processor() or 'n/a'}",
        "Timer": f"time.perf_counter (resolution {time.get_clock_info('perf_counter').resolution:.1e} s)",
        "Seed": SEED,
        "Trials per point": f"{TRIALS} (plus one warm-up)",
        "Reported statistic": "MEDIAN of the trials (mean, stdev and min also saved in the CSV)",
        "GC during timing": "disabled",
    }


# ----------------------------------------------------------------------------
# Plots
# ----------------------------------------------------------------------------
def draw_plots(data, out_dir):
    # Figure 1: execution time against n, with the fitted c*f(n) curve
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, exp in zip(axes.ravel(), EXPERIMENTS):
        ns, med = data[exp["key"]]["n"], data[exp["key"]]["median"]
        ys = [t * exp["scale"] for t in med]
        ax.plot(ns, ys, "o-", label="measured (median)")
        c = fit_through_origin([exp["f"](n) for n in ns], ys)
        ax.plot(ns, [c * exp["f"](n) for n in ns], "--", label=f"c * {exp['f_label']}")
        if exp["logx"]:
            ax.set_xscale("log", base=2)
        if exp["logy"]:
            ax.set_yscale("log")
        ax.set_title(f"{exp['name']}  {exp['bound']}")
        ax.set_xlabel("n")
        ax.set_ylabel(exp["unit"])
        ax.grid(alpha=0.3)
        ax.legend()
    fig.suptitle("Lab Work 1: execution time T(n) against input size n")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "lab1_time_vs_n.png"), dpi=130)
    plt.close(fig)

    # Figure 2: normalised quantity T(n)/f(n) - should be roughly constant
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, exp in zip(axes.ravel(), EXPERIMENTS):
        ns, med = data[exp["key"]]["n"], data[exp["key"]]["median"]
        ys = [t / exp["f"](n) * exp["scale"] for n, t in zip(ns, med)]
        ax.plot(ns, ys, "s-", color="tab:red")
        ax.set_ylim(bottom=0)
        if exp["logx"]:
            ax.set_xscale("log", base=2)
        ax.set_title(f"{exp['norm_label']}  (flat line = matches {exp['bound']})")
        ax.set_xlabel("n")
        ax.set_ylabel("T(n) / f(n)  [" + exp["unit"].split(" per")[0] + "]")
        ax.grid(alpha=0.3)
    fig.suptitle("Lab Work 1: normalised timings T(n)/f(n)")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "lab1_normalised.png"), dpi=130)
    plt.close(fig)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    self_check()
    env = environment_info()
    for k, v in env.items():
        print(f"{k:20}: {v}")
    print()

    csv_rows = []
    data = {}
    summaries = {}
    for exp in EXPERIMENTS:
        ns, med = [], []
        print(f"Running {exp['name']} ({exp['bound']}) ...")
        for n in exp["sizes"]:
            args, divisor = exp["make"](n)           # NOT timed
            times = measure(exp["run"], args, divisor)  # timed only here
            m = statistics.median(times)
            ns.append(n)
            med.append(m)
            csv_rows.append([exp["name"], exp["bound"], n, m,
                             statistics.mean(times), statistics.stdev(times),
                             min(times), TRIALS, exp["timed"]])
            print(f"  n = {n:>9,}   median = {m * exp['scale']:.4f} {exp['unit']}")
        data[exp["key"]] = {"n": ns, "median": med}
        summaries[exp["key"]] = trend_summary(exp, ns, med)[0]

    with open(os.path.join(out_dir, "lab1_timing_data.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["algorithm", "theoretical_bound", "n", "median_s", "mean_s",
                    "stdev_s", "min_s", "trials", "quantity_timed"])
        w.writerows(csv_rows)

    draw_plots(data, out_dir)

    # ---- markdown results file ------------------------------------------------
    lines = ["# Lab Work 1 - generated results", "",
             "## Environment and experimental setup", ""]
    lines += [f"- **{k}:** {v}" for k, v in env.items()]
    lines += ["", "Input data: pseudo-random integers from `random.Random(SEED + n)`; "
              "data generation is outside the timed region.", "",
              "## Comparison table", "",
              "| Algorithm | Theoretical bound | Measured trend | Experimental limitations |",
              "|---|---|---|---|"]
    for exp in EXPERIMENTS:
        lines.append(f"| {exp['name']} | {exp['bound']} | {summaries[exp['key']]} | {exp['limit']} |")
    lines += ["", "## Timing data (median of trials)", ""]
    for exp in EXPERIMENTS:
        d = data[exp["key"]]
        lines += [f"### {exp['name']} - {exp['bound']}  ({exp['unit']})", "",
                  "| n | median | normalised " + exp["norm_label"] + " |", "|---|---|---|"]
        for n, t in zip(d["n"], d["median"]):
            lines.append(f"| {n:,} | {t * exp['scale']:.4f} | {t / exp['f'](n) * exp['scale']:.6f} |")
        lines.append("")
    with open(os.path.join(out_dir, "lab1_results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\nComparison of measured trends:")
    for exp in EXPERIMENTS:
        print(f"  {exp['name']:26} {exp['bound']:11} {summaries[exp['key']]}")
    print("\nSaved: lab1_timing_data.csv, lab1_time_vs_n.png, lab1_normalised.png, lab1_results.md")


if __name__ == "__main__":
    main()
