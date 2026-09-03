# RQ1 Sweep 2 — Adaptive/Dynamic Compute in Generative Audio (agent report, 2026-08-15)

## Findings table

| Paper | Year/venue | Mechanism | Criterion | Task | Relevance |
|---|---|---|---|---|---|
| BDDM (2203.13508) | ICLR 2022 | Learned shortened noise schedule (7 steps) | Learned, fixed at inference, not per-content | Diffusion vocoder | Static step-reduction baseline |
| FastDiff (IJCAI 2022) | 2022 | Noise-schedule predictor + time-aware convs | Learned schedule, fixed per model | TTS diffusion vocoder | Static baseline |
| SoundStorm (2305.09636) | 2023 | MaskGIT-style confidence decoding over RVQ tokens | Model confidence orders tokens; iteration count fixed | Codec-token speech | Adaptive ordering, not compute amount |
| VampNet (ISMIR 2023) | 2023 | Variable parallel-iterative decoding steps | Confidence; step count user-chosen | Music | Manual quality-compute dial |
| AdaDiff (2311.14768) | 2023 | RL policy picks instance-specific step count | Learned reward (quality vs time) | Image/video only | Closest conceptual prior for content-adaptive steps — not audio; key citation |
| DeeDiff/ASE (2408.05927) | 2023–24 | Early exit inside score network per timestep | Learned uncertainty / fixed schedule | Image diffusion | Vision-only template |
| VALL-E R (NeurIPS 2024) | 2024 | Codec-merging + monotonic alignment | Static | Codec LM TTS | Efficiency baseline |
| Multi-token + Viterbi SD (2410.13839) | ICASSP 2025 | Multi-head speculative selection | Draft-verify acceptance | Codec TTS | Strong baseline, 4–5× per-token |
| VADUSA (via 2412.00061) | 2024 | Medusa-style tree SD for AR TTS | Draft-verify | AR TTS | Baseline |
| VRVQ (2410.06016) | ICASSP 2025 (Sony) | Importance map → per-frame codebook count | R-D learned (silence gets fewer codebooks) | Codec | Closest codec-side prior: frame-level content-adaptive allocation — bits not FLOPs |
| SoundStream dropout (TASLP 2022) | 2022 | One model, any bitrate | User-chosen | Codec | Scalability context |
| SSD (2505.15380) | Interspeech 2025 | Draft + parallel verify for AR TTS | Acceptance | AR TTS | Direct baseline, 1.4× |
| Fast F5-TTS / EPSS (2505.19931) | Interspeech 2025 | Empirically pruned 7-step schedule | Fixed for all inputs | Flow-matching TTS | Must-cite contrast: explicitly NOT content-adaptive |
| **DCAR (2506.22023)** | 2025 | On-policy module varies multi-token chunk size per speech context, 2.61× | Learned policy (not perceptual) | AR codec TTS | **Strongest direct prior art: true content-adaptive synthesis compute** |
| IMPACT (2506.00736) | 2025 (Amazon) | Iterative mask-based parallel decoding | Confidence unmasking | Text-to-audio | Variable-iteration NAR baseline |
| Adaptive Slimming SE (2507.04879) | Interspeech 2025 | Dynamic network width per input | Learned utterance-level (signal-driven) | Speech enhancement | Input-adaptive width works for audio |
| Dynamic Channel Pruning SE (2412.17121) | 2024–25 | Runtime channel pruning | Input-dependent gating | Speech enhancement | Adjacent evidence |
| VARSTok (2509.04685) | AAAI 2026 | Variable-frame-rate tokenizer (clustering merges similar frames) | Feature similarity | Tokenization → SLM/TTS | Content-adaptive token budget; up to 23% fewer tokens |
| DTM-Codec (2606.29480) / DyCAST (2601.23174) | 2026 | VFR coding via dynamic masking / char-aligned tokenization / entropy | Boundary/entropy | Codec/tokenizer | Growing VFR family |
| Coarse-Grained Acceptance SD (2511.13732) | 2025 | Relaxed acceptance for acoustic tokens | Implicitly perceptual interchangeability | Speech LM | Distinguish carefully |
| SPAR-K (2603.09215) | 2026 | Fixed-layer early exit for speech tokens + periodic refresh | Static schedule | Speech+text LM | Direct early-exit prior; static criterion |
| VocalNet-MDM (2602.08607) | 2026 | Self-distilled masked diffusion | Confidence | Speech LLM | Recent baseline |
| N-vium (2605.13190) | 2026 | Mixture-of-exits, token-adaptive routing | Learned router | Text LM | Portable concept |
| MoD (2404.02258) / MoR (2507.10524) | 2024–25 | Router caps tokens per layer / recursive depth | Learned router | Text LMs | **No audio-generation instantiation exists — gap we can claim** |
| Zhen et al. psychoacoustic calibration (2101.00054 lineage) | 2020–24 | Masking-weighted losses → smaller static models | Perceptual, training-time only | Neural coding | Only place psychoacoustics meets neural audio efficiency |

## Summary (agent verdict)

(a) Synthesis-side adaptive compute exists but is sparse and recent: speculative/multi-token decoding for AR codec TTS; DCAR's dynamic chunk policy (clearest true prior art); early-exit in speech LMs (SPAR-K, static); content-adaptive token/bit budgets (VARSTok, VRVQ, VFR codecs). Diffusion/flow TTS acceleration is uniformly static. **No early-exit or frame-level dynamically pruned vocoder (HiFi-GAN/Vocos class) exists. No MoD instantiation in audio generation.**

(b) **No perceptual/audibility criterion anywhere.** Criteria found: confidence, learned routing/policy, R-D, similarity/entropy, fixed schedules. Psychoacoustic masking appears only as training-loss weighting or bit allocation.

(c) Strongest baselines for our paper: DCAR; SSD + multi-token SD; Fast F5-TTS/EPSS + BDDM (static-reduction controls); SoundStorm/IMPACT confidence decoding; SPAR-K; VARSTok/VRVQ. Plus a fixed-schedule variant of our own system as the ablation reviewers will demand.

25 search queries recorded in session log.
