"""pam2 — vetted psychoacoustic model wrapper (Schuller / TU Ilmenau
Python-Audio-Coder `psyacmodel.py`, MIT-licensed reference used in perceptual
coding courses; spreading-matrix model with nonlinear superposition and ATH).

Conventions (kept identical between analysis and any noise/deletion probe):
  - STFT: 1024-sample hann frames, hop 512 (same grid as pam.py / h3 harness)
  - The reference model's calibration assumes int16-scaled samples; we feed
    |FFT(win * x * 32768)| magnitudes and use its LTQ-60 quiet-threshold
    convention unchanged.
  - Returns per-bin masking-threshold MAGNITUDES thr_mag[T, K] in the same
    FFT-voltage units as the analysis magnitudes mX[T, K] (K = 513, bin 512
    copied from 511 since the reference model stops at nfft/2).

alpha: nonlinear superposition exponent (book default ~0.8).
nfilts: Bark subbands (book example 64).
"""

import sys
from pathlib import Path

import numpy as np

VENDOR = Path(__file__).parent.parent / "vendor" / "Python-Audio-Coder" / "PythonPsychoacoustics"
sys.path.insert(0, str(VENDOR))
import psyacmodel  # noqa: E402

FRAME = 1024
HOP = 512
INT16 = 32768.0


class Pam2:
    def __init__(self, sr, nfilts=64, alpha=0.8):
        self.sr = sr
        self.nfilts = nfilts
        self.alpha = alpha
        self.W = psyacmodel.mapping2barkmat(sr, nfilts, FRAME)
        self.W_inv = psyacmodel.mappingfrombarkmat(self.W, FRAME)
        spdB = psyacmodel.f_SP_dB(sr / 2.0, nfilts)
        self.sprfuncmat = psyacmodel.spreadingfunctionmat(spdB, alpha, nfilts)

    def analyze(self, audio):
        """Returns dict with mX [T,K] analysis magnitudes, thr_mag [T,K]
        masking-threshold magnitudes (same units), and bark-domain arrays."""
        x = np.asarray(audio, dtype=np.float64) * INT16
        win = np.hanning(FRAME)
        n_frames = max(0, 1 + (len(x) - FRAME) // HOP)
        K = FRAME // 2 + 1
        mX = np.zeros((n_frames, K))
        thr = np.zeros((n_frames, K))
        mXbark_all = np.zeros((n_frames, self.nfilts))
        mTbark_all = np.zeros((n_frames, self.nfilts))
        for t in range(n_frames):
            X = np.fft.rfft(x[t * HOP: t * HOP + FRAME] * win)
            m = np.abs(X)
            mX[t] = m
            mXbark = psyacmodel.mapping2bark(m, self.W, FRAME)
            mTbark = psyacmodel.maskingThresholdBark(
                mXbark, self.sprfuncmat, self.alpha, self.sr, self.nfilts)
            mT = psyacmodel.mappingfrombark(mTbark, self.W_inv, FRAME)
            thr[t, :len(mT)] = mT[:K]
            if len(mT) < K:
                thr[t, len(mT):] = mT[-1]
            mXbark_all[t] = mXbark
            mTbark_all[t] = mTbark
        return {"mX": mX, "thr_mag": thr, "mXbark": mXbark_all,
                "mTbark": mTbark_all, "n_frames": n_frames, "K": K}

    def bark_exclusive_threshold(self, mXbark):
        """Per-frame exclusive thresholds in the Bark domain: for each band b,
        the threshold produced by all OTHER bands (+ATH). mXbark: [T, B]."""
        T, B = mXbark.shape
        a = self.alpha
        contrib = mXbark ** a  # [T, B] source strengths in alpha domain
        spr_a = self.sprfuncmat ** a  # [B_src, B_dst]
        total = contrib @ spr_a  # [T, B_dst]
        excl = np.zeros((T, B, B))  # too big? B=64 -> T*4096 floats, fine
        # exclusive threshold for band b at destination d:
        #   (total[d] - contrib[b]*spr_a[b,d])^(1/a), evaluated at d = b
        out = np.zeros((T, B))
        for b in range(B):
            v = np.maximum(total[:, b] - contrib[:, b] * spr_a[b, b], 0.0)
            out[:, b] = v ** (1.0 / a)
        # ATH floor, same convention as reference
        import numpy as _np
        maxbark = psyacmodel.hz2bark(self.sr / 2.0)
        barks = _np.arange(B) * maxbark / (B - 1)
        f = psyacmodel.bark2hz(barks) + 1e-6
        LTQ = _np.clip((3.64 * (f / 1000.) ** -0.8
                        - 6.5 * _np.exp(-0.6 * (f / 1000. - 3.3) ** 2.)
                        + 1e-3 * ((f / 1000.) ** 4.)), -20, 120)
        ath = 10.0 ** ((LTQ - 60) / 20)
        return np.maximum(out, ath[None, :])
