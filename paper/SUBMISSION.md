# arXiv submission checklist — Sotto (cs.AI primary)

Compiled from arXiv's official pages as of 2026-09-03 (sources at the end). Items marked **ACTION** need a human before upload.

## 0. Fill the two placeholders in `sotto.tex`
- `\newcommand{\headline}{[X]}` → the largest transparent budget from `study/analyze.py` (e.g. `75`). Also replace the dashes in Table `tab:abx` with the analyzer's table. **Do not upload with `[X]` in the abstract.**
- `\repourl` is set to https://github.com/Deployment-inc/perceptual-compute-allocation (done).

## 1. Content eligibility
- Since **31 Oct 2025**, cs.* rejects review/survey/position papers that lack prior peer review. This paper is an original empirical study with pre-registered hypotheses and measured results → **not affected**. Keep the title/abstract concrete and empirical (they are). Source: blog.arxiv.org/2025/10/31.

## 2. Generative-AI policy (important)
- AI tools may not be authors (they aren't). Significant use of generative AI must be **disclosed in the paper** — done in Acknowledgments ("Use of AI tools"). Source: blog.arxiv.org/2023/01/31; info.arxiv.org/help/moderation.
- **May 2026 enforcement:** submissions with evidence that authors did not check LLM output (non-existent references, leftover chatbot text) trigger a **one-year ban for all listed authors**. Every reference in `sotto.tex` was verified against arXiv/DOI/publisher records on 2026-09-03 (40/40 real; see `CITATIONS-VERIFIED.md`). **ACTION:** if you add any reference, verify it resolves before upload. Run the hygiene grep before uploading:
  `grep -niE "as an ai|certainly[!,]|here is (a|the) |would you like|\[insert|lorem|TODO|FIXME|\[X\]" sotto.tex`

## 3. Accounts, identity, endorsement (changed Jan 2026)
- Each author: one arXiv account under real name; affiliation "Deployment Inc." consistently. **ACTION:** all three authors create/confirm accounts; link ORCID (recommended).
- **Since 21 Jan 2026 an institutional email alone no longer grants automatic endorsement** — it also requires a prior arXiv paper in the domain. The submitting author (A. Gupta) has prior arXiv papers, so automatic endorsement applies — no action needed. (If a co-author submits instead, they would need an endorser.) eess.AS is a *separate* endorsement domain — only matters if you make eess.AS primary.
- Submitter must have written co-author consent and company IP sign-off (the license is irrevocable; withdrawal leaves v1 visible).

## 4. Category choice and reclassification risk
- **Recommended:** primary `cs.AI`, cross-list exactly `eess.AS` and `cs.SD` (max two cross-lists; more get pruned).
- **Risk, stated plainly:** cs.AI is defined by exclusion, and arXiv's own ML-classification guide says speech application papers belong in `eess.AS`. Moderators may silently reassign the primary to eess.AS or cs.SD (1–4 day hold, no negotiation, appeals final). The abstract is written to lead with the compute-allocation decision problem to support cs.AI; accept reclassification gracefully if it happens — it does not hurt discoverability.
- Lowest-risk alternative: primary `eess.AS`, cross-list `cs.AI`, `cs.SD` (needs an eess endorser).

## 5. License
- Choose **arXiv non-exclusive license** (keeps every venue option open) unless the company wants CC BY 4.0 for maximum reuse and has checked the target venue's preprint policy. Avoid CC0 and ND variants. Irrevocable per version.

## 6. Metadata (typed into the arXiv form)
- **Title:** `Neural TTS Spends Compute on What Listeners Cannot Hear: Perceptual Compute Allocation for CPU Speech Synthesis`
- **Authors:** `Aayush Gupta (Deployment Inc., CITY, COUNTRY), Jayesh Gupta (Deployment Inc., CITY, COUNTRY), Himanshu Rathore (Deployment Inc., CITY, COUNTRY)` — **ACTION:** fill city/country (no street/postcode).
- **Abstract (metadata field, ≤1920 characters; identical to the paper abstract, 1809 chars):**

  > Neural text-to-speech (TTS) systems spend roughly the same inference effort on every part of an utterance, even though human hearing is far more sensitive to some sounds than to others. Audio codecs have exploited this perceptual asymmetry for decades by spending bits only where listeners can notice them. We ask whether neural speech synthesis can do the same with compute. We study perceptual compute allocation - allocating synthesis effort according to perceptual importance rather than uniformly - on CPU TTS, where saved operations convert directly into latency and serving capacity. Across two CPU TTS families (VITS/HiFi-GAN and StyleTTS2/iSTFTNet) we find that a large fraction of time-frequency output can be removed when chosen by audibility, with far less perceptual degradation than random removal of the same amount. A pre-registered blind ABX study with 30 listeners, using hidden-reference and damaged-anchor controls, finds that [X]% of spectral bins can be removed without reliable discrimination from the original synthesis. Surprisingly, sophisticated psychoacoustic masking models are unnecessary for locating this removable content: in a pre-registered criterion test, a simple signal-energy criterion matches or outperforms three masking-model implementations at every tested budget. Removable output, however, does not automatically translate into faster inference: dynamic INT8 quantization of the dominant decoder is up to 8x slower on CPU, showing that the remaining challenge is architectural rather than perceptual. Our results point to a design direction for speech synthesis - decoders that spend compute only where listeners can perceive the difference - and we release our tooling, corpus, listening-study instrument, and the complete harness, including the negative results.

  (Replace `[X]` before upload.)
- **Comments:** `14 pages, 4 figures, 8 tables. Code, corpus, listening-study instrument and raw measurements: https://github.com/Deployment-inc/perceptual-compute-allocation . Pre-registered hypotheses; includes a negative result.` (adjust page/figure counts to the final PDF; keep the space before the period after the URL).
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
