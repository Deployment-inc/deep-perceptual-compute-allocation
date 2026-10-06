# Sotto: Hearing's Blind Spots

Code, corpus, measurements, listening-study instrument, and paper source for
*"Hearing's Blind Spots: Toward Perceptual Compute Allocation in Neural Text-to-Speech"*
(Aayush Gupta, Deployment Inc., 2026).

**Listen first:** paired audio examples are in [`examples/`](examples/), and the blind ABX test runs in the browser at https://deployment-inc.github.io/deep-perceptual-compute-allocation/

This is an exploratory oracle study of spectral perturbations in completed Piper and Kokoro waveforms. At matched target spectral-bin removal budgets, energy ranking achieves higher mean PESQ than the tested masking criteria and random deletion. The paper also reports masking-calibration sensitivity, CPU profiles, and an implementation-specific slowdown from dynamic INT8 quantization.

These results do not demonstrate saved synthesis computation or a human-transparent deletion budget. The listening evidence is an author-only pilot. The mel diagnostic starts from a completed waveform, rather than predicting audibility before synthesis.

The repository provides scripts, aggregate results, audio, and a listening-study instrument. It does not establish complete independent reproducibility of every reported measurement: complete trial-level records or generating scripts for the ABX counts, informal observations, Apple decoder microbenchmark, and spreading-matrix probe were not verified in the pinned experimental release. See Appendix C of the [current manuscript](paper/sotto.tex) for provenance and limitations. Historical planning documents and draft manuscripts record earlier hypotheses and interpretations; they are not independently timestamped preregistrations and do not supersede the current paper.

## Layout

| Path | What |
|---|---|
| `paper/sotto.tex` | Manuscript (LaTeX source, inline bibliography). `paper/SUBMISSION.md` is the arXiv checklist. |
| `scripts/corpus.py` | The fixed 45-text, three-domain corpus, producing 90 waveforms across two models. |
| `scripts/synth_corpus.py` | Synthesizes the corpus with Piper and Kokoro; records RTF timings. |
| `scripts/profile_stages.py` | ONNX Runtime per-node profiling → stage shares (RQ2). |
| `scripts/pam.py` | From-scratch MPEG-1 Model-1-lineage psychoacoustic model (+ forward masking, exclusive thresholds). |
| `scripts/pam2.py` | Wrapper for the reference spreading-matrix PAM (`vendor/Python-Audio-Coder`). |
| `scripts/run_h1*.py` | Model-declared masking diagnostics (H1), not validated inaudibility estimates. |
| `scripts/h3_proxy*.py`, `scripts/h3_pam2.py` | Criterion test (H3): deletion operator, bin-matched budgets, paired Wilcoxon tests. |
| `scripts/h3_noise_shaping.py` | Noise operator + the Δ-probe calibration. |
| `scripts/rq3_mel_proxy.py` | Completed-waveform mel-resolution reconstruction diagnostic (RQ3). |
| `results/` | Committed aggregate JSON outputs and run logs, including the x86 results (`x86_results.json`). |
| `study/` | Exploratory ABX listening-study instrument and archived protocol: static web instrument (`index.html` + `audio/`), `PROTOCOL.md`, `analyze.py`. |
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
# reference psychoacoustic model (not vendored; no license file upstream; used by scripts/pam2.py):
git clone --depth 1 https://github.com/TUIlmenauAMS/Python-Audio-Coder vendor/Python-Audio-Coder
```

## Reproduce

```bash
python scripts/synth_corpus.py      # corpus WAVs + timings.json
python scripts/profile_stages.py    # stage shares
python scripts/run_h1_v2.py         # H1 ladder
python scripts/h3_proxy3.py         # H3 deletion, Model-1 PAM
python scripts/h3_pam2.py           # H3 deletion + H1, reference PAM with an engineering threshold offset
python scripts/h3_noise_shaping.py  # noise operator + Δ-probe
python scripts/rq3_mel_proxy.py     # RQ3
```

All seeds are fixed (1234). Timings in the paper were taken on an Apple M5 Pro and an AWS c7i.2xlarge (Intel Xeon Platinum 8488C); see `results/x86_results.json`.

## Listening study

The existing pilot has one non-naive listener and six trials per condition. It does not establish population-level perceptual transparency. Before new recruitment, prespecify a study and analysis accounting for repeated listeners and utterances, as discussed in the manuscript. The archived protocol is research provenance, not proof of preregistration.

See `study/PROTOCOL.md`. Host the `study/` folder on any static host, set the completion code and (optionally) a results endpoint in `study/index.html`, recruit via Prolific, then `python study/analyze.py responses.jsonl`.

## License

Code: MIT. Corpus texts and generated audio: CC BY 4.0. Third-party models retain their own licenses (Kokoro: Apache-2.0; Piper: MIT; `vendor/Python-Audio-Coder`: check upstream terms before redistribution; no license file was verified).
