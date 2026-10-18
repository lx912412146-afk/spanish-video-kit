"""西班牙语用的响度检查（铁律 2 的四项，上限不变，见 gaokao_tts.LIMITS）。

和高考原版 gaokao_tts.verify_loudness 只有一处不同：3 秒短时响度波动只统计**朗读范围内**（第一句开始 → 最后一句结束）的窗口。
原版的窗口从 0 秒滑到结尾，会把铁律规定的片头 1.5 秒、结尾 2 秒静音算进“朗读响度的起伏”：首尾窗口一半是静音，比正文低 3–5 LU。
分级阅读的短文（A1 每句 2–4 秒、全篇不到 1 分钟）首尾窗口占比大，原模板原速原调也有约三分之一过不了（a1_01 1.09、a2_02 1.09）。
片头、结尾静音另有“开头静音 1.5 秒”“结尾静音 2 秒”两项单独核查。2026-10-18 用户确认改用这个测法。
原测法的数值仍然算出来，记在 short_term_std_full_lu（只记录，不判定）。
"""
import io

import numpy as np

LIMITS = {'integrated': 0.7, 'sentence_dev': 2.0, 'short_term_std': 1.0, 'peak_db': -1.0}   # 与 gaokao_tts.LIMITS 相同


def verify(mp3_bytes, items, target_lufs):
    import pyloudnorm as pyln
    import soundfile as sf
    a, sr = sf.read(io.BytesIO(mp3_bytes), dtype='float64')
    if a.ndim > 1:
        a = a.mean(1)
    m = pyln.Meter(sr)
    il = m.integrated_loudness(a)
    sent = []
    for it in items:
        seg = a[int(it['start'] * sr):int(it['end'] * sr)]
        if len(seg) > 0.5 * sr:
            sent.append(m.integrated_loudness(seg))
    med = float(np.median(sent))
    dev = max(abs(x - med) for x in sent)
    f = a.copy()
    for flt in m._filters.values():
        f = flt.apply_filter(f)
    W, H = 3 * sr, sr // 2

    def short_term(lo, hi):
        st = np.array([-0.691 + 10 * np.log10(np.mean(f[i:i + W] ** 2) + 1e-12) for i in range(lo, hi - W + 1, H)])
        return st[st > il - 10]

    full = short_term(0, len(f) - 1)                                   # 原版：从 0 秒到结尾
    lo, hi = int(items[0]['start'] * sr), int(items[-1]['end'] * sr)
    span = short_term(lo, hi) if hi - lo >= W else full                # 只看朗读范围
    peak = 20 * np.log10(np.max(np.abs(a)) + 1e-12)
    rep = {'integrated_lufs': round(float(il), 2), 'sentence_max_dev_lu': round(float(dev), 2),
           'short_term_std_lu': round(float(span.std()), 2), 'short_term_std_full_lu': round(float(full.std()), 2),
           'peak_dbfs': round(float(peak), 2)}
    errs = []
    if abs(il - target_lufs) > LIMITS['integrated']:
        errs.append(f'整体响度 {il:.2f} LUFS（目标 {target_lufs}）')
    if dev > LIMITS['sentence_dev']:
        errs.append(f'句间响度偏差 {dev:.2f} LU（上限 {LIMITS["sentence_dev"]}）')
    if span.std() > LIMITS['short_term_std']:
        errs.append(f'短时响度波动（朗读范围内） {span.std():.2f} LU（上限 {LIMITS["short_term_std"]}）')
    if peak > LIMITS['peak_db']:
        errs.append(f'峰值 {peak:.2f} dBFS（上限 {LIMITS["peak_db"]}）')
    return rep, errs
