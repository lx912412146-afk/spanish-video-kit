"""用 Supertonic 3 的一个说话人合成克隆用的参考录音（女4 等新声音）：
python make_ref_voice.py <工具包目录> <输出 wav> <说话人，如 F3> [另一个说话人 比例 …]

A1、A2 的 ref_F2、ref_F5、ref_M5 都是这样做的：Supertonic 读 Qwen3 克隆配置里的 ref_text（约 8 秒），
再由 make_tracks.py 用这段录音克隆出声音。
"""
import sys
from pathlib import Path

import soundfile as sf

KIT, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
spk = sys.argv[3:]
mix = {spk[0]: 1.0} if len(spk) == 1 else {spk[i]: float(spk[i + 1]) for i in range(0, len(spk), 2)}
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = OUT.parent / '_ref_cache'
cfg = dict(MA.VOICES['supertonic3_M1F5_25'], mix=mix, label=f'Supertonic 3 {mix}')
text = MA.VOICES['qwen3_M1F5_25']['ref_text']
(a, sr), = MA.Worker(cfg).synth_all([text])
sf.write(OUT, a, sr)
print(OUT, round(len(a) / sr, 2), '秒', mix)
