#!/bin/zsh
# 逐篇合成朗读：python make_audio.py <id> --voice <A1—A2 慢速 / B1—C1 原速>；成功写 state/<id>.audio_ok，失败写 state/<id>.audio_fail
set -uo pipefail
source "${0:A:h}/env.sh"
cd "$KIT"
for id in "$@"; do
  rm -f "$W/state/$id.audio_ok" "$W/state/$id.audio_fail"
  v=$(voice_of $id)
  echo "== $(date '+%T') $id $v"
  if python 西班牙语/tools/check_articles.py $id && python 西班牙语/tools/make_audio.py $id --voice $v > "$W/logs/$id.audio.log" 2>&1; then
    touch "$W/state/$id.audio_ok"; echo "$(date '+%T') $id 音频 OK：$(tail -1 "$W/logs/$id.audio.log")"
  else
    touch "$W/state/$id.audio_fail"; echo "$(date '+%T') $id 音频失败：$(tail -2 "$W/logs/$id.audio.log")"
  fi
done
echo AUDIO_CHAIN_DONE
