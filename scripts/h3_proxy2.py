"""H3 criterion control, v2 — coherent (criterion, operator) pairs and
bin-matched budgets.

Operators (what 'cheap compute' does to a cell):
  delete: zero the cell's bins  (proxy for: skip synthesizing this region)
  noise:  add fixed-level noise (proxy for: reduced-precision synthesis)

Policies (which cells get the cheap treatment), per operator:
  perceptual: delete -> most-maskable signal first (ascending E - T)
              noise  -> highest masking threshold first (descending T)
  energy:     delete -> quietest first (ascending E)
              noise  -> loudest first (descending E) [the naive SNR heuristic]
  random:     uniform, fixed seed

Budgets are matched on DEGRADED BIN COUNT (cells added in rank order until
cumulative bins >= B * total_bins), so all policies at a budget touch the
same amount of 'compute'.

Output: results/h3_proxy2.json + printed summary with paired Wilcoxon tests.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from scipy.stats import wilcoxon
from pesq import pesq as pesq_fn
from pystoi import stoi as stoi_fn

sys.path.insert(0, str(Path(__file__).parent))
import pam
from h3_proxy import stft, istft

ROOT = Path(__file__).parent.parent
BUDGETS = [0.1, 0.3, 0.5, 0.7]
NOISE_DBFS_PER_BIN = -55.0
SEED = 1234


def select_by_bins(order, band_bins_per_cell, target_bins):
    sel, cum = [], 0
    for c in order:
        sel.append(c)
        cum += band_bins_per_cell[c]
        if cum >= target_bins:
            break
    return np.array(sel), cum


def apply_op(X, cells, band_of_bin, op, win, rng):
    Y = X.copy()
    amp = 10 ** (NOISE_DBFS_PER_BIN / 20.0) * (np.sum(win) / 2.0)
    for (t, b) in cells:
        bins = np.where(band_of_bin == b)[0]
        if op == "delete":
            Y[t, bins] = 0.0
        else:
            noise = rng.standard_normal(len(bins)) + 1j * rng.standard_normal(len(bins))
            Y[t, bins] += amp * noise / np.sqrt(2)
    return Y


def eval_quality(ref, deg, sr):
    ref16 = resample_poly(ref, 16000, sr)
    deg16 = resample_poly(deg, 16000, sr)
    peak = max(np.abs(ref16).max(), 1e-9)
    ref16, deg16 = ref16 / peak * 0.7, deg16 / peak * 0.7
    return {
        "pesq_wb": float(pesq_fn(16000, ref16, deg16, "wb")),
        "stoi": float(stoi_fn(ref16, deg16, 16000, extended=False)),
    }


def main():
    timings = json.loads((ROOT / "results" / "timings.json").read_text())
    rng_r = np.random.default_rng(SEED)
    rows = []
    for n_i, t in enumerate(timings):
        audio, sr = sf.read(ROOT / t["wav"])
        res = pam.analyze(audio, sr, spl_ref=96.0, temporal=True)
        E, T = res["band_energy_db"], res["band_thr_db"]
        n_frames, n_bands = E.shape
        freqs = res["freqs"]
        z = pam.bark(freqs)
        band_of_bin = np.clip(z.astype(int), 0, n_bands - 1)
        bins_per_band = np.array([(band_of_bin == b).sum() for b in range(n_bands)])
        bins_per_cell = np.tile(bins_per_band, n_frames)  # cell id = t*n_bands+b
        total_bins = n_frames * len(freqs)

        X, win = stft(audio)
        X = X[:n_frames]

        orders = {
            "delete": {
                "perceptual": np.argsort((E - T).flatten(), kind="stable"),
                "energy": np.argsort(E.flatten(), kind="stable"),
                "random": rng_r.permutation(n_frames * n_bands),
            },
            "noise": {
                "perceptual": np.argsort(-T.flatten(), kind="stable"),
                "energy": np.argsort(-E.flatten(), kind="stable"),
                "random": rng_r.permutation(n_frames * n_bands),
            },
        }
        for op in ("delete", "noise"):
            for budget in BUDGETS:
                target = budget * total_bins
                for policy, order in orders[op].items():
                    sel, cum = select_by_bins(order, bins_per_cell, target)
                    cells = [(int(c // n_bands), int(c % n_bands)) for c in sel]
                    Y = apply_op(X, cells, band_of_bin, op, win,
                                 np.random.default_rng(SEED + 1))
                    deg = istft(Y, len(audio))
                    q = eval_quality(audio, deg, sr)
                    rows.append({"model": t["model"], "domain": t["domain"],
                                 "idx": t["idx"], "op": op, "budget": budget,
                                 "policy": policy, "bins": int(cum), **q})
        if n_i % 10 == 0:
            print(f"...{n_i}/{len(timings)}", flush=True)

    (ROOT / "results" / "h3_proxy2.json").write_text(json.dumps(rows, indent=1))

    agg = defaultdict(list)
    for r in rows:
        agg[(r["op"], r["model"], r["budget"], r["policy"])].append(
            (r["pesq_wb"], r["stoi"]))
    print(f"\n{'op':7s} {'model':8s} {'B':>4s} {'policy':>10s} {'PESQ':>6s} {'STOI':>6s}")
    for (op, model, budget, policy), v in sorted(agg.items()):
        p = np.mean([x[0] for x in v]); s = np.mean([x[1] for x in v])
        print(f"{op:7s} {model:8s} {budget:4.1f} {policy:>10s} {p:6.3f} {s:6.3f}")

    print("\nPaired Wilcoxon PESQ (perceptual - energy):")
    per = defaultdict(dict)
    for r in rows:
        per[(r["op"], r["model"], r["budget"], r["idx"], r["domain"])][r["policy"]] = r["pesq_wb"]
    for op in ("delete", "noise"):
        for model in ("piper", "kokoro"):
            for budget in BUDGETS:
                d = [v["perceptual"] - v["energy"] for k, v in per.items()
                     if k[0] == op and k[1] == model and k[2] == budget]
                try:
                    st = wilcoxon(d)
                    print(f"  {op:6s} {model:7s} B={budget}: {np.mean(d):+.3f} "
                          f"p={st.pvalue:.1e} n={len(d)}")
                except ValueError:
                    print(f"  {op:6s} {model:7s} B={budget}: degenerate")


if __name__ == "__main__":
    main()
