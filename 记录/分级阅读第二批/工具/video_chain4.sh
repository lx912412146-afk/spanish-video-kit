#!/bin/zsh
# （第四条：返工的几篇和改版式之前做的视频重做；每篇等音频队列 queue_done.txt 里有它）按顺序等每篇的音频做完，再生成视频（读 timings.json 偶尔撞上正在写，失败就等 20 秒重试，最多 3 次），然后逐句识别核对
set -uo pipefail
source "${0:A:h}/env.sh"
cd "$KIT"
for id in "$@"; do
  rm -f "$W/state/$id.video_ok" "$W/state/$id.video_fail" "$W/state/$id.asr_ok" "$W/state/$id.asr_fail"
  while ! grep -qx "$id" "$W/state/queue_done.txt" 2>/dev/null; do sleep 20; done
  if [[ -f "$W/state/$id.audio_fail" ]]; then echo "$(date '+%T') $id 跳过（音频失败）"; continue; fi
  v=$(voice_of $id)
  ok=0
  for try in 1 2 3; do
    if python 西班牙语/tools/make_video.py $id --voice $v > "$W/logs/$id.video.log" 2>&1; then ok=1; break; fi
    sleep 20
  done
  if [[ $ok == 1 ]]; then
    touch "$W/state/$id.video_ok"; echo "$(date '+%T') $id 视频 OK：$(grep -o '时长 [0-9.]* 秒' "$W/logs/$id.video.log" | tail -1)"
  else
    touch "$W/state/$id.video_fail"; echo "$(date '+%T') $id 视频失败：$(tail -2 "$W/logs/$id.video.log")"; continue
  fi
  if python 西班牙语/tools/asr_check_reading.py . "$ASR" $v $id > "$W/logs/$id.asr.log" 2>&1; then
    touch "$W/state/$id.asr_ok"; echo "$(date '+%T') $id 识别核对全部对上"
  else
    touch "$W/state/$id.asr_fail"; echo "$(date '+%T') $id 识别核对有出入：$(grep -c '^✗' "$W/logs/$id.asr.log") 句"
  fi
done
echo VIDEO_CHAIN_DONE
