# SOTTO — §3 Amendment 1 (signed off by owner 2026-09-02)

**Approved by:** Aayush Gupta, via interactive decision 2026-09-02, after reviewing the plain-language summary of all Stage-2 evidence and the blind listening rounds.
**Logged before any experiments under the amended hypotheses have run** (per operating rule 2 of the intent document).

## What is amended and why

**H3 (original):** "At matched compute budgets, perceptually-guided allocation outperforms energy-guided and random allocation on quality."
**Status: FAILED at proxy level, human-corroborated.** Evidence: three psychoacoustic-model variants (hand-built Model-1, exclusive-threshold variant, vetted Schuller spreading-matrix model with PESQ-calibrated offset), two degradation operators (deletion, noise injection), PESQ orderings over 90 utterances with paired Wilcoxon tests, and two blind owner listening rounds with passed hygiene checks (hidden references judged same; random anchors judged clearly damaged). In every test, energy-based ranking ≥ masking-model ranking for deletion-style gating. Reported as a first-class negative result per §3's falsification-honesty clause.

## Amended hypotheses

**H2′ (primary):** A content-adaptive CPU TTS inference system that skips or cheapens synthesis of perceptually irrelevant time–frequency content — selected by the cheap energy criterion, whose transparency at 60–75% deletion budgets is human-validated — achieves end-to-end wall-clock reduction at transparent quality. Publishability bars unchanged from §7.2 (≥25% publishable, ≥35% strong, ≥2 model families).

**H3′ (secondary, the retained perceptual claim):** In a draft–verify–redo system, a masking-model **verifier** (deciding whether an actual synthesis error is audible) catches audible errors that an SNR/energy verifier misses at matched verification budgets, and/or permits a smaller re-do pool at equal transparency. This is the Family-F "verifier swap" claim relocated from allocator to verifier. If H3′ also fails, it is reported as a negative and the paper stands on H2′.

**Additional reportable findings (already earned):** (a) PESQ's absolute severities collapse on masked-deletion distortions (human-indistinguishable clips scored 1.2–3.5) while its orderings survive — PESQ is demoted to ordering-only screening, and all transparency claims require human tests plus a to-be-validated metric battery; (b) criterion/operator matching and self-masking exclusion as methodological requirements for perceptual-gating studies; (c) the PAM calibration journey (hand-built Model-1 ~30–40 dB permissive; vetted textbook model ~15 dB permissive vs PESQ under codec-realistic capping).

## What is unchanged

- §7.4 claim discipline in full (capacity math, overhead accounting, no fabricated data, CPU-only inference claims, provenance).
- Transparency definition of §3, with the PESQ demotion noted above.
- The Stage-4 human-validation requirement (MUSHRA-style non-inferiority); owner listening rounds are direction-finding only, never paper evidence.
- Kill honesty: H2′ failing to reach §7.2 bars after mechanism building falls back to §7.3's salvage options.

## Immediate program (post-amendment)

1. **Mechanism engineering is now the critical path** (the §2.3 problem: deletable output ≠ skipped compute until installed). Candidate mechanisms, in exploration order: frame-level cheap/full decoder switching; band-limited decoding for frames with deletable upper bands; pause skipping; int8 decoder path on x86 (dead on Apple Silicon: 4.8× slower).
2. **x86 replication box is blocking** for mechanism economics and RQ2 replication.
3. H3′ verifier comparison harness (masking verifier vs SNR verifier on real mechanism errors, e.g., the aligned int8 draft).
4. Metric triangulation (NISQA/CDPAM-class) validated against the growing human-judgment set before use.
