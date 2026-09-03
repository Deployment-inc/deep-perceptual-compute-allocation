"""H3 noise-shaping control + PAM-vs-PESQ calibration probe.

At MATCHED total noise energy (noise-to-signal ratio NSR), compare noise
PLACEMENT policies:
  perceptual: noise PSD proportional to 10^(T/10) — waterfill under the
              masking-threshold curve (models threshold-shaped precision loss)
  energy:     noise PSD proportional to signal PSD — uniform SNR everywhere
              (the classic engineering heuristic)
  uniform:    equal noise PSD in every bin

For the perceptual policy we also record Delta = mean dB offset between the
injected noise PSD and the threshold curve; the NSR at which quality crosses
transparency, expressed as Delta, is a direct calibration measurement of the
PAM against PESQ's auditory model (Delta* < 0 => PAM is permissive by |Delta*| dB).

30 utterances (idx<5), NSR sweep, PESQ-WB/STOI. Output: results/h3_noise.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
import pam
from h3_proxy import stft, istft
from h3_proxy2 import eval_quality

ROOT = Path(__file__).parent.parent
NSRS_DB = [-45.0, -40.0, -35.0, -30.0, -25.0, -20.0]
SEED = 1234


def main():
    timings = json.loads((ROOT / "results" / "timings.json").read_text())
    subset = [t for t in timings if t["idx"] < 5]
    rows = []
    for n_i, t in enumerate(subset):
        audio, sr = sf.read(ROOT / t["wav"])
        res = pam.analyze(audio, sr, spl_ref=96.0, temporal=True)
        P, T = res["psd_db"], res["thr_db"]
        n_frames = P.shape[0]
        X, win = stft(audio)
        X = X[:n_frames]
        wsum2 = (np.sum(win) / 2.0) ** 2

        # power quantities in the PAM's calibrated PSD domain
        sig_pw = 10 ** (P / 10.0)
        thr_pw = 10 ** (T / 10.0)
        S_tot = sig_pw.sum()

        rng = np.random.default_rng(SEED)
        noise_unit = (rng.standard_normal(X.shape) +
                      1j * rng.standard_normal(X.shape)) / np.sqrt(2)

        for nsr_db in NSRS_DB:
            N_tot = S_tot * 10 ** (nsr_db / 10.0)
            shapes = {
                "perceptual": thr_pw,
                "energy": sig_pw,
                "uniform": np.ones_like(sig_pw),
            }
            for policy, shape in shapes.items():
                alloc = shape / shape.sum() * N_tot   # noise power, PSD domain
                # PSD domain is SPL-calibrated (full-scale sine = 96 dB):
                # convert to waveform-amplitude^2, then to FFT-bin amplitude
                a2 = alloc * 10 ** (-pam.SPL_REF / 10.0)
                amp = np.sqrt(a2 * wsum2)
                Y = X + amp * noise_unit
                deg = istft(Y, len(audio))
                q = eval_quality(audio, deg, sr)
                row = {"model": t["model"], "domain": t["domain"],
                       "idx": t["idx"], "nsr_db": nsr_db, "policy": policy, **q}
                if policy == "perceptual":
                    # dB offset of injected noise vs threshold curve (uniform
                    # in dB across cells by construction)
                    row["delta_db"] = float(10 * np.log10(N_tot / thr_pw.sum()))
                rows.append(row)
        if n_i % 10 == 0:
            print(f"...{n_i}/{len(subset)}", flush=True)

    (ROOT / "results" / "h3_noise.json").write_text(json.dumps(rows, indent=1))

    agg = defaultdict(list)
    for r in rows:
        agg[(r["model"], r["nsr_db"], r["policy"])].append(
            (r["pesq_wb"], r["stoi"], r.get("delta_db")))
    print(f"\n{'model':8s} {'NSR':>6s} {'policy':>11s} {'PESQ':>6s} {'STOI':>6s} {'Delta':>7s}")
    for (model, nsr, policy), v in sorted(agg.items()):
        p = np.mean([x[0] for x in v]); s = np.mean([x[1] for x in v])
        d = [x[2] for x in v if x[2] is not None]
        ds = f"{np.mean(d):7.1f}" if d else "      -"
        print(f"{model:8s} {nsr:6.0f} {policy:>11s} {p:6.3f} {s:6.3f} {ds}")

    from scipy.stats import wilcoxon
    per = defaultdict(dict)
    for r in rows:
        per[(r["model"], r["nsr_db"], r["idx"], r["domain"])][r["policy"]] = r["pesq_wb"]
    print("\nPaired Wilcoxon PESQ (perceptual - energy):")
    for model in ("piper", "kokoro"):
        for nsr in NSRS_DB:
            d = [v["perceptual"] - v["energy"] for k, v in per.items()
                 if k[0] == model and k[1] == nsr and "perceptual" in v and "energy" in v]
            try:
                st = wilcoxon(d)
                print(f"  {model} NSR={nsr:.0f}: {np.mean(d):+.3f} p={st.pvalue:.1e} n={len(d)}")
            except ValueError:
                print(f"  {model} NSR={nsr:.0f}: degenerate")


if __name__ == "__main__":
    main()
