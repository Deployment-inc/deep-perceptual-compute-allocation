# Sotto — Perceptual Compute Allocation for CPU Speech Synthesis

Code, corpus, measurements, listening-study instrument, and paper source for
*"Most of What Neural TTS Computes, Nobody Can Hear: Perceptual Compute Allocation for CPU Speech Synthesis"*
(Aayush Gupta, Jayesh Gupta, Himanshu Rathore — Deployment Inc., 2026).

Everything reported in the paper is reproducible from this repository; every experiment, including the negative results, is here.

## Layout

| Path | What |
|---|---|
| `paper/sotto.tex` | Manuscript (LaTeX source, inline bibliography). `paper/SUBMISSION.md` is the arXiv checklist. |
| `scripts/corpus.py` | The fixed 90-utterance, three-domain evaluation corpus. |
| `scripts/synth_corpus.py` | Synthesizes the corpus with Piper and Kokoro; records RTF timings. |
| `scripts/profile_stages.py` | ONNX Runtime per-node profiling → stage shares (RQ2). |
| `scripts/pam.py` | From-scratch MPEG-1 Model-1-lineage psychoacoustic model (+ forward masking, exclusive thresholds). |
| `scripts/pam2.py` | Wrapper for the vetted spreading-matrix PAM (`vendor/Python-Audio-Coder`). |
| `scripts/run_h1*.py` | Existence measurement (H1). |
| `scripts/h3_proxy*.py`, `scripts/h3_pam2.py` | Criterion test (H3): deletion operator, bin-matched budgets, paired Wilcoxon tests. |
| `scripts/h3_noise_shaping.py` | Noise operator + the Δ-probe calibration. |
| `scripts/rq3_mel_proxy.py` | Pre-waveform threshold predictability (RQ3). |
| `results/` | All measured JSON outputs and run logs, including the x86 replication (`x86_results.json`). |
| `study/` | Pre-registered ABX listening study: static web instrument (`index.html` + `audio/`), `PROTOCOL.md`, `analyze.py`. |
| `figures/` | Generated figures. |

## Setup

```bash
uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install numpy scipy soundfile matplotlib onnxruntime piper-tts kokoro-onnx onnx pesq pystoi
# models (not committed):
curl -sL -o models/en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
curl -sL -o models/en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
curl -sL -o models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -sL -o models/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
# reference psychoacoustic model (not vendored — no license file upstream; used by scripts/pam2.py):
git clone --depth 1 https://github.com/TUIlmenauAMS/Python-Audio-Coder vendor/Python-Audio-Coder
```

## Reproduce

```bash
python scripts/synth_corpus.py      # corpus WAVs + timings.json
python scripts/profile_stages.py    # stage shares
python scripts/run_h1_v2.py         # H1 ladder
python scripts/h3_proxy3.py         # H3 deletion, Model-1 PAM
python scripts/h3_pam2.py           # H3 deletion + H1, vetted calibrated PAM
python scripts/h3_noise_shaping.py  # noise operator + Δ-probe
python scripts/rq3_mel_proxy.py     # RQ3
```

All seeds are fixed (1234). Timings in the paper were taken on an Apple M5 Pro and an AWS c7i.2xlarge (Intel Xeon Platinum 8488C); see `results/x86_results.json`.

## Listening study

See `study/PROTOCOL.md`. Host the `study/` folder on any static host, set the completion code and (optionally) a results endpoint in `study/index.html`, recruit via Prolific, then `python study/analyze.py responses.jsonl`.

## License

Code: MIT. Corpus texts and generated audio: CC BY 4.0. Third-party models retain their own licenses (Kokoro: Apache-2.0; Piper: MIT; `vendor/Python-Audio-Coder`: see its LICENSE).
