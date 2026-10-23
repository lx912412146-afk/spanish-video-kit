"""单音节的元音辨认：量元音段（发声段的后半，避开开头的辅音和过渡）的前两个共振峰，和西语女声五个元音的典型值比。
语音跟读（发音类）全部是女声。典型值按女3 在语音跟读里 90 个单音节的中位数取整（和文献里西语女声的值一致）。
只量开音节（以元音结尾：ca、que、güe）；pan、dos、hoy 这类以辅音或 y 结尾的不量。"""
import re
import unicodedata

import numpy as np
import soxr
from scipy.linalg import solve_toeplitz
from scipy.signal import butter, sosfilt

TARGETS = {'a': (900, 1650), 'e': (440, 2450), 'i': (300, 2850), 'o': (490, 1100), 'u': (320, 720)}
SR = 11025


def plain(w):
    return ''.join(c for c in unicodedata.normalize('NFD', w.lower()) if unicodedata.category(c) != 'Mn')


def target_vowel(w):
    p = plain(w)
    if len(p) > 3 or not p.isalpha() or p[-1] not in 'aeiou':
        return None
    if 'ü' in w.lower():
        return p[-1]
    p = re.sub(r'(?<=[gq])u(?=[ei])', '', p)
    vs = [c for c in p if c in 'aeiou']
    return vs[0] if len(vs) == 1 else None


def _lpc(x, order):
    r = np.correlate(x, x, 'full')[len(x) - 1:len(x) + order]
    return np.concatenate([[1.0], -solve_toeplitz(r[:-1], r[1:])])


def formants(seg, sr):
    """元音段 F1、F2 的中位数（Hz），量不出来返回 None。"""
    low = sosfilt(butter(4, [100, 1000], 'band', fs=sr, output='sos'), seg)
    hop, win = int(0.01 * sr), int(0.025 * sr)
    if len(low) < win * 3:
        return None
    e = np.array([np.sqrt(np.mean(low[i:i + win] ** 2) + 1e-12) for i in range(0, len(low) - win, hop)])
    on = np.flatnonzero(20 * np.log10(e) > 20 * np.log10(e.max()) - 10)
    if len(on) < 3:
        return None
    span = on[-1] - on[0]
    lo, hi = on[0] + span // 2, on[-1] - span // 10
    y = soxr.resample(seg.astype(np.float64), sr, SR)
    y = np.append(y[0], y[1:] - 0.97 * y[:-1])
    k, w = SR / sr, int(0.025 * SR)
    out = []
    for i in range(lo, hi + 1):
        fr = y[int(i * hop * k): int(i * hop * k) + w]
        if len(fr) < w:
            continue
        a = _lpc(fr * np.hamming(len(fr)), 12)
        r = [z for z in np.roots(a) if np.imag(z) > 0 and np.abs(z) > 0.85]   # 带宽约 < 570 Hz
        f = sorted(float(np.angle(z) * SR / (2 * np.pi)) for z in r)
        f1 = next((x for x in f if 220 <= x <= 1200), None)
        f2 = next((x for x in f if f1 and x >= f1 + 200 and 600 <= x <= 3300), None)
        if f1 and f2:
            out.append((f1, f2))
    if len(out) < 2:
        return None
    return tuple(np.median(np.array(out), axis=0))


def classify(f):
    d = {v: float(np.hypot(np.log(f[0] / t[0]), np.log(f[1] / t[1]))) for v, t in TARGETS.items()}
    return min(d, key=d.get), d


def check(text, seg, sr):
    """返回 None（不适用或量不出来）或 (对不对, 量到的 (F1, F2), 最像的元音)。"""
    v = target_vowel(text)
    if not v:
        return None
    f = formants(seg, sr)
    if f is None:
        return None
    near, d = classify(f)
    return (near == v or d[v] <= 1.3 * d[near]), f, near


def fricative_db(seg, sr):
    """词首摩擦音的强度：前 200 ms 里 3.5–11 kHz 能量的最大值减去整个词 100–1500 Hz 能量的最大值（dB）。
    [θ] 很弱（女2 的 caza、cien、zapato 约 −20 到 −37 dB），[s] 很强（约 −7 到 −17 dB），见 theta_test.py。"""
    n, h = int(0.02 * sr), int(0.005 * sr)
    nz = np.flatnonzero(np.abs(seg) > np.abs(seg).max() * 0.02)
    x = seg[nz[0]:nz[-1]] if len(nz) > n else seg
    f = np.fft.rfftfreq(n, 1 / sr)
    win = np.hanning(n)

    def band(fr, lo, hi):
        return 10 * np.log10((np.abs(np.fft.rfft(fr * win)) ** 2)[(f >= lo) & (f < hi)].sum() + 1e-12)
    frames = [x[i:i + n] for i in range(0, len(x) - n, h)]
    if len(frames) < 3:
        return None
    on = [band(fr, 3500, 11000) for fr in frames[:int(0.2 * sr / h)]]
    return float(max(on) - max(band(fr, 100, 1500) for fr in frames))


def theta_initial(w):
    """词首是 z、ce、ci（要读齿间音）"""
    p = plain(w)
    return bool(re.match(r'z|c[ei]', p))


def vowel_sec(a, sr):
    """100–1000 Hz 段能量在最大值 12 dB 以内的时长（秒），量单音节的元音有多长。"""
    low = sosfilt(butter(4, [100, 1000], 'band', fs=sr, output='sos'), a)
    hop, win = int(0.01 * sr), int(0.02 * sr)
    db = 20 * np.log10(np.array([np.sqrt(np.mean(low[i:i + win] ** 2) + 1e-12) for i in range(0, max(1, len(low) - win), hop)]))
    return round(float((db > db.max() - 12).sum() * 0.01), 3)
