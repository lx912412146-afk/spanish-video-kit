"""核查语音跟读（类型“发音”）录音里的每个词：按停顿切开成品 MP3，个数要和录音稿对上；
每个词的发声时长、元音（100–1000 Hz）时长不能太短（单音节被吞掉、只剩辅音的情况），Parakeet 识别不能是空的。

    python audit_drills.py <教材目录> <识别模型目录> [录音号…]
"""
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import soxr
from scipy.signal import butter, sosfilt

MIN_TOTAL, MIN_VOWEL = 0.20, 0.14          # 秒（成品，0.85 倍语速）：单音节一般 0.22 秒以上、元音 0.16 秒以上；吞掉的只有 0.09–0.13 秒


def drills(book):
    for f in sorted((book / 'audio').glob('u*.md')):
        cur, typ, items = None, None, []
        for line in f.read_text('utf-8').split('\n') + ['### END']:
            m = re.match(r'^### (\S+)', line)
            if m:
                if cur and typ == '发音':
                    yield cur, items
                cur, typ, items = m.group(1), None, []
            elif line.startswith('- 类型：'):
                typ = line[5:].strip()
            elif line.startswith('> ') and typ == '发音':
                body = line.split(':', 1)[1].split('｜')[0]
                items += [w.strip() for w in body.split(',') if w.strip()]


def segments(a, sr):
    hop, win = int(0.01 * sr), int(0.02 * sr)
    db = 20 * np.log10(np.array([np.sqrt(np.mean(a[i:i + win] ** 2) + 1e-12) for i in range(0, len(a) - win, hop)]))
    act = db > db.max() - 45
    segs, s, gap = [], None, 0
    for i, v in enumerate(act):
        if v:
            if s is None:
                s = i
            gap = 0
        elif s is not None:
            gap += 1
            if gap >= 40:
                segs.append((s * hop, (i - gap + 1) * hop))
                s, gap = None, 0
    if s is not None:
        segs.append((s * hop, len(a)))
    return segs


def main():
    import sherpa_onnx
    d = ASR if (ASR / 'tokens.txt').exists() else next(p for p in ASR.iterdir() if p.is_dir() and 'parakeet' in p.name)
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(d / 'encoder.int8.onnx'), decoder=str(d / 'decoder.int8.onnx'), joiner=str(d / 'joiner.int8.onnx'),
        tokens=str(d / 'tokens.txt'), model_type='nemo_transducer', num_threads=4)
    bad_tracks = 0
    for tid, items in drills(BOOK):
        if only and tid not in only:
            continue
        a, sr = sf.read(BOOK / 'audio_out' / f'A2_{tid}.mp3', dtype='float32')
        a = a.mean(1) if a.ndim > 1 else a
        segs = segments(a, sr)
        sos = butter(4, [100, 1000], 'band', fs=sr, output='sos')
        flags = []
        if len(segs) != len(items):
            flags.append(f'切出 {len(segs)} 段，录音稿 {len(items)} 个')
        for w, (b, e) in zip(items, segs):
            seg = a[b:e]
            low = sosfilt(sos, seg)
            hop, win = int(0.01 * sr), int(0.02 * sr)
            le = 20 * np.log10(np.array([np.sqrt(np.mean(low[i:i + win] ** 2) + 1e-12) for i in range(0, max(1, len(low) - win), hop)]))
            vowel = (le > le.max() - 12).sum() * 0.01
            st = rec.create_stream()
            pad = np.zeros(int(0.3 * sr), np.float32)
            st.accept_waveform(16000, soxr.resample(np.concatenate([pad, seg, pad]), sr, 16000).astype(np.float32))
            rec.decode_stream(st)
            txt = st.result.text.strip()
            if (e - b) / sr < MIN_TOTAL or vowel < MIN_VOWEL or not txt.strip(' .'):
                flags.append(f'{w}：{(e - b) / sr:.2f} 秒，元音 {vowel:.2f} 秒，识别“{txt}”')
        print(('✗ ' if flags else '✓ ') + f'{tid}（{len(items)} 个）' + ('：' + '；'.join(flags) if flags else ''), flush=True)
        bad_tracks += bool(flags)
    print('全部通过' if not bad_tracks else f'{bad_tracks} 段有问题')


if __name__ == '__main__':
    BOOK, ASR = Path(sys.argv[1]), Path(sys.argv[2])
    only = set(sys.argv[3:])
    main()
