# Audio examples

Listen for yourself. Each row is one synthesized utterance. `original` is the untouched TTS output; the `energy N%` clips have the quietest N% of time-frequency bins deleted (energy-ordered removal); `random 30%` deletes 30% of bins at random and is the clearly damaged control.

Use headphones. GitHub plays `.wav` files in the browser when you click them. The same clips power the blind ABX test at https://deployment-inc.github.io/deep-perceptual-compute-allocation/ .

| Model | Text | original | energy 30% | energy 50% | energy 60% | energy 75% | energy 90% | random 30% (control) |
|---|---|---|---|---|---|---|---|---|
| piper | Sure - your order 4 8 2 ships Tuesday. | [wav](piper_agent0_ref.wav) | [wav](piper_agent0_e30.wav) | [wav](piper_agent0_e50.wav) | [wav](piper_agent0_e60.wav) | [wav](piper_agent0_e75.wav) | [wav](piper_agent0_e90.wav) | [wav](piper_agent0_anchor.wav) |
| piper | Haan ji, main aapki kya help kar sakta hoon? | [wav](piper_hinglish1_ref.wav) | [wav](piper_hinglish1_e30.wav) | [wav](piper_hinglish1_e50.wav) | [wav](piper_hinglish1_e60.wav) | [wav](piper_hinglish1_e75.wav) | [wav](piper_hinglish1_e90.wav) | [wav](piper_hinglish1_anchor.wav) |
| kokoro | The old clock in the hallway struck nine, and the house settled into the particular silence that comes only after everyone has gone to bed. | [wav](kokoro_narration5_ref.wav) | [wav](kokoro_narration5_e30.wav) | [wav](kokoro_narration5_e50.wav) | [wav](kokoro_narration5_e60.wav) | [wav](kokoro_narration5_e75.wav) | [wav](kokoro_narration5_e90.wav) | [wav](kokoro_narration5_anchor.wav) |
| kokoro | Thanks for calling. How can I help you today? | [wav](kokoro_agent1_ref.wav) | [wav](kokoro_agent1_e30.wav) | [wav](kokoro_agent1_e50.wav) | [wav](kokoro_agent1_e60.wav) | [wav](kokoro_agent1_e75.wav) | [wav](kokoro_agent1_e90.wav) | [wav](kokoro_agent1_anchor.wav) |

These are a subset of `study/audio/` (8 utterances). Clips are level-normalized 16-bit PCM. How they were generated: `scripts/` (deletion harness) and Section 4 of the paper.

What to expect: the paper's evidence that the low budgets are hard to tell apart is preliminary (a single-listener pilot), so treat your own ears as data. The random-deletion control should sound obviously damaged.
