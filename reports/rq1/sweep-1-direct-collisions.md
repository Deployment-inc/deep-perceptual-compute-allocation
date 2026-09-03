# RQ1 Sweep 1 — Direct Collision Search (agent report, 2026-08-15)

**Claim coordinates:** (C1) dynamic, inference-time compute allocation; (C2) perceptual-audibility criterion (psychoacoustic masking / JND); (C3) synthesis/generation task. Collision requires all three.

## Collision table

| Paper | What it does | Coords shared | Verdict | Notes |
|---|---|---|---|---|
| SPAR-K (arXiv:2603.09215, 2026) | Early exit for speech tokens in spoken LMs; fixed intermediate-layer exit with periodic full-depth refresh (~5–11% depth reduction) | C1 (scheduled, not input-dynamic), C3 | **PARTIAL** | Exit criterion is a fixed schedule, not audibility. Closest "early exit in speech generation". Must-cite + differentiate. |
| Speech Speculative Decoding (arXiv:2505.15380, Interspeech 2025) | Draft + parallel verification for AR speech synthesis, ~1.4×; follow-ons relax acceptance because discrepancies "may not perceptually affect quality" | C1, C3 | **PARTIAL** | "Perceptual" is hand-wavy token-level tolerance; no masking model. |
| Coarse-Grained Acceptance for SD in Speech (arXiv:2511.13732, 2025) | Coarse acceptance criterion for speech-token speculative decoding | C1, C3 | **PARTIAL** | Distributional, not audibility-based; gestures at perceptual interchangeability of tokens. |
| BAMU (arXiv:2608.08432, 2026) | Inference-time per-frame dynamic RVQ depth via learned marginal-utility predictor | C1 | **PARTIAL** | Allocates bits not compute; latent distortion not masking; codec not TTS. **The codec lane is drifting toward inference-time dynamic allocation — watch.** |
| VRVQ (arXiv:2506.16538, 2025) | Per-frame importance map gates RVQ stages at inference | C1 | **PARTIAL** | R-D-learned importance, not masking; bits not compute. |
| Elastic Time (arXiv:2606.27320, 2026) | Content-adaptive latent frame decimation at inference (learned skip predictor) | C1, C3 (weak) | **PARTIAL** | Criterion is reconstructability, not audibility. Nearest "dynamic temporal compute" audio paper. |
| **Acoustic Foveation (Peng et al., IEEE VR 2025)** | Psychophysical spatial-auditory-acuity model clusters unresolvable sources at render time; ~53% compute saving in sound-propagation rendering | C1, C2 (JND-style, but spatial acuity not spectral masking) | **PARTIAL** | **Closest paper in spirit**: hearing model → runtime compute saving. Domain is VR acoustic simulation, not neural TTS. Must-cite. |
| Differentiable Psychoacoustic Loss enhancement (arXiv:2608.02918, 2026) | PAQM-derived perceptual loss; 14× speedup | C2 (training only) | **PARTIAL** | Verified: speedup from static architecture, not dynamic allocation. |
| DiT-TTS layer caching (arXiv:2509.08696, 2025) | Caches transformer layer outputs across diffusion steps | C1, C3 | **PARTIAL** | Similarity criterion, not audibility. |
| EPSS/O3S step pruning (arXiv:2505.19931; RapFlow-TTS 2506.16741) | Offline near-optimal step schedules for flow-matching TTS, 4× at 7 NFE | C1 (static schedule), C3 | **PARTIAL** | One-time schedule search; no per-input audibility gating. |
| AdaDiff (ECCV 2024) / RAS (arXiv:2502.10389) | Uncertainty/attention-driven dynamic compute in diffusion | C1 | **PARTIAL** (vision) | Model attention/uncertainty, not human perception. |
| Skip-RNN SE (arXiv:2207.11108) + successors | Skips RNN updates on temporal redundancy/VAD | C1 | **PARTIAL** | Enhancement, not synthesis; no masking. |
| Distinctive Feature Codec (2505.18516) / DyCAST (2601.23174) / VFR tokenization (2509.04685) | Variable-rate tokenization by phonetic significance | C1, C2 (very weak) | **PARTIAL** | Phonetic features, not audibility masking; watch this lane. |
| MoEVC (~2021) | Sparse-gated MoE voice conversion | C1, C3 (VC) | **PARTIAL** | Learned gating, no perceptual criterion. |
| Quantization-noise masking codecs (Byun et al. ICASSP 2024-era; arXiv:2101.00054) | Masking thresholds shape quantization/losses | C2 | **PARTIAL** | Confined to bits/training. No inference-compute use found in the whole family. |
| JSQA (2507.11636), CDPAM/JND metrics | JND-based quality metrics | C2 | **NONE** | Evaluation tools, potential for our metric battery. |
| SEOFP-NET (2111.04436) | Static float compression verified against JND post-hoc | C2 (eval only) | **NONE** | Adjacent framing, no dynamic allocation. |

**Citation check on Zhen et al. 1801.09774:** all citing papers are loss-function/training-time descendants; zero inference-time-allocation directions.

## Verdict

**The lane is open.** ~22 searches (incl. arXiv API category sweeps, Interspeech/ICASSP 2024–26, citation-graph pull on 1801.09774). Every masking use in neural audio is training-time or bit-allocation; every dynamic inference mechanism in speech generation uses statistical/scheduled/similarity criteria. The one "hearing model → runtime compute" paper (Acoustic Foveation) is spatial acuity in VR rendering. The specific claim — MP3-style masking model computed at inference to gate synthesis compute — appears unclaimed. Three converging lanes to pre-empt in related work: (a) codec bit allocation going inference-time-dynamic (BAMU), (b) VFR/perceptual-significance tokenization, (c) tolerance-relaxed speculative decoding with perceptual hand-waves.

Search queries (22) recorded in session log.
