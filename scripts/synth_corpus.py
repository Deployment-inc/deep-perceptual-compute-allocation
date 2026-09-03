"""Synthesize the Stage-1 corpus with both model families, saving WAVs and
per-utterance wall-clock timings (median of 3 runs after 1 warmup).

Outputs:
  corpus/<model>/<domain>_<idx>.wav
  results/timings.json
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).parent))
from corpus import CORPUS

ROOT = Path(__file__).parent.parent
N_RUNS = 3


def synth_piper(voice, text):
    chunks = [np.frombuffer(ch.audio_int16_bytes, dtype=np.int16)
              for ch in voice.synthesize(text)]
    audio = np.concatenate(chunks).astype(np.float32) / 32768.0
    return audio, voice.config.sample_rate


def synth_kokoro(k, text):
    samples, sr = k.create(text, voice="af_sarah", speed=1.0, lang="en-us")
    return samples.astype(np.float32), sr


def run_model(name, synth_fn):
    out_dir = ROOT / "corpus" / name
    out_dir.mkdir(parents=True, exist_ok=True)
    timings = []
    # warmup
    synth_fn("This is a warm up sentence for the synthesizer.")
    for domain, texts in CORPUS.items():
        for i, text in enumerate(texts):
            times = []
            audio, sr = None, None
            for _ in range(N_RUNS):
                t0 = time.perf_counter()
                audio, sr = synth_fn(text)
                times.append(time.perf_counter() - t0)
            wav = out_dir / f"{domain}_{i:02d}.wav"
            sf.write(wav, audio, sr)
            dur = len(audio) / sr
            med = float(np.median(times))
            timings.append({
                "model": name, "domain": domain, "idx": i, "text": text,
                "wav": str(wav.relative_to(ROOT)), "sr": sr,
                "audio_s": dur, "synth_s_median": med,
                "synth_s_all": times, "rtf": med / dur if dur > 0 else None,
            })
            print(f"{name} {domain}_{i:02d}: {dur:.2f}s audio, "
                  f"{med:.3f}s synth, RTF {med/dur:.3f}", flush=True)
    return timings


def main():
    all_timings = []

    from piper import PiperVoice
    voice = PiperVoice.load(ROOT / "models" / "en_US-lessac-medium.onnx")
    all_timings += run_model("piper", lambda t: synth_piper(voice, t))
    del voice

    from kokoro_onnx import Kokoro
    k = Kokoro(str(ROOT / "models" / "kokoro-v1.0.onnx"),
               str(ROOT / "models" / "voices-v1.0.bin"))
    all_timings += run_model("kokoro", lambda t: synth_kokoro(k, t))

    out = ROOT / "results" / "timings.json"
    out.write_text(json.dumps(all_timings, indent=1))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
