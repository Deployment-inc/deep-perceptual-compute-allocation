"""Psychoacoustic model (MPEG-1 Model 1 lineage) for masking-threshold maps.

Computes, per analysis frame, a global masking threshold across frequency
(tonal + noise maskers, spreading, absolute threshold of hearing), then
aggregates signal energy and threshold into Bark-band cells.

Calibration convention: a full-scale sinusoid (amplitude 1.0) maps to 96 dB SPL.
All thresholds are conservative: per-band threshold is the MINIMUM of the
per-bin global threshold within the band, so "below threshold" here
underestimates the true maskable fraction.
"""

import numpy as np

FRAME = 1024
HOP = 512
SPL_REF = 96.0  # dB SPL assigned to a full-scale sine
EPS = 1e-12


def bark(f_hz):
    f = np.asarray(f_hz, dtype=float)
    return 13.0 * np.arctan(0.00076 * f) + 3.5 * np.arctan((f / 7500.0) ** 2)


def ath_db(f_hz):
    """Absolute threshold of hearing (Terhardt), dB SPL. f in Hz."""
    f = np.maximum(np.asarray(f_hz, dtype=float), 20.0) / 1000.0
    return (3.64 * f ** -0.8
            - 6.5 * np.exp(-0.6 * (f - 3.3) ** 2)
            + 1e-3 * f ** 4)


def _psd_db(frame_windowed, win):
    X = np.fft.rfft(frame_windowed)
    # amplitude of a full-scale sine after windowing: sum(win)/2
    amp = np.abs(X) / (np.sum(win) / 2.0)
    return SPL_REF + 20.0 * np.log10(amp + EPS)


def _tonal_maskers(P):
    """Return (indices, levels) of tonal maskers per ISO neighborhood rules."""
    n = len(P)
    idx, lvl = [], []
    k = 3
    while k < n - 3:
        if P[k] > P[k - 1] and P[k] >= P[k + 1]:
            if k < 63:
                dks = [-2, 2]
            elif k < 127:
                dks = [-3, -2, 2, 3]
            else:
                dks = [-6, -5, -4, -3, -2, 2, 3, 4, 5, 6]
            ok = all(0 <= k + d < n and P[k] - P[k + d] >= 7.0 for d in dks)
            if ok:
                p = 10.0 * np.log10(10 ** (P[k - 1] / 10) + 10 ** (P[k] / 10)
                                    + 10 ** (P[k + 1] / 10))
                idx.append(k)
                lvl.append(p)
                k += 2
        k += 1
    return np.array(idx, dtype=int), np.array(lvl)


def _noise_maskers(P, z_bins, tonal_idx):
    """One noise masker per critical band from residual (non-tonal) energy."""
    n = len(P)
    excluded = np.zeros(n, dtype=bool)
    for k in tonal_idx:
        lo, hi = max(0, k - 3), min(n, k + 4)
        excluded[lo:hi] = True
    idx, lvl = [], []
    for b in range(int(np.ceil(z_bins.max()))):
        sel = (z_bins >= b) & (z_bins < b + 1) & (~excluded)
        if not np.any(sel):
            continue
        power = np.sum(10 ** (P[sel] / 10))
        if power <= 0:
            continue
        ks = np.where(sel)[0]
        centroid = int(ks[np.argmin(np.abs(z_bins[ks] - (b + 0.5)))])
        idx.append(centroid)
        lvl.append(10.0 * np.log10(power + EPS))
    return np.array(idx, dtype=int), np.array(lvl)


def _decimate(idx, lvl, z_bins, ath):
    """Drop sub-ATH maskers; among maskers closer than 0.5 Bark keep strongest."""
    keep = lvl >= ath[idx] if len(idx) else np.array([], dtype=bool)
    idx, lvl = idx[keep], lvl[keep]
    order = np.argsort(z_bins[idx]) if len(idx) else []
    idx, lvl = idx[order], lvl[order]
    out_i, out_l = [], []
    for i, l in zip(idx, lvl):
        if out_i and z_bins[i] - z_bins[out_i[-1]] < 0.5:
            if l > out_l[-1]:
                out_i[-1], out_l[-1] = i, l
        else:
            out_i.append(i)
            out_l.append(l)
    return np.array(out_i, dtype=int), np.array(out_l)


def _spread(dz):
    """Two-slope spreading function value (dB) at Bark distance dz (maskee-masker)."""
    sf = np.full_like(dz, -np.inf)
    m = (dz >= -3.0) & (dz < -1.0)
    sf[m] = 17.0 * dz[m] + 15.0
    m = (dz >= -1.0) & (dz < 0.0)
    sf[m] = 6.0 * dz[m]
    m = (dz >= 0.0) & (dz < 1.0)
    sf[m] = -17.0 * dz[m]
    m = (dz >= 1.0) & (dz < 8.0)
    sf[m] = -17.0 * dz[m] + 0.15 * 0 * dz[m]  # simple -17 dB/Bark upper slope
    return sf


def global_threshold(P, z_bins, ath):
    """Global masking threshold per bin (dB SPL) for one frame's PSD."""
    ti, tl = _tonal_maskers(P)
    ni, nl = _noise_maskers(P, z_bins, ti)
    ti, tl = _decimate(ti, tl, z_bins, ath)
    ni, nl = _decimate(ni, nl, z_bins, ath)
    thr_power = 10 ** (ath / 10.0)
    for idx, lvl, is_tonal in ((ti, tl, True), (ni, nl, False)):
        for k, p in zip(idx, lvl):
            dz = z_bins - z_bins[k]
            m = (dz >= -3.0) & (dz < 8.0)
            sf = _spread(dz[m])
            if is_tonal:
                t = p - 0.275 * z_bins[k] + sf - 6.025
            else:
                t = p - 0.175 * z_bins[k] + sf - 2.025
            thr_power[m] += 10 ** (t / 10.0)
    return 10.0 * np.log10(thr_power + EPS)


def add_forward_masking(thr_db, hop_ms, decay_db_per_ms=0.3, max_ms=150.0):
    """Extend simultaneous thresholds with forward (post-) masking: a bin's
    threshold cannot fall faster than `decay_db_per_ms` after a loud frame."""
    T = thr_db.copy()
    d_max = int(max_ms / hop_ms)
    for d in range(1, d_max + 1):
        drop = decay_db_per_ms * d * hop_ms
        if T.shape[0] > d:
            T[d:] = np.maximum(T[d:], thr_db[:-d] - drop)
    return T


def global_threshold_with_contrib(P, z_bins, ath, band_of_bin, n_bands):
    """Like global_threshold, but also returns each Bark band's masker power
    contribution so self-masking can be excluded per band."""
    ti, tl = _tonal_maskers(P)
    ni, nl = _noise_maskers(P, z_bins, ti)
    ti, tl = _decimate(ti, tl, z_bins, ath)
    ni, nl = _decimate(ni, nl, z_bins, ath)
    thr_power = 10 ** (ath / 10.0)
    contrib = np.zeros((n_bands, len(P)))
    for idx, lvl, is_tonal in ((ti, tl, True), (ni, nl, False)):
        for k, p in zip(idx, lvl):
            dz = z_bins - z_bins[k]
            m = (dz >= -3.0) & (dz < 8.0)
            sf = _spread(dz[m])
            if is_tonal:
                t = p - 0.275 * z_bins[k] + sf - 6.025
            else:
                t = p - 0.175 * z_bins[k] + sf - 2.025
            pw = 10 ** (t / 10.0)
            thr_power[m] += pw
            contrib[band_of_bin[k], m] += pw
    return thr_power, contrib


def analyze_band_exclusive(audio, sr, spl_ref=SPL_REF, temporal=True):
    """Band-level energies plus EXCLUSIVE thresholds: for each (frame, band),
    the masking threshold from maskers OUTSIDE that band (+ATH). This is the
    correct deletion criterion — a cell must not justify its own removal via
    the masking it itself produces.

    Returns band_energy_db [T,B], band_thr_excl_db [T,B] (min over bins).
    """
    audio = np.asarray(audio, dtype=np.float64)
    win = np.hanning(FRAME)
    n_frames = max(0, 1 + (len(audio) - FRAME) // HOP)
    freqs = np.fft.rfftfreq(FRAME, 1.0 / sr)
    z_bins = bark(freqs)
    ath = ath_db(freqs)
    n_b = int(np.ceil(z_bins.max()))
    band_of_bin = np.clip(z_bins.astype(int), 0, n_b - 1)
    cal = spl_ref - SPL_REF

    E = np.zeros((n_frames, n_b))
    Tx = np.zeros((n_frames, n_b))
    for t in range(n_frames):
        fr = audio[t * HOP: t * HOP + FRAME] * win
        P = _psd_db(fr, win) + cal
        thr_power, contrib = global_threshold_with_contrib(
            P, z_bins, ath, band_of_bin, n_b)
        pw = 10 ** (P / 10.0)
        for b in range(n_b):
            sel = band_of_bin == b
            E[t, b] = 10 * np.log10(pw[sel].sum() + EPS)
            excl = np.maximum(thr_power[sel] - contrib[b, sel], 10 ** (ath[sel] / 10.0))
            Tx[t, b] = 10 * np.log10(excl + EPS).min()
    if temporal and n_frames > 1:
        Tx = add_forward_masking(Tx, hop_ms=1000.0 * HOP / sr)
    return {"band_energy_db": E, "band_thr_excl_db": Tx, "sr": sr,
            "hop": HOP, "frame": FRAME}


def analyze(audio, sr, n_bands=None, spl_ref=SPL_REF, temporal=True):
    """Frame the signal, return dict with per-(frame, Bark-band) energy,
    threshold, and per-bin maps for figures.

    Returns dict of arrays:
      band_energy_db [T, B], band_thr_db [T, B] (min-over-bins, conservative),
      band_bins [B] (bin counts per band), psd_db [T, K], thr_db [T, K],
      freqs [K], frame_energy_db [T]
    """
    audio = np.asarray(audio, dtype=np.float64)
    win = np.hanning(FRAME)
    n_frames = max(0, 1 + (len(audio) - FRAME) // HOP)
    freqs = np.fft.rfftfreq(FRAME, 1.0 / sr)
    z_bins = bark(freqs)
    ath = ath_db(freqs)
    # Bark band edges: integer bark bands present at this sample rate
    n_b = int(np.ceil(z_bins.max())) if n_bands is None else n_bands
    band_of_bin = np.clip(z_bins.astype(int), 0, n_b - 1)
    band_bins = np.array([(band_of_bin == b).sum() for b in range(n_b)])

    psd = np.zeros((n_frames, len(freqs)))
    thr = np.zeros_like(psd)
    cal = spl_ref - SPL_REF  # shift PSD if playback calibration differs
    for t in range(n_frames):
        fr = audio[t * HOP: t * HOP + FRAME] * win
        P = _psd_db(fr, win) + cal
        psd[t] = P
        thr[t] = global_threshold(P, z_bins, ath)
    if temporal and n_frames > 1:
        thr = add_forward_masking(thr, hop_ms=1000.0 * HOP / sr)

    band_energy = np.zeros((n_frames, n_b))
    band_thr = np.zeros((n_frames, n_b))
    for b in range(n_b):
        sel = band_of_bin == b
        if not np.any(sel):
            band_energy[:, b] = -np.inf
            band_thr[:, b] = np.inf
            continue
        band_energy[:, b] = 10 * np.log10(
            np.sum(10 ** (psd[:, sel] / 10), axis=1) + EPS)
        band_thr[:, b] = thr[:, sel].min(axis=1)  # conservative
    frame_energy = 10 * np.log10(np.sum(10 ** (psd / 10), axis=1) + EPS)
    return {
        "band_energy_db": band_energy,
        "band_thr_db": band_thr,
        "band_bins": band_bins,
        "psd_db": psd,
        "thr_db": thr,
        "freqs": freqs,
        "frame_energy_db": frame_energy,
        "sr": sr,
        "hop": HOP,
        "frame": FRAME,
    }


def h1_bin_metrics(res):
    """Per-FFT-bin below-threshold fractions — the honest compute weighting.

    A bin is 'below threshold' when its PSD is under the global masking
    threshold at that bin: its content could be altered or removed without
    audible effect. Frame fully maskable = every bin below threshold.
    """
    P, T = res["psd_db"], res["thr_db"]
    below = P < T  # [frames, bins]
    n_frames = below.shape[0]
    if n_frames == 0:
        return None
    frame_below = below.mean(axis=1)
    return {
        "bin_below_frac": float(below.mean()),
        "frame_fully_maskable_frac": float((frame_below >= 0.999).mean()),
        "frame_mostly_maskable_frac_95": float((frame_below >= 0.95).mean()),
        "n_frames": int(n_frames),
        "frame_below_frac": frame_below,
    }


def h1_metrics(res):
    """Below-threshold fractions under different compute weightings."""
    E, T = res["band_energy_db"], res["band_thr_db"]
    bins_w = res["band_bins"].astype(float)
    below = E < T  # [frames, bands]
    n_frames = below.shape[0]
    if n_frames == 0:
        return None
    # 1) cell fraction, uniform per Bark band
    cell_uniform = below.mean()
    # 2) cell fraction, weighted by linear-frequency bins (how conv/iSTFT
    #    compute actually distributes across frequency)
    w = bins_w / bins_w.sum()
    cell_linear = (below * w[None, :]).sum() / n_frames
    # 3) fully maskable frames (every band below threshold) — harvestable by
    #    pure per-frame gating
    frame_full = below.all(axis=1).mean()
    # 4) headroom map for tolerance analysis
    headroom = T - E  # positive = slack
    return {
        "cell_below_frac_uniform_bark": float(cell_uniform),
        "cell_below_frac_linear_freq": float(cell_linear),
        "frame_fully_maskable_frac": float(frame_full),
        "n_frames": int(n_frames),
        "headroom_db": headroom,
    }
