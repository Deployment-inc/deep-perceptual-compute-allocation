"""RQ2: where does wall-clock live inside each model?

Runs each ONNX model with onnxruntime profiling enabled on a handful of
utterances, parses the JSON trace, and groups per-node kernel time by the
top-level scope in the node name (e.g. /enc_p, /flow, /dec for Piper VITS).

Also measures the Python-side pipeline split (phonemization vs ONNX run).
Outputs results/stage_profile.json and prints a summary.
"""

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import onnxruntime as ort

sys.path.insert(0, str(Path(__file__).parent))
from corpus import CORPUS

ROOT = Path(__file__).parent.parent
PROF_DIR = ROOT / "results" / "profiles"
PROF_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_TEXTS = [CORPUS["agent"][0], CORPUS["agent"][5],
                CORPUS["narration"][0], CORPUS["narration"][4],
                CORPUS["hinglish"][0], CORPUS["hinglish"][7]]


def scope_of(node_name):
    """Top-level scope component of an ONNX node name like /dec/conv/Conv."""
    if not node_name.startswith("/"):
        return "(root)"
    parts = node_name.split("/")
    return "/" + parts[1] if len(parts) > 1 else "(root)"


def parse_profile(path):
    events = json.loads(Path(path).read_text())
    by_scope = defaultdict(float)
    total = 0.0
    for ev in events:
        if ev.get("cat") == "Node" and ev.get("name", "").endswith("_kernel_time"):
            node = ev.get("args", {}).get("op_name", "")
            name = ev["name"][: -len("_kernel_time")]
            dur = ev.get("dur", 0) / 1e6  # us -> s
            by_scope[scope_of(name)] += dur
            total += dur
    return by_scope, total


def profiled_session(model_path, tag):
    so = ort.SessionOptions()
    so.enable_profiling = True
    so.profile_file_prefix = str(PROF_DIR / tag)
    return ort.InferenceSession(str(model_path), sess_options=so,
                                providers=["CPUExecutionProvider"])


def profile_piper():
    from piper import PiperVoice
    voice = PiperVoice.load(ROOT / "models" / "en_US-lessac-medium.onnx")
    sess_attr = "session" if hasattr(voice, "session") else None
    if sess_attr is None:
        for a in dir(voice):
            if "session" in a.lower():
                sess_attr = a
                break
    setattr(voice, sess_attr,
            profiled_session(ROOT / "models" / "en_US-lessac-medium.onnx",
                             "piper"))
    phon_time = 0.0
    onnx_time = 0.0
    for text in SAMPLE_TEXTS:
        t0 = time.perf_counter()
        list(voice.synthesize(text))
        onnx_time += time.perf_counter() - t0
        t0 = time.perf_counter()
        voice.phonemize(text)
        phon_time += time.perf_counter() - t0
    prof = getattr(voice, sess_attr).end_profiling()
    by_scope, total = parse_profile(prof)
    return {"by_scope": dict(by_scope), "kernel_total_s": total,
            "pipeline": {"phonemize_s": phon_time,
                         "synthesize_total_s": onnx_time}}


def profile_kokoro():
    from kokoro_onnx import Kokoro
    k = Kokoro(str(ROOT / "models" / "kokoro-v1.0.onnx"),
               str(ROOT / "models" / "voices-v1.0.bin"))
    k.sess = profiled_session(ROOT / "models" / "kokoro-v1.0.onnx", "kokoro")
    tok_time = 0.0
    onnx_time = 0.0
    for text in SAMPLE_TEXTS:
        t0 = time.perf_counter()
        k.create(text, voice="af_sarah", speed=1.0, lang="en-us")
        onnx_time += time.perf_counter() - t0
        t0 = time.perf_counter()
        k.tokenizer.phonemize(text, lang="en-us")
        tok_time += time.perf_counter() - t0
    prof = k.sess.end_profiling()
    by_scope, total = parse_profile(prof)
    return {"by_scope": dict(by_scope), "kernel_total_s": total,
            "pipeline": {"phonemize_s": tok_time,
                         "create_total_s": onnx_time}}


def summarize(name, res):
    print(f"\n=== {name} ===")
    total = res["kernel_total_s"]
    scopes = sorted(res["by_scope"].items(), key=lambda kv: -kv[1])
    for scope, s in scopes[:15]:
        print(f"  {scope:30s} {s:8.3f}s  {100*s/total:5.1f}%")
    print(f"  {'TOTAL kernel':30s} {total:8.3f}s")
    print(f"  pipeline: {res['pipeline']}")


def main():
    out = {}
    out["piper"] = profile_piper()
    summarize("piper", out["piper"])
    out["kokoro"] = profile_kokoro()
    summarize("kokoro", out["kokoro"])
    (ROOT / "results" / "stage_profile.json").write_text(json.dumps(out, indent=1))
    print("\nwrote results/stage_profile.json")


if __name__ == "__main__":
    main()
