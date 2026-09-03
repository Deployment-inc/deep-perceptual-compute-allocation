# SOTTO — Stage-2 Interim Report: Early H3 Controls, RQ3, Mechanism-A Scaffolding

**Date:** 2026-08-16 · **Status:** Stage 2 in progress (proceed decision logged 2026-08-16)
**Headline:** The pre-registered H3 risk is live — under PESQ evaluation, energy-guided allocation currently beats our Model-1 PAM-guided allocation at matched budgets. Diagnosis points at PAM calibration, not at the thesis; the fix list is concrete. Everything else advanced: RQ3 answered (predictive gating feasible with margin), Mechanism A unblocked (bit-exact decoder split + aligned int8 draft).

---

## 1. H3 criterion control (oracle degradation proxy) — three iterations

**Design:** degrade a budget-matched set of (frame, Bark-band) STFT cells of the reference synthesis and compare *placement policies* at equal budgets. Quality vs the same-seed full output: PESQ-WB + STOI at 16 kHz (round-trip fidelity verified: 232 dB SNR, PESQ 4.64 ceiling). 90 utterances, both models, seeds fixed. Data: `results/h3_proxy{,2,3}.json`.

**Iteration lessons (methodology findings, paper-worthy):**
1. **v1 flaw — criterion/operator mismatch.** Ranking cells by "signal below threshold" pairs with *deletion*; placing *injected noise* must rank by "threshold high enough to mask the noise." Mismatched pairing produced artifactual low-budget losses.
2. **v2 flaw — self-masking.** A noise-like cell's threshold includes its own masker contribution, so it "justifies its own deletion" — delete it and the masking that excused the deletion vanishes. v3 introduced **exclusive (leave-self-out) thresholds** for deletion decisions.
3. Budgets must be matched on **bins** (≈compute), not cell counts (Bark cells have unequal width).

**v3 results (deletion operator, bin-matched budgets, PESQ-WB means over 45 utterances/model):**

| Model | Budget | energy | perceptual_excl | perceptual_incl | random |
|---|---|---|---|---|---|
| kokoro | 0.1 | **4.57** | 4.32 | 4.23 | 2.30 |
| kokoro | 0.3 | **4.12** | 3.21 | 3.15 | 1.29 |
| kokoro | 0.5 | **2.98** | 1.71 | 1.58 | 1.09 |
| piper | 0.1 | **4.64** | 4.56 | 4.54 | 2.32 |
| piper | 0.3 | **4.59** | 4.04 | 4.07 | 1.28 |
| piper | 0.5 | **4.40** | 2.69 | 2.32 | 1.09 |

All perceptual-vs-energy differences significant (Wilcoxon p < 1e-13). Noise-injection operator (v2): same direction at low budgets, but perceptual overtakes energy at B=0.7 (piper, +0.064, p=2.8e-3) — a hint that the perceptual criterion earns its keep on *noise shaping*, not deletion.

**Reading, honestly:**
- Perceptual ≫ random everywhere (the threshold map is highly informative).
- **Energy ≥ PAM-1 perceptual under PESQ for deletion at matched budgets.** If this survives better PAMs and human ears, §7.3's fallback applies (content-adaptive inference with rigorous perceptual evaluation; negative on the criterion reported as a finding).
- Reasons not to call H3 failed yet: (a) energy deleted ~32% of cells our PAM calls audible with almost no PESQ penalty — PESQ (validated against human MOS at scale) and our simplified Model-1 disagree, and the miscalibration is more plausibly ours (band-summed noise maskers are too permissive; min-over-bins is simultaneously too conservative elsewhere). (b) The exclusive-threshold safe pool is only ~23% of cells, so budgets ≥0.3 force the perceptual policy beyond its own validity claim — within-pool (B=0.1) gaps are small (0.09–0.25 PESQ). (c) PESQ-WB is band-limited (~7 kHz) and is itself only a proxy; MUSHRA remains the arbiter. (d) The deletion pool is where energy is naturally strong (quiet≈inaudible); the noise/precision pool is where energy misplaces error — and that pool is what H1 said is huge.
- **Concrete fix list for the PAM before re-running:** per-bin (not band-sum) noise maskers; recalibrated SMR offsets; ISO Model-2-grade spreading; validate the PAM itself against PESQ/ViSQOL on synthetic masked-noise probes before re-judging policies.

## 2. RQ3 — Can inaudibility be predicted pre-waveform? (mel proxy)

80-band mel-smoothed spectra → same threshold machinery → compare against ground-truth PAM decisions (30 utterances, `results/rq3_mel_proxy.json`):

| Model | Threshold RMSE | Cell-decision agreement | False-maskable | False-audible |
|---|---|---|---|---|
| piper | 2.78 dB | 96.4% | 11.4% | 0.3% |
| kokoro | 2.73 dB | 95.9% | 12.5% | 0.3% |

**Answer:** mel-resolution features carry nearly all the information (2.8 dB RMSE), but the unsafe direction (predicted-maskable, actually-audible) is 11–12% — predictive gating needs a conservative margin; draft-based verification remains the universal fallback. Reportable sub-result as pre-registered.

## 3. Mechanism A scaffolding — aligned cheap draft for Kokoro

- **Full-model int8 is NOT a valid draft:** quantization shifts the duration predictor → different output length → draft/target misalignment. (Also found: `kokoro_onnx.create()` trims output by default — comparisons must bypass it.)
- **Solution: graph surgery.** Kokoro's ONNX splits cleanly at 5 boundary tensors + style: encoder (`kokoro-enc.onnx`) and decoder (`kokoro-dec.onnx`, 213 MB = 2/3 of weights). Split pipeline is **bit-exact** vs monolithic (max abs diff 0.0).
- **Draft decoder:** dynamic-int8 decoder (`kokoro-dec-int8.onnx`, 63 MB) on shared encoder outputs → perfectly aligned. Draft quality vs fp32: SNR ≈ 9 dB, PESQ ≈ 2.5, and — the draft–verify number — **only ~2.1% of time-frequency bins carry error above the masking threshold**. The audible-error pool is small; whether it is *concentrated* enough in time for economical re-decode is the next measurement (frame-level concentration + realized wall-clock of int8 vs fp32 decoder, to be timed on an idle machine).

## 4. Next steps (priority order)

1. **PAM upgrade + self-validation** (per-bin noise maskers, SMR recalibration; probe-tone/noise validation against PESQ) — then re-run the v3 harness. H3's fate hangs here.
2. **Draft-error concentration + timing:** what fraction of frames need re-decode; int8 vs fp32 decoder wall-clock (uncontended machine).
3. **Regional re-decode prototype:** overlap-add splice fp32 re-decoded segments into the int8 draft; measure end-to-end cost vs quality (first real H2 datapoint).
4. Informal listening spot-check by owner (not evidence, but cheap direction-finding); formal MUSHRA design stays Stage 4.
5. x86 replication of RQ2/timings.

## 5. Provenance

Same environment as Stage 1 (+ `pesq` 0.0.4, `pystoi` 0.4.1, `onnx` 1.22.0). New artifacts: `models/kokoro-enc.onnx`, `models/kokoro-dec.onnx`, `models/kokoro-dec-int8.onnx`, `models/kokoro-v1.0.int8.onnx` (official release, rejected as draft due to misalignment). Logs: `results/h3_proxy_run.log`, `h3_proxy2_run.log`, `h3_proxy3_run.log`. All seeds fixed (1234); noise level −55 dBFS/bin (v2/v3); calibration 96 dB.

---

# Addendum (2026-08-16, session 2): PAM miscalibration confirmed; RQ4 and RQ2 reality checks

## A1. The smoking gun — PAM is ~30–40 dB too permissive

Noise-shaping probe (`scripts/h3_noise_shaping.py`, corrected calibration; `results/h3_noise.json`): noise allocated proportional to the PAM threshold curve must sit **Δ ≈ −30 to −40 dB below the computed thresholds** before PESQ ≥ 4.4. External anchor: LAME MP3 round-trips score PESQ 4.64 (128 kbps) and 4.54 (64 kbps) on our corpus audio — PESQ is perfectly content with noise at *real* ISO thresholds. Conclusion: our simplified Model-1 implementation inflates thresholds by tens of dB (band-summed noise maskers are the prime suspect). **This single defect explains every adverse H3 result.** All harnesses, metrics, and statistics are built; swapping in a vetted PAM (port a reference ISO 11172-3 Model-1, e.g. the TU Ilmenau Python audio-coding implementation, then re-validate with the Δ-probe until threshold-level noise scores ≥4.4 like MP3 does) re-runs everything.

Noise-shaping H3 at matched budgets (corrected): energy-proportional placement ≥ threshold-shaped placement at all NSRs (small gaps, growing with budget); both beat uniform placement by 1.5–2 PESQ. Shaping matters; our threshold's *shape* currently adds nothing beyond the signal envelope — consistent with the inflation diagnosis.

## A2. RQ4 reality check — int8 realized savings are NEGATIVE on Apple Silicon

Idle-machine timing, Kokoro decoder subgraph, 5 utterances, best of 3: fp32 3.87 s vs dynamic-int8 **18.62 s (4.8× slower)**. Dynamic-quantized convs fall off the fast path on this aarch64 build while fp32 uses AMX. The int8 draft is dead on this hardware regardless of quality; x86 (AVX-VNNI) replication is now blocking for Mechanism A. First-class RQ4 data point: operation-count savings vs wall-clock savings can have opposite signs.

## A3. RQ2 audit flag — Kokoro stage shares are suspect

Split-pipeline timing: extracted encoder subgraph ≈ 0.83 s/utt vs decoder subgraph ≈ 0.77 s/utt, though profiling attributed 95.6% of kernel time to `/decoder`; the split also runs slower than the monolithic graph. Hypotheses: (a) prosody/duration predictor nodes carry `/decoder`-scoped names (share conflates predictor + vocoder); (b) ORT optimizes the fused graph better than the subgraphs. Action: per-node audit of scope attribution + minimal-cut re-extraction before any Amdahl claim for Kokoro. Piper's `/dec` split used distinct top-level scopes and is likely robust; audit anyway.

## A4. Draft-error concentration (Mechanism A shape)

Int8-draft audible error is NOT time-concentrated: 62% of frames exceed a 0.5%-audible-bins tolerance (short bursts, ~9 frames, ~3.3 segments/s). Whole-decoder int8 is too coarse a draft for time-selective redo; draft quality must rise (selective/QDQ quantization, or fp16-class drafts) or repair must be frequency-selective.

## A5. Listening pack for informal spot-check

`results/listening/`: reference vs energy- vs perceptual-guided deletion at B=0.3/0.5 for two utterances. PESQ's verdicts (energy transparent-ish at B=0.5 on Piper; perceptual audibly damaged) can be checked by ear. Not evidence — direction-finding only.

## A6. Revised priority order

1. Port + validate a reference ISO PAM (Δ-probe target: threshold-level noise ⇒ PESQ ≥ 4.4). **Everything downstream waits on this.**
2. Re-run H3 deletion + noise-shaping harnesses with the vetted PAM.
3. RQ2 attribution audit (Kokoro scopes, split overhead).
4. x86 box for int8/mechanism timing (blocking for Mechanism A economics).
5. Then regional re-decode prototype, mixed policies, and H2.

---

# Addendum 2 (2026-08-16, session 3): vetted PAM, recalibrated H1, and a §3 checkpoint

## B1. Vetted PAM adopted and calibrated

Ported the TU Ilmenau / Schuller spreading-matrix PAM (`vendor/Python-Audio-Coder`, wrapper `scripts/pam2.py`; α=0.8 nonlinear superposition, −23.5 dB masking offset, ATH floor). Δ-probe results: raw thresholds still ~15 dB permissive vs PESQ transparency *when noise is capped codec-realistically at min(threshold, signal)* (Δ=0 → PESQ 2.83; ≥4.35 needs Δ≈−16). Residual gap attributed to missing tonality handling (fixed offset vs tonal SMR). Working model: **pam2 − 16 dB** (offset calibration; leaves rankings unchanged, sets pool sizes). MP3 anchor (PESQ 4.64 at 128 kbps) confirms PESQ itself is not the bottleneck.

## B2. H1 revised (honest existence numbers at calibrated thresholds)

| model | domain | bins below thr | frames 100% maskable | frames ≥95% |
|---|---|---|---|---|
| kokoro | all 3 | 0.113–0.117 | 0.000 | 0.000 |
| piper | all 3 | 0.285–0.297 | 0.000 | 0.000 |

The Stage-1 read ("~98% of bins free") was an artifact of the inflated PAM. Calibrated: **Kokoro sits at/below the 15% conservative kill line; Piper sits in the 15–35% band.** Zero fully-skippable frames at strict calibration (silence still carries a hair of decoder noise floor above the −16 dB-calibrated floor).

## B3. H3 deletion with vetted+calibrated PAM (exclusive thresholds)

Energy still wins everywhere (Wilcoxon p<1e-6); gaps shrink as the PAM improves and budgets fall (piper B=0.1: −0.009 PESQ ≈ tie). Third PAM variant, same ordering. Cumulative H3 verdict at proxy level, under PESQ: **the masking-threshold ranking does not beat the energy ranking for deletion-style gating; near-parity at low budgets; energy decisively better at high budgets.** Perceptual ≫ random throughout.

## B4. RQ2 audit resolved

The "encoder ≈ decoder cost" alarm was an extraction artifact: two aux boundary tensors (`onnx::Gather_6471`, `onnx::Add_6479`) have decoder ancestors (ISTFT length/index bookkeeping), pulling 1228 decoder nodes into the encoder subgraph. Profiler attribution stands: **Kokoro decoder ≈ 95.6%** (sub-scope audit: `/decoder/decoder` 95.6%, all encoder scopes ≤1.7%). Both aux tensors are derivable from the frame count in Python — noted for the production split. The int8-vs-fp32 decoder timing (4.8× slower on Apple Silicon) used the clean decoder graph and stands.

## B5. Where this leaves the pre-registered rules — decision needed (human checkpoint)

Evidence across three PAM variants and two degradation operators, all under PESQ (humans not yet consulted):
- H3-as-written (perceptual **allocator** beats energy at matched budgets) is failing at proxy level.
- H1 recalibrated straddles the kill line (model-dependent).
- Unrefuted and still promising: the masking model as **verifier** — judging whether an actual synthesis error is audible (the draft–verify–redo shape; the int8 draft's error was 98% below threshold; RQ3 showed thresholds are mel-predictable to 2.8 dB). H3's failures concern *ranking hypothetical* error placement, not *verifying actual* error.

Options for the owner (per §3, changes require sign-off logged before affected experiments):
- **(A) Human micro-check first:** listen to `results/listening/`; optionally a 15-minute informal ABX. If ears contradict PESQ on the perceptual-policy samples, the H3 conclusion reopens.
- **(B) Pre-registered amendment — pivot the criterion's role:** "energy proposes, masking verifies." H3′ becomes: a perceptual-verifier draft–verify system beats (i) SNR-verifier and (ii) verifier-free static baselines at matched compute. Keeps the listener-model novelty (Family-F verifier swap), matches the mechanism H1 favored, drops the failing allocator-ranking claim.
- **(C) §7.3 fallback as-is:** content-adaptive inference with energy criterion + rigorous perceptual evaluation; report the H3 negative.
- **(D) Kill → salvage benchmark paper.**

Recommendation: A then B (B's amendment drafted for sign-off only after the listening check).

## B6. Listening round 1 (owner, informal, 2026-08-16)

Blind pack (pam2-based, budgets 0.3/0.5 + calibrated noise): **owner reports almost every clip identical to the reference** — including pam2-guided 50% deletions PESQ scored 2.1–3.4. Direction: PESQ appears to over-penalize masked spectral deletion (its validation domain is telephony noise), i.e., the objective judge used for every adverse H3 verdict is suspect on exactly our distortion class; the PAM's "safe" judgments may have been right. Caveats: n=1, untrained, unknown playback, no forced choice. Action: round 2 pushed budgets to 60/75/90% and added MUSHRA-style hygiene (hidden reference + random-deletion anchor) to find the human transparency edge per policy and validate the listening setup. PESQ demoted to screening metric pending triangulation (NISQA/CDPAM/ViSQOL candidates); formal ABX/MUSHRA (RQ7) moves earlier in the program.

## B7. Listening round 2 (owner, blind, interactive page, 2026-09-02)

Setup: speakers, quiet volume. **Hygiene passed:** both hidden references judged "same", both random-30% anchors judged "clear" — the listener detects real damage and doesn't imagine differences. Raw data: `results/listening3/owner_round2_results.json` (collected via the self-publishing artifact page).

| Condition | Piper agent | Kokoro narration |
|---|---|---|
| del60 energy / PAM | same / same | same / same |
| del75 energy / PAM | same / same | same / slight |
| del90 energy / PAM | same / slight | slight / clear |
| anchor random-30% | clear ✓ | clear ✓ |
| hidden reference | same ✓ | same ✓ |

**Findings:** (1) Transparent-deletion pool is far larger than any model predicted — 60–75% of T-F bins deletable (quietest-first) with no perceptible difference; random placement at 30% is clearly audible, so sorted placement carries the perceptual load. (2) Human ordering corroborates PESQ/all-PAM-variant ordering: energy ≥ PAM at every budget — for deletion, signal energy is a sufficient statistic of audibility; H3-as-written fails at proxy level with human corroboration (informal, n=1, 2 utterances). (3) PESQ absolute scores are meaningless on this distortion class (scored human-indistinguishable clips 1.2–3.5); orderings held, severities did not — PESQ demoted to ordering-only screening; transparency judgments require humans or a to-be-validated metric. Caveat: quiet speaker playback is forgiving (not unlike real agent-call conditions); headphone re-run would tighten but is unlikely to flip the ordering.

**Program implication:** H2 potential is strongly resurrected (huge harvestable pool, cheap criterion suffices); H3's novelty claim must move off the allocator (per the drafted H3′ amendment: masking model as verifier, or §7.3 fallback with the energy-criterion finding reported honestly).

---

# Addendum 3 (2026-09-02): x86 replication on AWS (ephemeral c7i.2xlarge, torn down)

Host: Intel Xeon Platinum 8488C (Sapphire Rapids, AVX-VNNI), 8 vCPU, Ubuntu 24.04, ORT 1.29.0. Instance created and terminated same session; key pair + security group deleted and verified. Data: `results/x86_results.json`.

## RQ2 replicates cross-architecture (decoder dominance confirmed)
| Model | Decoder share — M5 Pro | Decoder share — Xeon 8488C |
|---|---|---|
| Piper (VITS) `/dec` | 69.5% | **63.3%** (0.506 / 0.799 s) |
| Kokoro `/decoder` | 95.6% | **93.9%** (2.95 / 3.14 s) |

The load-bearing assumption (a dominant, gateable decoder stage) holds on server silicon. Amdahl ceilings stand. Baseline RTF: Piper 0.023, Kokoro 0.194 (≈2× faster per-core than M5 Pro, as expected).

## RQ4 headline: int8 decoder is DEAD on x86 too — 8× SLOWER
fp32 decoder 4.78 s vs dynamic-int8 decoder 38.56 s for 5 utterances → **int8 speedup 0.124 (i.e. 8.06× slower)**. On Apple Silicon it was 4.8× slower; the earlier hypothesis that this was an aarch64/AMX artifact is **refuted** — dynamic INT8 quantization of this decoder is catastrophic on AVX-VNNI Intel as well. Root cause (consistent with the quantizer warnings): the ISTFTNet decoder is dominated by transposed convolutions and an ISTFT/`NonZero` block that ORT's dynamic-quant path cannot map to VNNI GEMM kernels, so it inserts per-op QuantizeLinear/DequantizeLinear around ops that still run in fp32 — pure overhead, no fast-path payoff.

**Mechanism implication:** dynamic-int8-decoder-as-draft is abandoned on both architectures. The cheap-draft path for Mechanism A/H3′ must come from something else: (a) static/QOperator quantization with a calibration set (may hit VNNI where dynamic does not), (b) an fp16 or reduced-channel decoder draft, (c) fewer-iteration/coarse decoding rather than lower precision, or (d) a genuinely smaller student decoder. This is the next fork to explore before any draft–verify timing is meaningful.

## Cost/cleanup
One c7i.2xlarge ~35 min ≈ well under $0.50. Instance i-0b68c410fc83abc14 terminated; key pair sotto-ephemeral and SG sg-02137e937a7917099 deleted; all verified absent.
