"""H1 existence measurement: below-masking-threshold fractions per model x domain.

For every corpus WAV: run the PAM, compute per-(frame, Bark-band) energy and
conservative masking threshold, then:
  - cell_below_frac (uniform-Bark and linear-frequency weightings): theoretical
    time-frequency harvest ceiling
  - frame_fully_maskable_frac: harvestable by pure per-frame temporal gating
  - headroom distribution
Combine with RQ2 decoder share for compute-weighted H1 numbers.

Outputs results/h1_summary.json, figures/money_figure.png, figures/headroom_hist.png
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

DECODER_SHARE = {"piper": 0.695, "kokoro": 0.956}  # from results/stage_profile.json


def main():
    timings = json.loads((ROOT / "results" / "timings.json").read_text())
    per_utt = []
    agg = defaultdict(lambda: {"cells_below_u": [], "cells_below_l": [],
                               "frames_full": [], "headrooms": []})
    money = None
    for t in timings:
        audio, sr = sf.read(ROOT / t["wav"])
        res = pam.analyze(audio, sr)
        m = pam.h1_metrics(res)
        if m is None:
            continue
        key = (t["model"], t["domain"])
        agg[key]["cells_below_u"].append(m["cell_below_frac_uniform_bark"])
        agg[key]["cells_below_l"].append(m["cell_below_frac_linear_freq"])
        agg[key]["frames_full"].append(m["frame_fully_maskable_frac"])
        agg[key]["headrooms"].append(m["headroom_db"].flatten())
        per_utt.append({
            "model": t["model"], "domain": t["domain"], "idx": t["idx"],
            "cell_below_uniform_bark": m["cell_below_frac_uniform_bark"],
            "cell_below_linear_freq": m["cell_below_frac_linear_freq"],
            "frame_fully_maskable": m["frame_fully_maskable_frac"],
            "n_frames": m["n_frames"],
        })
        if t["model"] == "piper" and t["domain"] == "agent" and t["idx"] == 0:
            money = (res, t)

    summary = {}
    print(f"\n{'model':8s} {'domain':10s} {'cell<thr(bark)':>14s} "
          f"{'cell<thr(linfreq)':>17s} {'frames all<thr':>14s} "
          f"{'H1 ceiling':>10s} {'H1 temporal':>11s}")
    for (model, domain), a in sorted(agg.items()):
        cu = float(np.mean(a["cells_below_u"]))
        cl = float(np.mean(a["cells_below_l"]))
        ff = float(np.mean(a["frames_full"]))
        share = DECODER_SHARE[model]
        h1_ceiling = share * cl
        h1_temporal = share * ff
        summary[f"{model}/{domain}"] = {
            "cell_below_uniform_bark_mean": cu,
            "cell_below_linear_freq_mean": cl,
            "frame_fully_maskable_mean": ff,
            "decoder_share": share,
            "h1_compute_ceiling_linfreq": h1_ceiling,
            "h1_compute_temporal_only": h1_temporal,
            "n_utts": len(a["cells_below_u"]),
        }
        print(f"{model:8s} {domain:10s} {cu:14.3f} {cl:17.3f} {ff:14.3f} "
              f"{h1_ceiling:10.3f} {h1_temporal:11.3f}")

    (ROOT / "results" / "h1_summary.json").write_text(
        json.dumps({"summary": summary, "per_utterance": per_utt,
                    "decoder_share_source": "results/stage_profile.json",
                    "notes": "conservative thresholds (min over bins per band); "
                             "ceiling = decoder_share * cell_below_linear_freq; "
                             "temporal = decoder_share * frame_fully_maskable"},
                   indent=1))

    # ---- figures ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if money is not None:
        res, t = money
        E, T = res["band_energy_db"], res["band_thr_db"]
        head = E - T  # positive = audible
        below = (E < T)
        times = np.arange(E.shape[0]) * res["hop"] / res["sr"]
        fig, axes = plt.subplots(4, 1, figsize=(11, 11), sharex=True)
        ex = [0, times[-1], 0, E.shape[1]]
        im0 = axes[0].imshow(E.T, origin="lower", aspect="auto", extent=ex,
                             vmin=-20, vmax=90, cmap="magma")
        axes[0].set_title(f'Signal energy per Bark band (dB SPL) — "{t["text"]}" [{t["model"]}]')
        im1 = axes[1].imshow(T.T, origin="lower", aspect="auto", extent=ex,
                             vmin=-20, vmax=90, cmap="magma")
        axes[1].set_title("Masking threshold (dB SPL, conservative min-over-bins)")
        im2 = axes[2].imshow(head.T, origin="lower", aspect="auto", extent=ex,
                             vmin=-40, vmax=40, cmap="RdBu_r")
        axes[2].set_title("Headroom: energy − threshold (red = audible, blue = maskable)")
        im3 = axes[3].imshow(below.T, origin="lower", aspect="auto", extent=ex,
                             cmap="Greys", vmin=0, vmax=1)
        axes[3].set_title("Below-threshold cells (black = compute here is perceptually wasted)")
        axes[3].set_xlabel("time (s)")
        for ax in axes:
            ax.set_ylabel("Bark band")
        for im, ax in zip([im0, im1, im2, im3], axes):
            fig.colorbar(im, ax=ax, pad=0.01)
        fig.tight_layout()
        fig.savefig(ROOT / "figures" / "money_figure.png", dpi=140)
        print("wrote figures/money_figure.png")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for ax, model in zip(axes, ["piper", "kokoro"]):
        for domain in ["agent", "narration", "hinglish"]:
            hs = np.concatenate(agg[(model, domain)]["headrooms"])
            hs = np.clip(hs, -60, 60)
            xs = np.linspace(-60, 60, 121)
            frac = [(hs >= x).mean() for x in xs]
            ax.plot(xs, frac, label=domain)
        ax.axvline(0, color="k", lw=0.8, ls="--")
        ax.set_title(f"{model}: fraction of cells with headroom ≥ x dB")
        ax.set_xlabel("headroom (threshold − energy, dB)")
        ax.set_ylabel("fraction of (frame, band) cells")
        ax.legend()
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(ROOT / "figures" / "headroom_curve.png", dpi=140)
    print("wrote figures/headroom_curve.png")


if __name__ == "__main__":
    main()
