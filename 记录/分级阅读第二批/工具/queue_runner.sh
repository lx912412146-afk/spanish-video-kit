#!/bin/zsh
# 音频队列：等第一条链（C1）做完，然后按 queue.txt 的顺序逐篇合成（一次只跑一个合成进程）；queue.txt 里出现 END 且都做完就退出
set -uo pipefail
source "${0:A:h}/env.sh"
while ! grep -q AUDIO_CHAIN_DONE "$W/logs/audio_c1.log" 2>/dev/null; do sleep 30; done
touch "$W/state/queue_done.txt"
while true; do
  next=""
  for id in $(grep -v '^END$' "$W/queue.txt"); do
    grep -qx "$id" "$W/state/queue_done.txt" || { next=$id; break; }
  done
  if [[ -z $next ]]; then
    grep -qx END "$W/queue.txt" && break
    sleep 30; continue
  fi
  zsh "$W/audio_chain.sh" $next | grep -v AUDIO_CHAIN_DONE
  echo $next >> "$W/state/queue_done.txt"
done
echo QUEUE_DONE
