"""H1 v2: per-bin below-threshold fractions with temporal masking and a
playback-calibration sensitivity sweep (full-scale = 96 / 80 / 70 dB SPL).

Outputs results/h1_v2.json and prints the summary tables.
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
DECODER_SHARE = {"piper": 0.695, "kokoro": 0.956}
CALIBRATIONS = [96.0, 80.0, 70.0]


def main():
    timings = json.loads((ROOT / "results" / "timings.json").read_text())
    agg = defaultdict(lambda: {"bin_below": [], "frame_full": [],
                               "frame_95": []})
    for n, t in enumerate(timings):
        audio, sr = sf.read(ROOT / t["wav"])
        for cal in CALIBRATIONS:
            res = pam.analyze(audio, sr, spl_ref=cal, temporal=True)
            m = pam.h1_bin_metrics(res)
            if m is None:
                continue
            key = (t["model"], t["domain"], cal)
            agg[key]["bin_below"].append(m["bin_below_frac"])
            agg[key]["frame_full"].append(m["frame_fully_maskable_frac"])
            agg[key]["frame_95"].append(m["frame_mostly_maskable_frac_95"])
        if n % 15 == 0:
            print(f"...{n}/{len(timings)}", flush=True)

    summary = {}
    print(f"\n{'model':8s} {'domain':10s} {'cal':>5s} {'bin<thr':>8s} "
          f"{'fr100%':>7s} {'fr95%':>7s} {'H1ceil':>7s} {'H1temp':>7s}")
    for (model, domain, cal), a in sorted(agg.items()):
        bb = float(np.mean(a["bin_below"]))
        ff = float(np.mean(a["frame_full"]))
        f95 = float(np.mean(a["frame_95"]))
        share = DECODER_SHARE[model]
        summary[f"{model}/{domain}/{int(cal)}"] = {
            "bin_below_frac": bb, "frame_fully_maskable": ff,
            "frame_95pct_maskable": f95,
            "h1_ceiling": share * bb, "h1_temporal_100": share * ff,
            "h1_temporal_95": share * f95,
        }
        print(f"{model:8s} {domain:10s} {cal:5.0f} {bb:8.3f} {ff:7.3f} "
              f"{f95:7.3f} {share*bb:7.3f} {share*f95:7.3f}")

    (ROOT / "results" / "h1_v2.json").write_text(json.dumps(summary, indent=1))
    print("wrote results/h1_v2.json")


if __name__ == "__main__":
    main()
