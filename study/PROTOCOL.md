# Sotto ABX Listening Study — Protocol (pre-registered)

**Purpose.** Establish, with real listeners, the largest fraction of time–frequency content that can be removed from CPU-TTS output (energy-ordered deletion) without listeners being able to detect it. This is the evidence behind the paper's headline claim and replaces the single-listener pilot.

**Pre-registration.** This protocol, the analysis rules, and the transparency threshold are fixed before any participant is recruited. Log any deviation with justification before running.

## 1. Design

- **Paradigm:** ABX discrimination. Each round presents clips A, B, X; X is an exact copy of A or B; listener picks which. Chance = 50%. ABX is the standard for "can it be heard at all" claims (stricter than MOS/MUSHRA for transparency).
- **Stimuli:** 8 utterances (4 Piper, 4 Kokoro; agent, Hinglish, narration domains), level-normalized. Conditions: energy-ordered deletion at **30 / 50 / 60 / 75 / 90%** of time–frequency bins; **anchor** = random deletion at 30% (clearly audible control).
- **Per participant:** 2 practice rounds (anchor, with feedback) + 36 test rounds = 30 energy-condition rounds (6 per budget, utterances sampled without repeating an (utterance, condition) pair) + 6 anchor rounds, all shuffled. Ref/processed assignment to A/B and X randomized per round. ~10–15 minutes.
- **Hygiene:** anchors verify listener + playback can detect real damage; every clip must be played before answering; RT recorded.

## 2. Sample size and power

- **N = 30 participants** after screening (recruit ~36 to allow exclusions).
- Yields ~180 trials per condition. For a true detection rate of 50%, Wilson 95% CI half-width ≈ ±7.3 points, so a transparent condition's CI upper bound will fall ≤ 0.60 with high probability; a condition at ≥ 65% true detection is rejected as detectable with >95% power.

## 3. Screening (applied blind to condition results)

Exclude a participant if anchor accuracy < 5/6 (0.83), or median test-round RT < 1.5 s (click-through). Report the number excluded.

## 4. Pre-registered verdict rule

A condition is declared **transparent** if pooled detection accuracy is not significantly above chance (one-sided exact binomial test, p ≥ 0.05) **and** the Wilson 95% CI upper bound ≤ 0.60. Report per-condition and per-model results, accuracy with CIs, and d′. The paper's headline is the largest budget declared transparent; if none qualifies, the paper reports the detection curve honestly.

## 5. Recruitment (Prolific)

- Study title: "Short listening test: which clip is the copy?" · Duration 15 min · Reward £2.70 (≈ £10.80/hr) · Recruit 36.
- Filters: fluent English; **"Headphones" = yes** (prescreener); no hearing difficulties; desktop or mobile OK.
- Completion: participants receive the code shown on the final page (`COMPLETION_CODE` in `index.html`; set it to the code Prolific generates for the study).
- Estimated cost: 36 × £2.70 ≈ £97 + Prolific fee (~33%) ≈ **£130 total**.
- Consent text is on the study's first screen (voluntary, anonymous, answers/timings/device only, stop anytime).

## 6. Hosting

**Live instance (GitHub Pages, `gh-pages` branch of this repo):** https://deployment-inc.github.io/perceptual-compute-allocation/
Share that link directly (append `?pid=NAME` to tag a known listener, or `?PROLIFIC_PID={{%PROLIFIC_PID%}}` on Prolific). To republish after editing `study/`, push the folder's contents to the `gh-pages` branch again.

The study is a static site: `study/index.html` + `study/audio/*.wav` (10 MB), so it can also be hosted anywhere static:
- **Netlify Drop:** drag the `study/` folder onto app.netlify.com/drop → get a URL.
- **Vercel:** `vercel deploy study/` (or connect the repo).
- **S3 + static website hosting** or GitHub Pages also work.
Prolific study link: `https://<your-host>/index.html?PROLIFIC_PID={{%PROLIFIC_PID%}}` (Prolific fills the ID).

## 7. Collecting responses (choose one)

**A — Endpoint (recommended).** Create a Google Apps Script web app that appends the POST body to a Sheet:
```javascript
function doPost(e) {
  const sh = SpreadsheetApp.openById('YOUR_SHEET_ID').getSheets()[0];
  sh.appendRow([new Date(), e.postData.contents]);
  return ContentService.createTextOutput('ok');
}
```
Deploy → Web app → "Anyone" → copy the URL into `CONFIG.SUBMIT_URL` in `index.html`. Each row's second column is one participant's JSON. Export the column to `responses.jsonl` (one JSON per line).

**B — Results code.** With no endpoint, the final page shows a copyable results code; ask participants to paste it into Prolific's completion box or a Google Form. Collect the codes one per line into `codes.txt`.

## 8. Analysis

```bash
python study/analyze.py responses.jsonl     # or responses/ directory, or codes.txt
```
Prints screening summary, the per-condition table with CIs/p-values/d′ and the pre-registered verdict, and a per-model breakdown. Paste the table into §5.5 of the paper.

## 9. Timeline

Day 1: set completion code + endpoint, host, run 3 internal dry-runs. Day 2: launch on Prolific (typically fills in hours). Day 3: screen, analyze, insert the table and headline number into the paper.
