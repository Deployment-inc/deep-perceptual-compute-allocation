# RQ1 Sweep 3 — Vision & Cross-Modality (agent report, 2026-08-15)

## Findings Table

| Work | Year/venue | Modality | What is allocated | Perceptual criterion used | Does it claim a general principle? | Threat level |
|---|---|---|---|---|---|---|
| **Foveated Diffusion: Efficient Spatially Adaptive Image and Video Generation** (Chao, Yariv, Xiao, Wetzstein — Stanford) arXiv 2603.23491 | Mar 2026, arXiv | Image + streaming video (diffusion/DiT) | Token density across the latent — high density at fovea, low in periphery; reduced denoising compute and latency | Eccentricity-dependent visual acuity (gaze-contingent foveation), validated by user preference study | Claims "a generative framework that can allocate capacity according to visual eccentricity" — a principle for generative VISION only; does NOT generalize across modalities | **HIGH** |
| **FoV-NeRF** (Deng et al.) arXiv 2103.16365 | 2022, IEEE TVCG/ISMAR | 3D neural view synthesis | Neural encoding/synthesis quality and runtime (up to 99% latency reduction) | Human visual acuity AND stereoacuity psychophysics | Perception-synthesis co-design for VR, vision-only | **HIGH** |
| **DeepFovea** (Kaplanyan et al., Meta) SIGGRAPH Asia 2019 | 2019 (lineage) | Video (GAN reconstruction) | Rendered pixel budget — GAN hallucinates periphery from <10% of pixels | Peripheral acuity falloff | No general claim; generative model exploiting perceptual sensitivity for compute/bandwidth | **MED-HIGH** (must-cite) |
| **Region-Adaptive Sampling (RAS)** (Microsoft) arXiv 2502.10389 | 2025 | Image (DiT) | Denoising-step compute per region, 2.36–2.51× speedup | Model's own attention (NOT a human perceptual model) | No | **MED** |
| **VR-Splatting** (ACM PACMCGIT 2025); **Fov-GS** (2025); **A3FR** (ICS 2025); **MetaSapiens** (ASPLOS 2025, arXiv 2407.00435) | 2024–2025 | 3D Gaussian splatting | Rendering compute: neural detail in fovea vs cheap periphery | Peripheral acuity, gaze tracking | No — foveated rendering of fixed scenes | **MED** |
| **Attention-aware Foveated Rendering** (Krajancich et al.) arXiv 2302.01368 | 2023, SIGGRAPH/TOG | Classical rendering | Shading rate | CSF + visual attention | No | **MED** (lineage) |
| **ROI-Aware Dynamic Network Quantization for Neural Video Compression** ICPR 2024 | 2024 | Neural video codec | Network bit-widths per region | ROI/saliency | No | **MED** |
| **MOBLIVE** (Tsinghua Sci & Tech 2024) | 2024 | Video super-resolution | Which regions get server-side VSR compute | Perception-critical regions | No | **MED** |
| **QDM** arXiv 2503.12015 | 2025 | Image SR (diffusion) | Mask-guided sparse diffusion compute | Detail-richness (signal, not human model) | No | **LOW-MED** |
| **SODA** arXiv 2603.07057 | CVPR 2026 | Image (DiT) | Caching/pruning schedule | Numerical sensitivity, NOT perceptual (verified) | No | **LOW** |
| **SkipVAR** arXiv 2506.08908 | 2025 | Image (visual AR) | Step/model skipping | Frequency redundancy | No | **LOW** |
| **GazeFusion** ACM TAP 2024 | 2024 | Image (diffusion) | Content attention placement, not compute | Saliency prediction | No | **LOW** |
| **Foveated Rendering Survey** (Wang et al.) arXiv 2211.07969 | 2022/23 | Rendering (survey) | Taxonomy of rendering-budget allocation by perceptual models | Acuity, CSF, metamerism | Principle stated for classical rendering only | **MED** (closest principle statement) |
| Classical lineage: Guenter 2012; Patney 2016; Tursun 2019; Walton 2021; Motion Metamers TOG 2024 | 2012–2024 | Rendering | Shading/sampling budget | Acuity, CSF, metamers | No | **LOW; mandatory citations** |

## Verdict (agent's, verbatim in substance)

The general cross-modal principle has NOT been claimed anywhere found. No position/survey paper (2022–2026) articulates "allocate generative-model inference compute according to human perceptual sensitivity" as a modality-general axis. However, the paper cannot claim to be the first instantiation of the principle in generative inference overall: **Foveated Diffusion (arXiv 2603.23491, March 2026)** explicitly allocates generative capacity by visual eccentricity in diffusion image/video generation; FoV-NeRF (2022) did the analogue for neural view synthesis. Safe framing: (a) claim the general, modality-independent principle and the audio/psychoacoustic instantiation as novel; (b) position the vision line as an independent, modality-specific convergence on the same axis. Timing risk: the Wetzstein group's framing is one abstraction step from the general claim — publish the principle framing sooner rather than later.

Mandatory vision-side citations: Guenter 2012; Patney 2016; Tursun 2019; DeepFovea 2019 (key generative precedent); Walton 2021; Wang survey 2022 (2211.07969); FoV-NeRF 2022; Krajancich 2023; VR-Splatting/Fov-GS/MetaSapiens 2025; RAS 2025 (non-perceptual contrast case); Foveated Diffusion 2026 (closest prior, vision-only).

17 search queries were run (recorded in session log), plus abstract-level verification of 2603.23491 and 2603.07057.
