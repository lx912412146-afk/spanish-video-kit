#!/bin/zsh
# macOS 批量生成：逐篇生成朗读音频 + 4K 视频（先运行 ./setup_mac.sh）。
#   ./batch_mac.sh                                  # 分级阅读全部 50 篇（a1_01…c1_10），音色 qwen3_M1F5_25_slow
#   ./batch_mac.sh qwen3_M1F5_25_slow a1_01 b2_03   # 指定音色和文章
# 已经生成并核查通过的（最终视频/<名>_核查.json 存在）自动跳过，中断后重新运行会接着做。
# 某篇失败不影响后面的，结果记在 西班牙语/最终视频/批量日志.txt。
# 原始合成有缓存（西班牙语/audio/_合成缓存/），只改速度、音高、停顿时重跑很快。
set -uo pipefail
KIT="${0:A:h}"
ES_ENV="${ES_ENV:-$KIT/.mac-env}"
if [[ ! -x "$ES_ENV/bin/python" ]]; then
  echo "找不到环境 $ES_ENV，请先运行 ./setup_mac.sh" >&2
  exit 1
fi
export PATH="$ES_ENV/bin:$PATH"
export PLAYWRIGHT_BROWSERS_PATH="${PLAYWRIGHT_BROWSERS_PATH:-$ES_ENV/pw-browsers}"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1

VOICE=qwen3_M1F5_25_slow
if [[ $# -gt 0 && "$1" != [a-c][1-2]_* && "$1" != es* ]]; then
  VOICE="$1"
  shift
fi
cd "$KIT"
if [[ $# -gt 0 ]]; then
  IDS=("$@")
else
  IDS=(${(f)"$(ls 西班牙语/文章 | grep -E '^[abc][12]_[0-9]{2}\.json$' | sed 's/\.json$//' | sort)"})
fi
OUT="西班牙语/最终视频"
LOG="$OUT/批量日志.txt"
mkdir -p "$OUT"
echo "== $(date '+%F %T') 开始：${#IDS} 篇，音色 $VOICE" | tee -a "$LOG"
ok=0; skip=0; fail=0
for id in $IDS; do
  name=$(python 西班牙语/tools/make_video.py "$id" --print-name 2>/dev/null) || { echo "$id ❌ 文章读不进来" | tee -a "$LOG"; fail=$((fail + 1)); continue; }
  if [[ -f "$OUT/${name:r}_核查.json" ]]; then
    echo "$id 跳过（已完成）：$name"
    skip=$((skip + 1))
    continue
  fi
  echo "== $(date '+%T') $id $name"
  if python 西班牙语/tools/check_articles.py "$id" && \
     python 西班牙语/tools/make_audio.py "$id" --voice "$VOICE" && \
     python 西班牙语/tools/make_video.py "$id" --voice "$VOICE"; then
    echo "$(date '+%T') $id ✅ $name" | tee -a "$LOG"
    ok=$((ok + 1))
  else
    echo "$(date '+%T') $id ❌ 失败（见上面的输出）" | tee -a "$LOG"
    fail=$((fail + 1))
  fi
done
echo "== $(date '+%F %T') 结束：完成 $ok，跳过 $skip，失败 $fail" | tee -a "$LOG"
[[ $fail -eq 0 ]]
