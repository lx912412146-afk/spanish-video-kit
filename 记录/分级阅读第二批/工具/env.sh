S="<工作区>"
KIT="$S/kit/西班牙语视频生成包（先行版）"
W="$S/gr2"
ASR="$S/tools/asr/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
export PATH="$S/env/bin:$PATH" PLAYWRIGHT_BROWSERS_PATH="$S/tools/pw-browsers" HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
voice_of() { case $1 in a1_*|a2_*) echo qwen3_M1F5_25_slow ;; *) echo qwen3_M1F5_25 ;; esac }
