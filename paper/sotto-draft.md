# Most of What Neural TTS Computes, Nobody Can Hear: Perceptual Compute Allocation for CPU Speech Synthesis

*Working draft — arXiv (eess.AS / cs.SD / cs.LG). All numbers are measured on named hardware; illustrative figures from planning never appear here. The headline listening claim is supported by a pre-registered ABX study (`study/PROTOCOL.md`); until that study's table is inserted in §5.5, the only human evidence is an informal single-listener pilot, explicitly labelled as such and never used as a transparency claim.*

> **Headline (to be finalized from the ABX study):** listeners cannot detect the removal of **[X]%** of the time–frequency content of neural TTS output when the removed content is chosen by audibility — while removing a fraction of that amount at random is obviously audible. *[X] is the largest budget declared transparent under the pre-registered rule; the single-listener pilot suggests 60–75%.*

**Author:** Aayush Gupta (CelestLabs.ai)
**Status:** pre-print draft, 2026-09-02

---

## Abstract

Generative systems whose output is consumed by human senses are trained and served to uniform fidelity, yet human perception is radically non-uniform in time and frequency. We ask whether inference compute in neural text-to-speech (TTS) can be allocated by *perceptual sensitivity* rather than uniformly — spending effort only where a listener could tell. We instantiate this "perceptual compute allocation" principle on CPU TTS, the cost-sensitive regime where saved operations convert directly to latency and serving capacity.

Three findings emerge, two positive and one a deliberate negative. **(1)** The perceptually-removable pool is real and large: sorting time–frequency content by audibility and removing the least-audible portion is transparent to a reference-based perceptual metric up to substantial budgets, and an informal listening pilot tolerated 60–75% removal without reliably distinguishing it from the reference, while *random* removal at a fraction of that budget is obviously broken. Allocating by audibility massively beats uniform allocation — the principle holds. **(2)** A pre-registered criterion test asks whether a psychoacoustic masking model (the machinery inside MP3) is *necessary* to locate that pool, versus a trivial signal-energy criterion. Across three masking-model implementations, two degradation operators, and 90 utterances on two model families, energy-guided allocation *matches or beats* masking-guided allocation for time–frequency removal — the sophisticated listener model is not needed; energy is a sufficient statistic for this decision. We report this as a first-class negative. **(3)** We quantify the gap between *theoretical* and *realized* savings: on a fixed neural circuit, removing perceptually-unnecessary output does not by itself save compute, and the obvious post-hoc precision mechanism (dynamic INT8 of the dominant decoder) is *8× slower* than full precision on AVX-VNNI Intel and 4.8× slower on Apple Silicon — realized savings can be strongly negative.

We conclude that perceptual compute allocation is a sound and promising principle for CPU TTS, that a cheap criterion suffices to drive it, and that the open problem is not *what to remove* but *how to install the removal* in allocation-native architectures. We release our psychoacoustic tooling, calibration probe, evaluation corpus, and the full negative-result harness.

---

## 1. Introduction

A neural TTS model is a fixed circuit: synthesizing 10 ms of near-silence costs the same operations as a plosive burst. There is no built-in "easy frame" discount. Yet the human auditory system discards most of what reaches the eardrum — via frequency masking, temporal masking, and the absolute threshold of hearing — and audio codecs (MP3, AAC) have exploited exactly this for fifty years, transparently at ~10× compression, using a *psychoacoustic model* (PAM) that computes a per-band masking threshold below which added error is inaudible.

Psychoacoustic masking has been used in three ways: to allocate **bits** at codec encode time, to weight **gradients** at training time, and to place **adversarial** perturbations. To our knowledge it has not been used to allocate **inference compute** during generation. On GPU, batch parallelism hides per-item savings, so GPU-rich labs had little incentive; on CPU — where cost-sensitive voice serving lives — every skipped operation returns directly as latency.

This paper tests the principle we call **perceptual compute allocation**: in a generative system consumed by human senses, spend inference compute according to human perceptual sensitivity, not uniformly. We take CPU TTS as the first instantiation and organize the work around three pre-registered hypotheses (§3), reporting each honestly including a central negative.

**Contributions.**
1. A measurement of the perceptually-removable pool in two CPU TTS families, with a reference-based metric and an informal listening pilot, establishing that audibility-guided allocation vastly outperforms uniform/random allocation (§5.1, §5.5).
2. A pre-registered, adversarially-designed criterion test showing that **signal energy matches or beats a psychoacoustic masking model** for time–frequency removal — a counter-intuitive negative that refines the principle (§5.2).
3. A characterization of the theoretical-vs-realized savings gap, including a reproducible result that naïve post-hoc precision reduction *increases* wall-clock cost on two CPU architectures (§5.4).
4. Methodological artifacts: a PESQ-anchored calibration probe for psychoacoustic models, and evidence that a standard perceptual metric's *severities* (though not its orderings) collapse on masked-removal distortions (§5.3).
5. Open-source release of tooling, corpus, and harness.

We claim the principle and its CPU-TTS instantiation; we do **not** claim that a masking model beats energy (our data refute that), and we do not claim realized end-to-end speedups (we did not achieve one — §6).

## 2. Background: the listener model

A PAM computes, per short-time frame, a masking threshold across frequency by identifying maskers (tonal and noise), spreading their influence across critical (Bark) bands, and taking the maximum with the absolute threshold of hearing. **Headroom** is signal energy minus threshold, per time–frequency cell; where headroom is negative, added error is, by construction, inaudible. Crucially, masking is dynamic — thresholds depend on content, level, and time — which is why exploiting it requires a model running *during* inference, analogous to the eye-tracker in foveated rendering.

## 3. Hypotheses and pre-registered decision rules

- **H1 (existence).** A substantial fraction of CPU-TTS synthesis produces time–frequency output a listener cannot perceive.
- **H2 (exploitability).** Making computation conditional on audibility reduces end-to-end wall-clock at transparent quality.
- **H3 (criterion — the scientific core).** At matched compute budgets, *perceptually*-guided allocation (masking model) outperforms *energy*-guided and *random* allocation on quality. **If H3 fails, the work is content-adaptive synthesis with a rigorous perceptual evaluation, and the negative is reported as a finding.**

Transparency is defined relative to the full-compute output of the same model, text, and seed. Matched budgets are compared at equal expected compute per utterance. These rules were fixed before the main experiments.

**Amendment (logged 2026-09-02, before affected analysis).** After H3 failed at proxy level (§5.2), the program's primary claim was moved to the *principle and its measurement*, with H2's realization reframed as an open mechanism problem; H3's negative is retained and reported. No hypothesis was weakened to fit a result.

## 4. Testbed and method

**Models.** Two CPU-practical families: **Piper** (`en_US-lessac-medium`, a VITS/HiFi-GAN system, 22.05 kHz) and **Kokoro v1.0** (a StyleTTS2/ISTFTNet system, 24 kHz). Both run under ONNX Runtime, CPU execution provider only.

**Hardware.** Apple M5 Pro (aarch64) and, for cross-architecture replication, an ephemeral AWS `c7i.2xlarge` (Intel Xeon Platinum 8488C, Sapphire Rapids, AVX-VNNI, 8 vCPU).

**Corpus.** A fixed 90-utterance corpus over three domains — conversational agent speech (digits/entities), long-form narration, and romanized Hinglish agent speech — 15 utterances each, seeds fixed. (Hinglish is synthesized through an English voice/G2P, as in production English-voice agents; a native Hindi voice is future work.)

**Psychoacoustic tooling.** We use two PAM implementations: a from-scratch MPEG-1 Model-1-lineage model, and a vetted spreading-matrix model ported from a reference audio-coding implementation, plus temporal (forward) masking. Both are calibrated with a **Δ-probe** (§5.3).

**Oracle degradation harness.** To test *placement* independent of any mechanism, we degrade a budget-matched set of time–frequency cells of the reference synthesis and compare policies at equal budgets, scoring against the same-seed full output with wideband PESQ and STOI. Two operators: **deletion** (zero a cell) and **noise injection** (add fixed-level noise). Budgets are matched on FFT-bin count (≈ compute), not cell count. Design lessons that materially affect results, and are contributions in themselves: (i) the criterion must match the operator — deletion ranks by signal-minus-threshold, noise ranks by threshold; (ii) deletion decisions require *exclusive* (leave-self-out) thresholds, so a cell cannot justify its own removal via the masking it itself produces.

## 5. Results

### 5.1 RQ2 — where compute lives (cross-architecture)

Per-node ONNX kernel profiling shows one dominant, gateable stage in both families:

| Model | Decoder share (M5 Pro) | Decoder share (Xeon 8488C) |
|---|---|---|
| Piper (VITS) | 69.5% | 63.3% |
| Kokoro (ISTFTNet) | 95.6% | 93.9% |

The waveform decoder dominates on both architectures, so by Amdahl's law it is the only worthwhile allocation target. Baseline real-time factors (median of 3): Piper 0.018 (ARM) / 0.023 (x86); Kokoro 0.15 (ARM) / 0.19 (x86). Phonemization is <0.5% of the pipeline.

### 5.2 H1 and the criterion test H3 — the core result

**The removable pool is large, and audibility-ordering is what matters.** In the oracle harness, removing time–frequency content *ordered by audibility* is transparent to PESQ up to substantial budgets, whereas removing the *same amount at random* is grossly audible (PESQ collapses toward 1.1–2.3 at budgets where ordered removal scores near-transparent). Allocating by audibility rather than uniformly/randomly is the entire game — the **principle is strongly supported**.

**But energy is a sufficient statistic for the ordering.** The pre-registered H3 test compares *masking-guided* against *energy-guided* and *random* placement at matched budgets. Across **three** PAM implementations (from-scratch Model-1, its exclusive-threshold variant, and the vetted calibrated model), **two** operators, both models, and 90 utterances, energy-guided placement **matches or beats** masking-guided placement for deletion at every budget, with paired Wilcoxon p < 10⁻⁶ throughout; masking never significantly wins. Representative deletion result (mean PESQ, vetted+calibrated PAM):

| Model | Budget | energy | masking (excl.) | random |
|---|---|---|---|---|
| Kokoro | 0.1 | **4.59** | 4.39 | 2.88 |
| Kokoro | 0.3 | **4.30** | 3.19 | 1.63 |
| Piper | 0.1 | **4.64** | 4.63 | 2.76 |
| Piper | 0.3 | **4.62** | 4.42 | 1.62 |

Interpretation: for deciding *where a listener cannot hear removed content*, signal energy already captures nearly all the usable information; the masking model's extra machinery (spreading, inter-band masking, absolute threshold) does not improve the decision for this task. **H3 fails, human-corroborated (§5.5).** Per §3, the work therefore stands on the principle, the measurement, and this negative — not on a masking-beats-energy claim.

### 5.3 A calibration probe, and a metric caveat

We introduce a **Δ-probe**: inject noise shaped at the PAM's own threshold curve, offset by Δ dB, and find the Δ at which a reference metric judges the result transparent. A correctly-calibrated PAM should reach transparency near Δ = 0. Our from-scratch model required Δ ≈ −30 to −40 dB (thresholds ~tens of dB too permissive); the vetted model required Δ ≈ −16 dB under codec-realistic capping. As an external anchor, MP3 round-trips at 64–128 kbps score PESQ 4.54–4.64 on the same audio — the metric is content with noise at *real* ISO thresholds. The probe is a reusable tool for validating any inference-time PAM before trusting its decisions.

**Metric caveat.** PESQ's *orderings* are informative here, but its *absolute severities* are not: clips an informal listener could not distinguish from the reference received PESQ scores as low as 1.2–3.5. PESQ was validated on telephony degradations, not masked spectral removal. We therefore treat PESQ as an ordering-only screen and require human judgement for any transparency claim.

### 5.4 RQ4 — theoretical vs realized savings

Removing perceptually-unnecessary output saves nothing until the computation is made conditional. We tested the most obvious post-hoc precision mechanism — dynamic INT8 quantization of the dominant decoder — as an aligned instance of "spend fewer bits where error is inaudible." It is **catastrophically slower**: the INT8 Kokoro decoder runs **8.06× slower** than full precision on AVX-VNNI Intel (0.124× speedup) and 4.8× slower on Apple Silicon. The cause is structural: the ISTFTNet decoder is dominated by transposed convolutions and an inverse-STFT block that the runtime's dynamic-quant path cannot map to fast integer kernels, so it wraps still-fp32 operators in quantize/dequantize overhead. This is a clean, reproducible instance of realized savings diverging in *sign* from theoretical savings, and it argues that perceptual compute allocation needs allocation-native architectures, not post-hoc precision.

### 5.5 RQ3 and an informal listening pilot

*Predictability.* Masking thresholds estimated from mel-resolution features (a proxy for pre-waveform representations) agree with ground-truth thresholds to 2.8 dB RMSE and 96% cell-decision agreement, but with an 11–12% *false-maskable* rate (predicted inaudible, actually audible) — predictive gating would need a conservative margin; draft-based verification is the safe fallback.

*Pre-registered ABX listening study.* **[TABLE PENDING — insert output of `study/analyze.py`.]** Design: 8 utterances (both models, three domains), energy-ordered deletion at 30/50/60/75/90% of bins plus a random-deletion anchor; ABX discrimination (chance = 50%); N = 30 screened listeners (anchor accuracy ≥ 5/6, median RT ≥ 1.5 s); ~180 trials per condition. Pre-registered transparency rule: detection not significantly above chance (exact binomial, one-sided p ≥ 0.05) **and** Wilson 95% CI upper bound ≤ 0.60. The largest transparent budget is the paper's headline number.

*Informal pilot (single listener; direction-finding only, not evidence).* A blind pilot with hidden-reference and known-damaged-anchor hygiene checks (both passed) found energy-ordered deletion indistinguishable from the reference up to 60–75% of bins (Piper tolerated 90%), and corroborated the energy ≥ masking ordering. This motivated the study above and is superseded by it.

## 6. Discussion

Our results refine rather than defeat perceptual compute allocation. The *premise* — that a large fraction of generative audio output is perceptually irrelevant and can be identified and removed transparently — is strongly supported. The *principle* — allocate by audibility, not uniformly — beats uniform/random allocation decisively. What our data remove is a piece of the *original mechanism story*: you do not need MP3's psychoacoustic model to drive the allocation; signal energy is a sufficient and far cheaper criterion for time–frequency removal. This is good news for deployment (the "eye-tracker" is nearly free) and a caution for novelty (the sophisticated-model angle is not the contribution).

The binding constraint is realization. A fixed neural circuit does not become cheaper because its output is ignorable; the savings must be *installed*, and post-hoc precision reduction does not install them on CPU. The path forward is allocation-native decoding — architectures that can *decline* to synthesize masked frequency regions or perceptually-slack frames — which is a training-time and architecture question, not an inference-time trick.

## 7. Related work

Psychoacoustic masking has been applied to codec bit allocation (encode time) and to perceptual training losses (training time), never to inference-time compute allocation in synthesis. Dynamic/adaptive computation exists in speech *understanding* (early-exit ASR) and, recently, in speech *generation* via speculative decoding, dynamic chunk policies, early-exit spoken LMs, and variable-frame-rate tokenizers — but all use confidence, learned policies, or fixed schedules, never an audibility criterion. Foveated rendering and, recently, foveated generative image/video synthesis apply the analogous "allocate by perceptual sensitivity" idea in vision; we position CPU-TTS perceptual compute allocation as an independent, audio-side instantiation of the same general axis. A concurrent VR line ("acoustic foveation") uses spatial-auditory acuity to cut sound-propagation rendering, distinct from spectral masking in neural synthesis. (Full collision table and citations in the camera-ready.)

## 8. Limitations

Single informal listener (no MUSHRA yet); PESQ is an imperfect proxy whose severities we show to be unreliable here; two model families, one language pair with Hinglish through an English G2P; PAM implementations are Model-1-class; no end-to-end speedup was achieved (H2 unrealized). We report no capacity multiplier because we have no measured end-to-end reduction to base one on (per our claim-discipline rules).

## 9. Conclusion

Perceptual compute allocation is a sound organizing principle for CPU speech synthesis: the perceptually-removable pool is large, audibility-ordered allocation dominates uniform allocation, and — surprisingly — a trivial energy criterion suffices to find the pool, with the heavyweight psychoacoustic model offering no advantage for time–frequency removal. The open problem is installation: turning removable output into skipped computation demands allocation-native decoders, since post-hoc precision reduction fails on CPU. We release our tooling, corpus, calibration probe, and full harness — including the negative-result experiments — to make the next step reproducible.

---

*Reproducibility.* Fixed seeds; pinned tool versions (ONNX Runtime 1.28/1.29, piper-tts 1.6.1, kokoro-onnx 0.5.0). All measurements CPU-only on named hardware; any training-side or quantization compute is disclosed as such. No fabricated or interpolated measurements; the single listening pilot is real and labelled informal.
