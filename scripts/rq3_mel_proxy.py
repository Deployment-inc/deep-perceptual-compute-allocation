"""RQ3: how well can masking thresholds be estimated from a mel-resolution
spectral representation (proxy for pre-waveform features), vs ground truth
computed on the produced audio?

Method: PSD -> 80-band mel energies -> pseudo-inverse back to linear PSD
(spectrally smoothed, as a mel-conditioned predictor would see) -> run the
same PAM threshold machinery -> compare per-(frame, Bark-band) decisions.

Key safety number: FALSE-MASKABLE rate — cells the estimate calls maskable
but ground truth calls audible (degrading them would be audible).

Output: results/rq3_mel_proxy.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import pam

ROOT = Path(__file__).parent.parent
N_MELS = 80
EPS = 1e-12


def hz_to_mel(f):
    return 2595.0 * np.log10(1.0 + f / 700.0)


def mel_to_hz(m):
    return 700.0 * (10 ** (m / 2595.0) - 1.0)


def mel_filterbank(sr, n_fft, n_mels):
    freqs = np.fft.rfftfreq(n_fft, 1.0 / sr)
    mel_pts = np.linspace(hz_to_mel(0), hz_to_mel(sr / 2), n_mels + 2)
    hz_pts = mel_to_hz(mel_pts)
    fb = np.zeros((n_mels, len(freqs)))
    for i in range(n_mels):
        lo, c, hi = hz_pts[i], hz_pts[i + 1], hz_pts[i + 2]
        left = (freqs - lo) / max(c - lo, 1e-9)
        right = (hi - freqs) / max(hi - c, 1e-9)
        fb[i] = np.clip(np.minimum(left, right), 0, None)
    return fb, freqs


def main():
    timings = json.loads((ROOT / "results" / "timings.json").read_text())
    # subset: 5 per domain per model = 30 utterances
    subset = [t for t in timings if t["idx"] < 5]
    agg = defaultdict(lambda: {"rmse": [], "false_mask": [], "false_aud": [],
                               "agree": []})
    for n_i, t in enumerate(subset):
        audio, sr = sf.read(ROOT / t["wav"])
        res = pam.analyze(audio, sr, spl_ref=96.0, temporal=True)
        P_true, T_true = res["psd_db"], res["thr_db"]
        freqs = res["freqs"]
        z = pam.bark(freqs)
        n_bands = int(np.ceil(z.max()))
        band_of_bin = np.clip(z.astype(int), 0, n_bands - 1)
        ath = pam.ath_db(freqs)

        fb, _ = mel_filterbank(sr, pam.FRAME, N_MELS)
        fb_norm = fb / (fb.sum(axis=1, keepdims=True) + EPS)
        # smooth PSD through mel and back (uniform spread within each filter)
        pw = 10 ** (P_true / 10.0)
        mel_e = pw @ fb_norm.T                     # [T, M] mean power per mel
        # distribute back: each bin gets weighted mean of its mel bands
        w = fb / (fb.sum(axis=0, keepdims=True) + EPS)   # [M, K] col-normalized
        pw_est = mel_e @ w                          # [T, K]
        P_est = 10 * np.log10(pw_est + EPS)

        T_est = np.zeros_like(P_est)
        for fr in range(P_est.shape[0]):
            T_est[fr] = pam.global_threshold(P_est[fr], z, ath)
        T_est = pam.add_forward_masking(T_est, hop_ms=1000.0 * pam.HOP / sr)

        # band-level decisions against TRUE band energy
        def bandify(M, reduce):
            out = np.zeros((M.shape[0], n_bands))
            for b in range(n_bands):
                selb = band_of_bin == b
                out[:, b] = reduce(M[:, selb])
            return out

        E_band = bandify(10 ** (P_true / 10.0), lambda x: 10 * np.log10(x.sum(axis=1) + EPS))
        Tt_band = bandify(T_true, lambda x: x.min(axis=1))
        Te_band = bandify(T_est, lambda x: x.min(axis=1))

        mask_true = E_band < Tt_band
        mask_est = E_band < Te_band
        n_cells = mask_true.size
        false_mask = (mask_est & ~mask_true).sum() / max((mask_est).sum(), 1)
        false_aud = (~mask_est & mask_true).sum() / max(mask_true.sum(), 1)
        agree = (mask_est == mask_true).mean()
        rmse = float(np.sqrt(np.mean((Te_band - Tt_band) ** 2)))
        agg[t["model"]]["rmse"].append(rmse)
        agg[t["model"]]["false_mask"].append(float(false_mask))
        agg[t["model"]]["false_aud"].append(float(false_aud))
        agg[t["model"]]["agree"].append(float(agree))
        if n_i % 10 == 0:
            print(f"...{n_i}/{len(subset)}", flush=True)

    out = {}
    print(f"\n{'model':8s} {'thrRMSE(dB)':>11s} {'agree':>7s} "
          f"{'falseMaskable':>13s} {'falseAudible':>12s}")
    for model, a in sorted(agg.items()):
        row = {k: float(np.mean(v)) for k, v in a.items()}
        out[model] = row
        print(f"{model:8s} {row['rmse']:11.2f} {row['agree']:7.3f} "
              f"{row['false_mask']:13.3f} {row['false_aud']:12.3f}")
    (ROOT / "results" / "rq3_mel_proxy.json").write_text(json.dumps(out, indent=1))
    print("wrote results/rq3_mel_proxy.json")


if __name__ == "__main__":
    main()
