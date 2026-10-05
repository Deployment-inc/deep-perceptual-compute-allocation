# arXiv submission checklist — Sotto (cs.AI primary)

Compiled from arXiv's official pages as of 2026-09-03 (sources at the end). Items marked **ACTION** need a human before upload.

## 0. Placeholders
- None remain. The paper was reframed on 2026-10-05 as a proposal with preliminary evidence (single author; single-listener ABX pilot reported as a pilot). `\repourl` is set.

## 1. Content eligibility
- Since **31 Oct 2025**, cs.* rejects review/survey/position papers that lack prior peer review. This paper is an original empirical study with pre-registered hypotheses and measured results → **not affected**. Keep the title/abstract concrete and empirical (they are). Source: blog.arxiv.org/2025/10/31.

## 2. Generative-AI policy (important)
- AI tools may not be authors (they aren't). Significant use of generative AI must be **disclosed in the paper** — done in Acknowledgments ("Use of AI tools"). Source: blog.arxiv.org/2023/01/31; info.arxiv.org/help/moderation.
- **May 2026 enforcement:** submissions with evidence that authors did not check LLM output (non-existent references, leftover chatbot text) trigger a **one-year ban for all listed authors**. Every reference in `sotto.tex` was verified against arXiv/DOI/publisher records on 2026-09-03 (40/40 real; see `CITATIONS-VERIFIED.md`). **ACTION:** if you add any reference, verify it resolves before upload. Run the hygiene grep before uploading:
  `grep -niE "as an ai|certainly[!,]|here is (a|the) |would you like|\[insert|lorem|TODO|FIXME|\[X\]" sotto.tex`

## 3. Accounts, identity, endorsement (changed Jan 2026)
- Each author: one arXiv account under real name; affiliation "Deployment Inc." consistently. **ACTION:** the single author (A. Gupta) confirms their account; link ORCID (recommended).
- **Since 21 Jan 2026 an institutional email alone no longer grants automatic endorsement** — it also requires a prior arXiv paper in the domain. The submitting author (A. Gupta) has prior arXiv papers, so automatic endorsement applies — no action needed. (If a co-author submits instead, they would need an endorser.) eess.AS is a *separate* endorsement domain — only matters if you make eess.AS primary.
- Submitter must have company IP sign-off (the license is irrevocable; withdrawal leaves v1 visible).

## 4. Category choice and reclassification risk
- **Recommended:** primary `cs.AI`, cross-list exactly `eess.AS` and `cs.SD` (max two cross-lists; more get pruned).
- **Risk, stated plainly:** cs.AI is defined by exclusion, and arXiv's own ML-classification guide says speech application papers belong in `eess.AS`. Moderators may silently reassign the primary to eess.AS or cs.SD (1–4 day hold, no negotiation, appeals final). The abstract is written to lead with the compute-allocation decision problem to support cs.AI; accept reclassification gracefully if it happens — it does not hurt discoverability.
- Lowest-risk alternative: primary `eess.AS`, cross-list `cs.AI`, `cs.SD` (needs an eess endorser).

## 5. License
- Choose **arXiv non-exclusive license** (keeps every venue option open) unless the company wants CC BY 4.0 for maximum reuse and has checked the target venue's preprint policy. Avoid CC0 and ND variants. Irrevocable per version.

## 6. Metadata (typed into the arXiv form)
- **Title:** `Perceptual Compute Allocation for Speech Synthesis: Spend Compute Only Where Listeners Can Hear the Difference`
- **Authors:** `Aayush Gupta (Deployment Inc., CITY, COUNTRY)` — **ACTION:** fill city/country (no street/postcode).
- **Abstract (metadata field, ≤1920 characters; identical to the paper abstract, 1652 chars):**

  > Neural text-to-speech (TTS) systems spend roughly the same inference effort on every part of an utterance, even though human hearing is far more sensitive to some sounds than to others. Audio codecs have exploited this asymmetry for decades by spending bits only where listeners can notice them. We propose perceptual compute allocation: spending synthesis compute according to audibility rather than uniformly, a direction that matters most on CPU, where saved operations convert directly into latency and serving capacity. This paper presents the idea together with preliminary evidence from two CPU TTS families (VITS/HiFi-GAN and StyleTTS2/iSTFTNet), not a finished system. We find that a large fraction of time-frequency output can be removed with far less perceptual degradation when chosen by audibility than at random; that a trivial signal-energy criterion matches or beats three psychoacoustic masking-model implementations at locating removable content, so no heavyweight listener model is needed; and, in an informal single-listener blind ABX pilot, that deletion of up to 60-75% of bins was not reliably distinguishable from the original, which motivates but does not establish a transparency claim. We also report what does not work: dynamic INT8 quantization of the dominant decoder is up to 8x slower on CPU, so post-hoc precision reduction cannot realize the savings. We argue that the realization is architectural (decoders that decline to synthesize what listeners cannot hear) and outline what such decoders would require. We release tooling, corpus, listening-study instrument, and the complete harness, including negative results.

- **Comments:** `14 pages, 3 figures, 7 tables. Code, corpus, audio examples, listening-study instrument and raw measurements: https://github.com/Deployment-inc/deep-perceptual-compute-allocation . Includes negative results.` (adjust page/figure counts to the final PDF; keep the space before the period after the URL).
- **ACM class (optional):** `I.2.7; C.4`. Journal-ref/DOI: leave blank.

## 7. TeX source upload (arXiv builds from source; PDF-only is rejected)
- Upload `sotto.tex` + `figures/money_figure.png` (the only external figure). No `.bib`/`.bbl` needed — the bibliography is inline `thebibliography`.
- Select **TeX Live 2025** (arXiv default). The document uses only standard packages (no cleveref, no minted, no shell-escape, no externalized TikZ — pgfplots inline compiles fine). No `\today`. hyperref loaded explicitly (arXiv no longer injects it).
- Remove `build.log`, `preview_*.png`, `sotto.pdf` from the upload; keep the placeholder comment lines only after the values are filled.
- View and approve the arXiv-built PDF in the UI (check for `[?]` citations, missing figure).
- Announcement: cutoff 14:00 ET Mon–Fri, announced 20:00 ET. Expect a hold of 1–4 days for first-time submitters; do **not** resubmit while on hold.

## 8. Data/code availability
- Tag a GitHub release matching the arXiv version; optionally archive it on Zenodo for a DOI and cite that DOI in v2. Optionally include `results/*.json` as arXiv ancillary files (`anc/` directory).

## Sources
blog.arxiv.org/2025/10/31 (review/position rule) · blog.arxiv.org/2023/01/31 + info.arxiv.org/help/moderation (AI policy) · TechCrunch 2026-05-16 / Inside Higher Ed 2026-05-22 (one-year ban enforcement; not yet on info.arxiv.org — re-check on submission day) · blog.arxiv.org/2026/01/21 + info.arxiv.org/help/endorsement (endorsement) · info.arxiv.org/help/policies/identity_and_affiliation · info.arxiv.org/help/cross · arxiv.org/category_taxonomy · blog.arxiv.org/2019/12/05 (ML classification guide) · info.arxiv.org/help/license · info.arxiv.org/help/prep (metadata limits) · info.arxiv.org/help/submit_tex, faq/texlive, faq/mistakes (TeX) · blog.arxiv.org/2025/09/10 (TeX Live 2025) · blog.arxiv.org/2025/11/05 (.bib processing) · info.arxiv.org/help/ancillary_files · info.arxiv.org/help/availability.
