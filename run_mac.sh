#!/bin/zsh
# macOS 生成：朗读音频 + 4K 逐句精读视频（先运行 ./setup_mac.sh 装好环境和模型）。
#   ./run_mac.sh es02                       # 推荐音色 qwen3_M1F5_25：先生成音频，再生成视频
#   ./run_mac.sh es02 supertonic3_M1F5_25   # 换音色（voices.json 里的名字）
#   ./run_mac.sh es02 --stills              # 只出截图（预览截图/es02/），先看画面
#   ./run_mac.sh es02 --video-only          # 音频已经生成，只做视频
# 新文章：照 西班牙语/文章/es01.json 的格式写 西班牙语/文章/<编号>.json；列举的逗号登记在 西班牙语/tools/逗号停顿.json。
# 成品：西班牙语/audio/<音色>/（MP3 + SRT）、西班牙语/最终视频/（MP4 + 核查.json）。
set -euo pipefail
KIT="${0:A:h}"
ES_ENV="${ES_ENV:-$KIT/.mac-env}"
if [[ ! -x "$ES_ENV/bin/python" ]]; then
  echo "找不到环境 $ES_ENV，请先运行 ./setup_mac.sh" >&2
  exit 1
fi
export PATH="$ES_ENV/bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$ES_ENV/pw-browsers}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

PID="${1:?用法：./run_mac.sh 文章编号 [音色名] [--stills|--video-only]}"
shift
VOICE=qwen3_M1F5_25
MODE=all
for a in "$@"; do
  case "$a" in
    --stills) MODE=stills ;;
    --video-only) MODE=video ;;
    *) VOICE="$a" ;;
  esac
done

cd "$KIT"
case $MODE in
  stills)
    python 西班牙语/tools/make_video.py "$PID" --stills --scale 1 --out "预览截图/$PID" ;;
  video)
    python 西班牙语/tools/make_video.py "$PID" --voice "$VOICE" ;;
  all)
    python 西班牙语/tools/make_audio.py "$PID" --voice "$VOICE"
    python 西班牙语/tools/make_video.py "$PID" --voice "$VOICE" ;;
esac
