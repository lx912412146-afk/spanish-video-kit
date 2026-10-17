#!/bin/zsh
# macOS 一键安装：运行环境 + 两个模型，全部从网上取回（conda-forge、PyPI、本仓库的 Release），不用管理员密码。
#   curl -L https://github.com/lx912412146-afk/spanish-video-kit/archive/refs/heads/main.tar.gz | tar -xz
#   cd spanish-video-kit-main && zsh setup_mac.sh
# （用 .tar.gz，不要用 .zip：macOS 自带的 unzip 解压 GitHub 的 zip 时中文文件名会出错）
# 装好后生成视频：./run_mac.sh es02
# 磁盘：环境约 3 GB，模型约 4.4 GB，合并模型分卷时临时再多占约 4.5 GB。可以重复运行，做完的步骤会跳过。
# 在 Apple 芯片的 Mac（arm64，16 GB 内存）上测试通过；版本号固定为 2026-10-17 测试时的版本。
set -euo pipefail
KIT="${0:A:h}"
REL="https://github.com/lx912412146-afk/spanish-video-kit/releases/download/es-kit-preview"
MM_REL="https://github.com/mamba-org/micromamba-releases/releases/download/2.9.0-0"
ES_ENV="${ES_ENV:-$KIT/.mac-env}"
DL="$KIT/.mac-downloads"
M="$KIT/西班牙语/models"
case "$(uname -m)" in
  arm64) PLAT=osx-arm64 ;;
  x86_64) PLAT=osx-64 ;;
  *) echo "不支持的 CPU：$(uname -m)" >&2; exit 1 ;;
esac
mkdir -p "$DL" "$M"

sha_ok() {  # sha_ok 文件名：按 SHA256SUMS.txt 核对 $DL 里的文件
  (cd "$DL" && grep -E " $1\$" SHA256SUMS.txt | shasum -a 256 -c - >/dev/null 2>&1)
}
fetch() {   # fetch 文件名：从本仓库 Release 下载到 $DL（已下载且校验通过就跳过，断了可以续传）
  sha_ok "$1" && return 0
  echo "== 下载 $1"
  curl -fL --retry 5 --retry-delay 5 -C - -o "$DL/$1" "$REL/$1" || curl -fL --retry 5 -o "$DL/$1" "$REL/$1"
  sha_ok "$1" || { echo "$1 校验失败，删掉后请重新运行" >&2; rm -f "$DL/$1"; exit 1; }
}

# 1. micromamba（conda-forge 的单文件安装器，固定 2.9.0）
MM="$DL/micromamba"
if [[ ! -x "$MM" ]]; then
  echo "== 下载 micromamba 2.9.0"
  curl -fsSL -o "$MM" "$MM_REL/micromamba-$PLAT"
  want=$(curl -fsSL "$MM_REL/micromamba-$PLAT.sha256" | awk '{print $1}')
  got=$(shasum -a 256 "$MM" | awk '{print $1}')
  [[ "$want" == "$got" ]] || { echo "micromamba 校验失败" >&2; rm -f "$MM"; exit 1; }
  chmod +x "$MM"
fi

# 2. Python 环境：Python 3.11 + PyTorch（CPU）+ ffmpeg/ffprobe（conda-forge）
PY="$ES_ENV/bin/python"
if [[ ! -x "$PY" ]]; then
  echo "== 建 Python 环境 $ES_ENV"
  MAMBA_ROOT_PREFIX="$DL/mamba" "$MM" create -y -p "$ES_ENV" -c conda-forge --override-channels \
    python=3.11 pytorch=2.13.0 torchaudio=2.11.0 numpy=2.4.6 scipy=1.17.1 ffmpeg=9.0.2 git
fi

# 3. Python 库（PyPI，版本固定）。qwen-tts 用 --no-deps：它声明的 gradio 等界面依赖用不到
echo "== 安装 Python 库"
"$PY" -m pip install -q --disable-pip-version-check \
  soundfile==0.14.0 soxr==1.1.0 pyloudnorm==0.2.0 lameenc==1.9.0 num2words==0.5.14 playwright==1.64.0 \
  transformers==4.57.3 accelerate==1.12.0 librosa==0.11.0 onnxruntime==1.31.0 einops==0.8.2 sox==1.5.0 \
  sherpa-onnx==1.13.8
"$PY" -m pip install -q --disable-pip-version-check --no-deps qwen-tts==0.1.1

# 4. 截图用的 Chromium（放在环境里）
echo "== 安装 Chromium"
PLAYWRIGHT_BROWSERS_PATH="$ES_ENV/pw-browsers" "$PY" -m playwright install chromium

# 5. 模型（本仓库 Release：Qwen3-TTS 1.7B 分卷 + 工具包里的 Supertonic 3）
curl -fsSL -o "$DL/SHA256SUMS.txt" "$REL/SHA256SUMS.txt"
if [[ ! -f "$M/qwen3-base/model.safetensors" || ! -f "$M/qwen3-base/speech_tokenizer/model.safetensors" ]]; then
  parts=(${(f)"$(grep -oE 'qwen3-tts-1\.7b-base\.zip\.[0-9]{3}' "$DL/SHA256SUMS.txt" | sort -u)"})
  for f in $parts; do fetch "$f"; done
  echo "== 合并并解压 Qwen3-TTS 模型"
  cat "${parts[@]/#/$DL/}" > "$DL/qwen3-tts-1.7b-base.zip"
  sha_ok qwen3-tts-1.7b-base.zip || { echo "合并后的模型校验失败" >&2; rm -f "$DL/qwen3-tts-1.7b-base.zip"; exit 1; }
  unzip -q -o "$DL/qwen3-tts-1.7b-base.zip" -d "$M"
  rm -f "$DL/qwen3-tts-1.7b-base.zip" "${parts[@]/#/$DL/}"
fi
if [[ ! -f "$M/supertonic3/tts.json" ]]; then
  fetch SPANISH-video-kit-preview.zip
  echo "== 解压 Supertonic 3 模型"
  mkdir -p "$M/supertonic3"
  unzip -q -o -j "$DL/SPANISH-video-kit-preview.zip" '*/models/supertonic3/*' -d "$M/supertonic3"
fi

# 6. 自检
"$PY" -c "import qwen_tts, sherpa_onnx, playwright, soundfile, soxr, pyloudnorm, lameenc, num2words" 2>/dev/null
"$ES_ENV/bin/ffmpeg" -version >/dev/null
"$ES_ENV/bin/ffprobe" -version >/dev/null
echo "安装完成。生成视频：./run_mac.sh es02（推荐音色 qwen3_M1F5_25；先看画面：./run_mac.sh es02 --stills）"
