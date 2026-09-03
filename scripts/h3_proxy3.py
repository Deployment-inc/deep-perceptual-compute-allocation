"""H3 criterion control, v3 — deletion operator with EXCLUSIVE (leave-self-out)
perceptual thresholds, vs the v2 inclusive policy, energy, and random.

Policy 'perceptual_excl' additionally caps deletion at its safe pool: it only
deletes cells with E < T_excl; if the budget exceeds the pool, remaining
budget goes to the next-least-audible cells (ranked by E - T_excl) and the
overflow fraction is recorded.

Output: results/h3_proxy3.json + printed summary.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).parent))
import pam
from h3_proxy import stft, istft
from h3_proxy2 import select_by_bins, eval_quality

ROOT = Path(__file__).parent.parent
BUDGETS = [0.1, 0.3, 0.5]
SEED = 1234


def main():
    timings = json.loads((ROOT / "results" / "timings.json").read_text())
    rng_r = np.random.default_rng(SEED)
    rows = []
    for n_i, t in enumerate(timings):
        audio, sr = sf.read(ROOT / t["wav"])
        res = pam.analyze(audio, sr, spl_ref=96.0, temporal=True)
        E, T_incl = res["band_energy_db"], res["band_thr_db"]
        rex = pam.analyze_band_exclusive(audio, sr, spl_ref=96.0, temporal=True)
        T_excl = rex["band_thr_excl_db"]
        assert rex["band_energy_db"].shape == E.shape
        n_frames, n_bands = E.shape
        freqs = res["freqs"]
        z = pam.bark(freqs)
        band_of_bin = np.clip(z.astype(int), 0, n_bands - 1)
        bins_per_band = np.array([(band_of_bin == b).sum() for b in range(n_bands)])
        bins_per_cell = np.tile(bins_per_band, n_frames)
        total_bins = n_frames * len(freqs)

        X, win = stft(audio)
        X = X[:n_frames]

        safe_pool_frac = float((E < T_excl).mean())
        orders = {
            "perceptual_excl": np.argsort((E - T_excl).flatten(), kind="stable"),
            "perceptual_incl": np.argsort((E - T_incl).flatten(), kind="stable"),
            "energy": np.argsort(E.flatten(), kind="stable"),
            "random": rng_r.permutation(n_frames * n_bands),
        }
        for budget in BUDGETS:
            target = budget * total_bins
            for policy, order in orders.items():
                sel, cum = select_by_bins(order, bins_per_cell, target)
                cells = [(int(c // n_bands), int(c % n_bands)) for c in sel]
                Y = X.copy()
                for (fr, b) in cells:
                    Y[fr, np.where(band_of_bin == b)[0]] = 0.0
                deg = istft(Y, len(audio))
                q = eval_quality(audio, deg, sr)
                # overflow: how many deleted cells were NOT safe under T_excl
                overflow = float(np.mean([(E[fr, b] >= T_excl[fr, b])
                                          for fr, b in cells]))
                rows.append({"model": t["model"], "domain": t["domain"],
                             "idx": t["idx"], "budget": budget,
                             "policy": policy, "bins": int(cum),
                             "overflow_frac": overflow,
                             "safe_pool_frac": safe_pool_frac, **q})
        if n_i % 10 == 0:
            print(f"...{n_i}/{len(timings)}", flush=True)

    (ROOT / "results" / "h3_proxy3.json").write_text(json.dumps(rows, indent=1))

    agg = defaultdict(list)
    for r in rows:
        agg[(r["model"], r["budget"], r["policy"])].append(
            (r["pesq_wb"], r["stoi"], r["overflow_frac"]))
    print(f"\n{'model':8s} {'B':>4s} {'policy':>16s} {'PESQ':>6s} {'STOI':>6s} {'overflow':>8s}")
    for (model, budget, policy), v in sorted(agg.items()):
        p = np.mean([x[0] for x in v]); s = np.mean([x[1] for x in v])
        o = np.mean([x[2] for x in v])
        print(f"{model:8s} {budget:4.1f} {policy:>16s} {p:6.3f} {s:6.3f} {o:8.2f}")

    print("\nPaired Wilcoxon PESQ (perceptual_excl - energy):")
    per = defaultdict(dict)
    for r in rows:
        per[(r["model"], r["budget"], r["idx"], r["domain"])][r["policy"]] = r["pesq_wb"]
    for model in ("piper", "kokoro"):
        for budget in BUDGETS:
            d = [v["perceptual_excl"] - v["energy"] for k, v in per.items()
                 if k[0] == model and k[1] == budget]
            try:
                st = wilcoxon(d)
                print(f"  {model} B={budget}: {np.mean(d):+.3f} p={st.pvalue:.1e} n={len(d)}")
            except ValueError:
                print(f"  {model} B={budget}: degenerate")
    print("\nMean safe pool (E < T_excl):",
          {m: round(float(np.mean([r['safe_pool_frac'] for r in rows if r['model'] == m])), 3)
           for m in ('piper', 'kokoro')})


if __name__ == "__main__":
    main()
