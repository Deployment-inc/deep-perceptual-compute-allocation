"""H3 criterion control (oracle degradation proxy).

Question: at MATCHED budgets (same number of degraded time-frequency cells,
same injected noise level), does perceptually-guided placement beat
energy-guided and random placement on quality?

Design:
  - STFT grid identical to the PAM's (1024/512 hann, WOLA resynthesis).
  - Degradation model: additive complex Gaussian noise at a FIXED per-bin
    PSD (quantization-noise-like: level independent of local signal), injected
    only into selected (frame, Bark-band) cells.
  - Policies rank cells and degrade the top-B fraction:
      perceptual: most-maskable first (ascending signal-minus-threshold)
      energy:     lowest band energy first
      random:     uniform (fixed seed)
  - Quality vs the undegraded synthesis (the true same-seed reference):
    PESQ-WB and STOI at 16 kHz.

Matched-budget note: cells are equal-size in Bark bands but not in bins;
we match the number of CELLS per policy AND report mean degraded-bin count
per policy so budget parity can be audited both ways.

Output: results/h3_proxy.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from pesq import pesq as pesq_fn
from pystoi import stoi as stoi_fn

sys.path.insert(0, str(Path(__file__).parent))
import pam

ROOT = Path(__file__).parent.parent
BUDGETS = [0.1, 0.3, 0.5, 0.7]
NOISE_DBFS_PER_BIN = -50.0   # fixed per-bin noise PSD (re full scale = 1.0)
SEED = 1234


def stft(audio, n=pam.FRAME, hop=pam.HOP):
    win = np.hanning(n)
    n_frames = max(0, 1 + (len(audio) - n) // hop)
    X = np.zeros((n_frames, n // 2 + 1), dtype=complex)
    for t in range(n_frames):
        X[t] = np.fft.rfft(audio[t * hop: t * hop + n] * win)
    return X, win


def istft(X, length, n=pam.FRAME, hop=pam.HOP):
    win = np.hanning(n)
    out = np.zeros(length)
    norm = np.zeros(length)
    for t in range(X.shape[0]):
        s = t * hop
        out[s:s + n] += np.fft.irfft(X[t], n=n) * win
        norm[s:s + n] += win ** 2
    norm[norm < 1e-8] = 1.0
    return out / norm


def degrade(audio, sr, cells, band_of_bin, rng):
    """Add fixed-level complex Gaussian noise into the given (frame, band) cells."""
    X, win = stft(audio)
    # per-bin noise amplitude so that its PSD (dB re full-scale sine) matches
    # NOISE_DBFS_PER_BIN under the same windowed-FFT convention as the PAM
    amp = 10 ** (NOISE_DBFS_PER_BIN / 20.0) * (np.sum(win) / 2.0)
    for (t, b) in cells:
        bins = np.where(band_of_bin == b)[0]
        noise = rng.standard_normal(len(bins)) + 1j * rng.standard_normal(len(bins))
        X[t, bins] += amp * noise / np.sqrt(2)
    return istft(X, len(audio))


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
    rng = np.random.default_rng(SEED)
    rows = []
    for n_i, t in enumerate(timings):
        audio, sr = sf.read(ROOT / t["wav"])
        res = pam.analyze(audio, sr, spl_ref=96.0, temporal=True)
        E, T = res["band_energy_db"], res["band_thr_db"]
        n_frames, n_bands = E.shape
        freqs = res["freqs"]
        z = pam.bark(freqs)
        band_of_bin = np.clip(z.astype(int), 0, n_bands - 1)

        margin = (E - T).flatten()          # ascending = most maskable first
        energy = E.flatten()                # ascending = quietest first
        n_cells = margin.size
        order_p = np.argsort(margin, kind="stable")
        order_e = np.argsort(energy, kind="stable")
        order_r = rng.permutation(n_cells)

        for budget in BUDGETS:
            k = int(round(budget * n_cells))
            for policy, order in (("perceptual", order_p), ("energy", order_e),
                                  ("random", order_r)):
                sel = order[:k]
                cells = [(int(c // n_bands), int(c % n_bands)) for c in sel]
                nbins = int(sum((band_of_bin == b).sum() for _, b in cells))
                deg = degrade(audio, sr, cells, band_of_bin,
                              np.random.default_rng(SEED + 1))
                q = eval_quality(audio, deg, sr)
                rows.append({"model": t["model"], "domain": t["domain"],
                             "idx": t["idx"], "budget": budget,
                             "policy": policy, "degraded_bins": nbins, **q})
        if n_i % 10 == 0:
            print(f"...{n_i}/{len(timings)}", flush=True)

    (ROOT / "results" / "h3_proxy.json").write_text(json.dumps(rows, indent=1))

    # summary + paired tests
    from scipy.stats import wilcoxon
    agg = defaultdict(list)
    for r in rows:
        agg[(r["model"], r["budget"], r["policy"])].append(
            (r["pesq_wb"], r["stoi"], r["degraded_bins"]))
    print(f"\n{'model':8s} {'budget':>6s} {'policy':>10s} {'PESQ':>6s} "
          f"{'STOI':>6s} {'bins':>8s}")
    for (model, budget, policy), v in sorted(agg.items()):
        p = np.mean([x[0] for x in v]); s = np.mean([x[1] for x in v])
        nb = np.mean([x[2] for x in v])
        print(f"{model:8s} {budget:6.1f} {policy:>10s} {p:6.3f} {s:6.3f} {nb:8.0f}")

    print("\nPaired Wilcoxon (perceptual vs energy PESQ), per model x budget:")
    per = defaultdict(dict)
    for r in rows:
        per[(r["model"], r["budget"], r["idx"], r["domain"])][r["policy"]] = r["pesq_wb"]
    for model in ("piper", "kokoro"):
        for budget in BUDGETS:
            pairs = [(v["perceptual"], v["energy"])
                     for k, v in per.items() if k[0] == model and k[1] == budget]
            d = [a - b for a, b in pairs]
            try:
                stat = wilcoxon(d)
                print(f"  {model} B={budget}: mean diff {np.mean(d):+.3f}, "
                      f"p={stat.pvalue:.2e}, n={len(d)}")
            except ValueError:
                print(f"  {model} B={budget}: degenerate (all zero diffs)")


if __name__ == "__main__":
    main()
