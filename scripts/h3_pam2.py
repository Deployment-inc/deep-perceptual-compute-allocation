"""Re-run of the H3 deletion control and the H1 existence measurement with the
vetted+calibrated model: pam2 (Schuller spreading-matrix PAM) with a global
calibration offset DELTA_CAL determined by the PESQ Δ-probe (capped variant):
noise at min(threshold, signal) * 10^(Δ/20) reaches PESQ >= ~4.35 at Δ = -16 dB.

H1 (calibrated): per-bin below-threshold fraction (mX < thr*10^(DELTA/20)),
frames fully / >=95% maskable.

H3 deletion: bark-band cells (nfilts=64), bin-matched budgets, policies:
  perceptual_excl: rank by band energy (dB) - exclusive calibrated threshold (dB)
  energy:          rank by band energy
  random:          fixed-seed shuffle
48 utterances (idx<8), budgets 0.1/0.3/0.5. Output: results/h3_pam2.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.stats import wilcoxon

sys.path.insert(0, str(Path(__file__).parent))
from pam2 import Pam2, INT16, FRAME
from h3_proxy import stft, istft
from h3_proxy2 import select_by_bins, eval_quality

ROOT = Path(__file__).parent.parent
DELTA_CAL = -16.0
BUDGETS = [0.1, 0.3, 0.5]
SEED = 1234
EPS = 1e-12


def main():
    timings = json.loads((ROOT / "results" / "timings.json").read_text())
    subset = [t for t in timings if t["idx"] < 8]
    rng_r = np.random.default_rng(SEED)
    pams = {}
    rows, h1_rows = [], []
    for n_i, t in enumerate(subset):
        audio, sr = sf.read(ROOT / t["wav"])
        if sr not in pams:
            pams[sr] = Pam2(sr)
        pm = pams[sr]
        p = pm.analyze(audio)
        n_frames, K = p["n_frames"], p["K"]
        if n_frames == 0:
            continue
        cal = 10 ** (DELTA_CAL / 20.0)

        # ---- H1 with calibrated thresholds ----
        below = p["mX"] < p["thr_mag"] * cal
        fb = below.mean(axis=1)
        h1_rows.append({"model": t["model"], "domain": t["domain"],
                        "idx": t["idx"], "bin_below": float(below.mean()),
                        "frame_full": float((fb >= 0.999).mean()),
                        "frame_95": float((fb >= 0.95).mean())})

        # ---- H3 deletion with exclusive calibrated thresholds ----
        E_bark_db = 20 * np.log10(p["mXbark"] + EPS)
        Tx = pm.bark_exclusive_threshold(p["mXbark"]) * cal
        Tx_db = 20 * np.log10(Tx + EPS)
        B = E_bark_db.shape[1]
        # bin membership of each bark band from the mapping matrix
        Wbins = pm.W[:, :K - 1] > 0  # [B, K-1]
        bins_per_band = Wbins.sum(axis=1)
        bins_per_cell = np.tile(bins_per_band, n_frames)
        total_bins = n_frames * K
        X, win = stft(audio)
        X = X[:n_frames]

        orders = {
            "perceptual_excl": np.argsort((E_bark_db - Tx_db).flatten(), kind="stable"),
            "energy": np.argsort(E_bark_db.flatten(), kind="stable"),
            "random": rng_r.permutation(n_frames * B),
        }
        for budget in BUDGETS:
            target = budget * total_bins
            for policy, order in orders.items():
                sel, cum = select_by_bins(order, bins_per_cell, target)
                Y = X.copy()
                for c in sel:
                    fr, b = int(c // B), int(c % B)
                    Y[fr, :K - 1][Wbins[b]] = 0.0
                deg = istft(Y, len(audio))
                q = eval_quality(audio, deg, sr)
                rows.append({"model": t["model"], "domain": t["domain"],
                             "idx": t["idx"], "budget": budget,
                             "policy": policy, "bins": int(cum), **q})
        if n_i % 8 == 0:
            print(f"...{n_i}/{len(subset)}", flush=True)

    (ROOT / "results" / "h3_pam2.json").write_text(
        json.dumps({"h3": rows, "h1": h1_rows, "delta_cal_db": DELTA_CAL}, indent=1))

    print(f"\nH1 (pam2, calibrated {DELTA_CAL:+.0f} dB):")
    agg1 = defaultdict(list)
    for r in h1_rows:
        agg1[(r["model"], r["domain"])].append((r["bin_below"], r["frame_full"], r["frame_95"]))
    print(f"{'model':8s} {'domain':10s} {'bin<thr':>8s} {'fr100%':>7s} {'fr95%':>7s}")
    for (model, domain), v in sorted(agg1.items()):
        print(f"{model:8s} {domain:10s} {np.mean([x[0] for x in v]):8.3f} "
              f"{np.mean([x[1] for x in v]):7.3f} {np.mean([x[2] for x in v]):7.3f}")

    print("\nH3 deletion (pam2 exclusive calibrated):")
    agg = defaultdict(list)
    for r in rows:
        agg[(r["model"], r["budget"], r["policy"])].append(r["pesq_wb"])
    print(f"{'model':8s} {'B':>4s} {'policy':>16s} {'PESQ':>6s}")
    for (model, budget, policy), v in sorted(agg.items()):
        print(f"{model:8s} {budget:4.1f} {policy:>16s} {np.mean(v):6.3f}")

    per = defaultdict(dict)
    for r in rows:
        per[(r["model"], r["budget"], r["idx"], r["domain"])][r["policy"]] = r["pesq_wb"]
    print("\nWilcoxon PESQ (perceptual_excl - energy):")
    for model in ("piper", "kokoro"):
        for budget in BUDGETS:
            d = [v["perceptual_excl"] - v["energy"] for k, v in per.items()
                 if k[0] == model and k[1] == budget]
            try:
                st = wilcoxon(d)
                print(f"  {model} B={budget}: {np.mean(d):+.3f} p={st.pvalue:.1e} n={len(d)}")
            except ValueError:
                print(f"  {model} B={budget}: degenerate")


if __name__ == "__main__":
    main()
