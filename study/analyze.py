"""Analysis for the Sotto ABX listening study.

Usage:
  python analyze.py responses/            # directory of *.json (one per participant)
  python analyze.py responses.jsonl       # or one JSON object per line
  python analyze.py codes.txt             # or one pasted base64 results-code per line

Pre-registered rules (see PROTOCOL.md):
  - Screening: include a participant only if anchor accuracy >= 5/6 (0.83)
    and median test-trial RT >= 1.5 s (rules out click-through).
  - Transparency verdict per condition: detection accuracy not significantly
    above chance (one-sided binomial p >= 0.05) AND Wilson 95% CI upper bound
    <= 0.60. Report d' as a secondary statistic.
"""

import base64, json, sys
from collections import defaultdict
from math import sqrt
from pathlib import Path

from scipy.stats import binomtest, norm


def load(path):
    p = Path(path)
    out = []
    if p.is_dir():
        for f in sorted(p.glob("*.json")):
            out.append(json.loads(f.read_text()))
    else:
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("{"):
                out.append(json.loads(line))
            else:
                out.append(json.loads(base64.b64decode(line).decode("utf-8")))
    return out


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, c - h, c + h)


def dprime(hits, fas, n_h, n_f):
    # ABX: treat "X=A correct when xIsRef" loosely; report simple d' from accuracy
    # d' = sqrt(2) * z(accuracy) for 2AFC-equivalent
    return None


def main():
    parts = load(sys.argv[1])
    print(f"participants loaded: {len(parts)}")
    included, excluded = [], []
    for p in parts:
        test = [t for t in p["trials"] if t["kind"] == "test"]
        anch = [t for t in p["trials"] if t["kind"] == "anchor"]
        acc_a = sum(t["correct"] for t in anch) / max(len(anch), 1)
        rts = sorted(t["rt_ms"] for t in test)
        med_rt = rts[len(rts) // 2] / 1000 if rts else 0
        ok = acc_a >= 0.83 and med_rt >= 1.5
        (included if ok else excluded).append((p, acc_a, med_rt))
    print(f"included: {len(included)}  excluded: {len(excluded)}")
    for p, a, r in excluded:
        print(f"  excluded {p['pid']}: anchor acc {a:.2f}, median RT {r:.1f}s")

    by_cond = defaultdict(lambda: [0, 0])
    by_cond_model = defaultdict(lambda: [0, 0])
    for p, _, _ in included:
        for t in p["trials"]:
            if t["kind"] == "practice":
                continue
            by_cond[t["cond"]][0] += int(t["correct"]); by_cond[t["cond"]][1] += 1
            model = t["utt"].split("_")[0]
            by_cond_model[(t["cond"], model)][0] += int(t["correct"]); by_cond_model[(t["cond"], model)][1] += 1

    print("\n| condition | n | accuracy | 95% CI | p (>chance) | d' | verdict |")
    print("|---|---|---|---|---|---|---|")
    order = ["e30", "e50", "e60", "e75", "e90", "anchor"]
    for c in order:
        if c not in by_cond:
            continue
        k, n = by_cond[c]
        p_, lo, hi = wilson(k, n)
        pval = binomtest(k, n, 0.5, alternative="greater").pvalue
        acc = min(max(p_, 0.5 + 1e-6), 1 - 1e-6)
        dp = sqrt(2) * norm.ppf(acc)
        if c == "anchor":
            verdict = "control (should be detected)"
        else:
            verdict = "TRANSPARENT" if (pval >= 0.05 and hi <= 0.60) else ("detectable" if pval < 0.05 else "inconclusive")
        print(f"| {c} | {n} | {p_:.3f} | [{lo:.3f}, {hi:.3f}] | {pval:.3g} | {dp:.2f} | {verdict} |")

    print("\nPer model:")
    for (c, m), (k, n) in sorted(by_cond_model.items()):
        p_, lo, hi = wilson(k, n)
        print(f"  {c:7s} {m:7s} n={n:3d} acc={p_:.3f} CI=[{lo:.2f},{hi:.2f}]")


if __name__ == "__main__":
    main()
