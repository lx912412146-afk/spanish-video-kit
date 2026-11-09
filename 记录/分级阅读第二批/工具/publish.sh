#!/bin/zsh
# 分级阅读第二批（在终端面板里运行）：发 Release graded-reading-2（50 个视频、核查报告、SHA256SUMS），
# 提交推送文章、音频、字幕、timings.json、核查报告、改过的工具、README 和 记录/分级阅读第二批/，
# 再用 api.github.com 核对每个文件
set -euo pipefail
S="<工作区>"
KIT="$S/kit/西班牙语视频生成包（先行版）"
GH="$S/tools/gh_2.102.0_macOS_arm64/bin/gh"
G="$S/env/bin/git"
PY="$S/env/bin/python"
REPO=lx912412146-afk/spanish-video-kit
TAG=graded-reading-2
TITLE="西班牙语分级阅读第二批（A1—C1 50 篇，每篇约 1 分钟）"
W=<工作区>/gr2
REL=$W/release_full
FILES=("${(@f)$(<$W/files.txt)}")
echo "仓库文件 ${#FILES[@]} 个，Release 文件 $(ls $REL | wc -l | tr -d ' ') 个"
cd "$KIT"
if grep -lE "claude""-501|liu""xuanxuan|Application"" Support|scratch""-workspaces" "${FILES[@]}" $REL/graded-reading-2_checks.json $W/release-notes.md; then
  echo "LOCAL PATH LEFT"; exit 1
fi
(cd $REL && shasum -a 256 -c graded-reading-2-SHA256SUMS.txt | tail -3)
"$G" pull --ff-only origin main
# 1) Release
if "$GH" release view $TAG --repo "$REPO" >/dev/null 2>&1; then
  "$GH" release upload $TAG --repo "$REPO" --clobber $REL/*
  "$GH" release edit $TAG --repo "$REPO" --title "$TITLE" --notes-file $W/release-notes.md
else
  "$GH" release create $TAG --repo "$REPO" --title "$TITLE" --notes-file $W/release-notes.md $REL/*
fi
# 2) 仓库
"$G" add -- "${FILES[@]}"
"$G" status --short | head -20
if "$G" diff --cached --quiet; then
  echo "仓库里的文件没有变化，不用提交"
else
  "$G" commit -q -F $W/commit-msg.txt
  "$G" push origin main
fi
"$G" log --oneline -1
# 3) 核对
sleep 5
"$GH" api repos/$REPO/releases/tags/$TAG > $W/verify_release.json
"$GH" api "repos/$REPO/git/trees/main?recursive=1" > $W/verify_tree.json
"$PY" $W/verify_upload.py $W/verify_release.json $W/verify_tree.json "$KIT" $REL "${FILES[@]}"
echo PUBLISH_DONE
