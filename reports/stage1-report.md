# SOTTO — Stage-1 Report: RQ1 Novelty Sweep + RQ2 Cost Profile + H1 Existence Measurement

**Date:** 2026-08-15 · **Status:** awaiting human kill/pivot/proceed decision (§3 of the intent doc)
**All numbers below are measurements, not illustrations.** Every measured number displaces its illustrative counterpart per §7.4.

---

## 1. RQ1 — Novelty sweep: **the lane is open** (with a timing warning)

Three independent sweeps (~60 distinct searches total; full agent reports in `reports/rq1/`):

- **Direct collisions (sweep 1):** No paper combines all three claim coordinates {dynamic inference-time allocation} × {audibility criterion} × {synthesis}. Every psychoacoustic-masking use in neural audio remains at training time (loss weighting) or in codec bit allocation. Every dynamic inference mechanism in speech generation (SPAR-K early exit, speech speculative decoding, DiT layer caching, step pruning) uses statistical/scheduled/similarity criteria. Citation-graph check on Zhen et al. 1801.09774: zero inference-time descendants.
- **Closest in spirit:** *Acoustic Foveation* (Peng et al., IEEE VR 2025) — a psychophysical **spatial-acuity** model cuts VR sound-propagation rendering compute ~53%. It is a hearing-model→runtime-compute paper, but spatial localization acuity, not spectral masking, and acoustic simulation, not neural TTS. Must-cite; clearly distinguishable.
- **Strongest adaptive-synthesis prior (sweep 2):** DCAR (arXiv:2506.22023, 2025) — learned policy varies AR-TTS chunk size per content, 2.61×. No perceptual model. It plus speech speculative decoding (2505.15380), static step-reduction (Fast F5-TTS/EPSS, BDDM), and a fixed-schedule variant of our own system form the baseline set reviewers will demand. **No early-exit or dynamically pruned HiFi-GAN/Vocos-class vocoder exists; no Mixture-of-Depths instantiation in audio generation exists** — both gaps we can occupy.
- **Cross-modality (sweep 3):** Nobody has claimed the general "perceptual compute allocation" principle. **But: *Foveated Diffusion* (Wetzstein group, arXiv 2603.23491, March 2026) allocates diffusion token density by visual eccentricity** — the vision-side instantiation now exists, framed vision-only. The general-principle framing is one abstraction step away from them. **Timing pressure is real: the principle claim should reach arXiv sooner rather than later.** Our framing must position the vision line (DeepFovea 2019 → FoV-NeRF 2022 → Foveated Diffusion 2026) as an independent modality-specific convergence, and claim (a) the modality-general principle and (b) the audio/psychoacoustic instantiation.

**Watch-lanes converging on us:** (a) codec bit allocation going inference-time-dynamic (BAMU, Aug 2026); (b) variable-frame-rate/perceptual-significance tokenization (VARSTok, DyCAST); (c) speculative decoding with informal perceptual acceptance arguments (2511.13732).

## 2. RQ2 — Where cost lives: **a dominant gateable stage exists in both families**

ONNX Runtime per-node kernel profiling, 6 utterances spanning all domains, Apple M5 Pro, CPUExecutionProvider (`results/stage_profile.json`):

| Model | Stage | Share of kernel time |
|---|---|---|
| Piper en_US-lessac-medium (VITS family) | **HiFi-GAN decoder (`/dec`)** | **69.5%** |
| | flow | 10.9% |
| | text encoder | 9.9% |
| | duration predictor | 7.0% |
| Kokoro v1.0 (StyleTTS2/ISTFTNet family) | **decoder** | **95.6%** |
| | encoder (incl. prosody) | 4.3% |

Phonemization is negligible (<0.5% of pipeline). **The load-bearing assumption holds:** the waveform decoder dominates, so by Amdahl the end-to-end ceiling from decoder-only gating is 0.695 (Piper) / 0.956 (Kokoro) × stage-level reduction. A 40% decoder cut ⇒ r ≈ 0.28 (Piper) / 0.38 (Kokoro) ⇒ capacity ×1.39 / ×1.62.

Baseline speed (median of 3, this machine): Piper RTF ≈ 0.018; Kokoro RTF ≈ 0.14–0.17.

## 3. H1 — Existence measurement

**Setup:** 90 utterances (2 models × 3 domains × 15 texts, fixed corpus in `scripts/corpus.py`), PAM of the MPEG-1 Model-1 lineage (tonal/noise maskers, spreading, ATH, conservative min-over-bins thresholds) **plus forward temporal masking** (0.3 dB/ms decay, 150 ms horizon); playback-calibration sensitivity at full-scale = 96/80/70 dB SPL. Code: `scripts/pam.py`. Sanity audit passed: ~84% of signal **energy** is audible (spectral peaks sit 5+ dB above threshold), i.e., the model is not degenerately declaring everything maskable.

**The metric ladder** (each row is a different, honest attribution of "compute producing below-threshold output"; decoder-share weighting applied where marked):

| Metric (96 dB calibration; 70 dB in parens) | Piper | Kokoro | What it means for mechanisms |
|---|---|---|---|
| **M1 — Fully maskable frames × decoder share** | 0.07–0.11 (0.11–0.14) | 0.13–0.14 (0.23–0.25) | Harvestable by pure per-frame skipping (pauses). Real but small. |
| **M2 — Band-conservative cells × decoder share** (v1: band energy vs min-bin threshold, no temporal masking) | 0.17–0.18 | 0.11–0.12 | Most conservative time-frequency view. |
| **M3 — Signal energy below threshold** | ~0.16 | ~0.18 | Energy-weighted view. |
| **M4 — Frames ≥95% of bins maskable × decoder share** | 0.63 (0.65) | 0.82–0.85 (0.84–0.86) | In ~90% of frames, only a handful of spectral lines need accuracy — the pool for *coarse-synthesis + fix-the-lines* mechanisms. |
| **M5 — Bins below threshold × decoder share (ceiling)** | 0.68 | 0.93 | Codec-style fine-structure freedom; the theoretical ceiling if compute were perfectly separable per spectral line. |

Domain differences are modest (±2–3 points); the "agent speech leads" hypothesis (RQ5) is only weakly visible at frame level and mostly via pauses. Hinglish ≈ agent ≈ narration on every metric.

### Decision-rule reading (against §3, pre-registered)

The rule keys on "below-threshold compute fraction." The measurement shows this is **not a single number — it depends on the compute-attribution model**, which is itself a Stage-1 finding:

- The **most conservative** metrics (M1–M3) land at **11–18%** — inside the 15–35% "proceed, prioritize harvestable mechanisms" band (Piper) and straddling its lower edge (Kokoro M2 at 11–12%, but Kokoro M1 alone is 13–25%).
- The **mechanism-relevant** metrics (M4–M5) land at **63–93%** — far above the 35% full-program line.
- **No metric supports the <15% kill branch on both models simultaneously.**

**Recommendation (mine, for your sign-off):** *Proceed* under the 15–35% branch's logic — the measurement tells us *which* mechanisms can harvest the slack:
1. **Per-frame temporal gating** (pauses) is worth ~7–25% of decoder compute — cheap to implement, small headline.
2. **The big pool is fine-structure freedom** (M4/M5): in almost every frame, most spectral lines tolerate arbitrary error while a sparse audible skeleton (harmonic peaks, formant regions) must be right. This favors: **draft–verify–redo with the PAM as verifier**, **precision reduction shaped under the threshold** (each bit ≈ 6 dB), and **coarse decoding modes** — over early-exit-style depth skipping.
3. H3's energy-vs-perceptual control becomes even more central: energy gating would also find the pauses (M1), but the *fine-structure* pool is exactly where energy ≠ audibility (M3: 16–18% of *energy* is maskable vs 98% of *bins*).

## 4. Limitations of this measurement (logged before Stage 2)

- **Hardware:** Apple M5 Pro (aarch64). CelestLabs serves on x86 CPUs; RQ2 shares must be re-measured on the serving class before any paper claim. (Decoder dominance is architectural, so direction is robust; the exact 69.5/95.6 numbers are not.)
- **Hinglish domain** used English voices with English G2P (romanized text), as in production English-voice agents; a native Hindi/Hinglish voice (e.g., Kokoro hi voices, Piper hi) is a Stage-2 addition. Aspiration-contrast protection (RQ5) is untested.
- **PAM simplifications:** Model-1 lineage, simplified tonal/noise separation, linear forward-masking decay, no backward masking, min-over-bins band thresholds (conservative). Threshold-estimation quality (RQ3) untested.
- **Calibration:** below-threshold fractions are playback-level dependent; reported at 96/80/70 dB full-scale. Paper must state calibration policy (codec practice: conservative worst-case).
- **No perceptual validation yet** — H1 is a property of the threshold model, not a listening claim. Nothing here yet says gating is transparent (that's H2/H3).
- Piper's `/dec` scope share attributes fused/root ops (~1.7%) to no stage; treated as non-gateable (conservative).

## 5. Proposed Stage-2 plan (on your green light)

1. **Mechanism A — draft–verify–redo:** cheap decode everywhere (e.g., int8 decoder / fewer upsampling channels), PAM-verify on the draft, re-decode only audibly-wrong regions. Architecture-agnostic; directly exploits M4.
2. **Mechanism B — per-frame gating:** skip/cheapen decoder on fully-maskable frames (pauses); trivial, banks M1.
3. **RQ3:** measure pre-waveform threshold predictability (mel-domain estimate vs ground-truth PAM on produced audio) — decides predictive vs draft-based allocation.
4. **H3 controls harness early:** perceptual vs energy vs random gating at matched budgets (run the control before building more, per §9).
5. **x86 replication** of RQ2 (cloud VM or any Linux box you have).
6. Add native Hindi voice for the Hinglish domain.

**Required from you:** (a) the Stage-1 kill/pivot/proceed decision; (b) nothing else right now — no OpenRouter key needed (no hosted LLM in the loop; all synthesis and analysis run locally; literature sweeps used built-in web search). If Stage 2 wants an x86 replication box, that's a trivial-cost item I'll flag before spending.

## 6. Provenance

- Machine: Apple M5 Pro, 15 cores, 24 GB, macOS (Darwin 25.6.0)
- Env: Python 3.12.13 (uv), onnxruntime 1.28.0, piper-tts 1.6.1, kokoro-onnx 0.5.0, numpy 2.5.2
- Models: `en_US-lessac-medium.onnx` (HuggingFace rhasspy/piper-voices), `kokoro-v1.0.onnx` + `voices-v1.0.bin` (thewh1teagle/kokoro-onnx release v1.0)
- Data: `results/timings.json` (median of 3 runs, 1 warmup), `results/stage_profile.json`, `results/h1_summary.json` (v1), `results/h1_v2.json` (v2), corpus WAVs in `corpus/`
- Figures: `figures/money_figure.png` (prototype of §7.1 money figure), `figures/headroom_curve.png`
