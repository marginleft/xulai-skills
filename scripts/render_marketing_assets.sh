#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ASSET_DIR="$ROOT_DIR/assets"
TMP_DIR="$(mktemp -d)"

MONO_FONT="/System/Library/Fonts/SFNSMono.ttf"
SANS_FONT="/System/Library/Fonts/SFNS.ttf"

mkdir -p "$ASSET_DIR"

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

cat > "$TMP_DIR/social_terminal.txt" <<'EOF'
$ ai-tool-auditor audit
  --tool codex --days 30
tool=codex
days=30
usage_status=counted
plugins=18
agents=30
skills=177
mcps=4
recommended_skills=119
recommended_mcps=2
EOF

cat > "$TMP_DIR/frame1.txt" <<'EOF'
$ python3 scripts/ai_tool_auditor.py audit --tool codex --days 30
Scanning logs...
Discovering plugins, agents, skills, and MCP configs...
EOF

cat > "$TMP_DIR/frame2.txt" <<'EOF'
$ python3 scripts/ai_tool_auditor.py audit --tool codex --days 30
tool=codex
days=30
usage_status=counted
plugins=18
agents=30
skills=177
mcps=4
EOF

cat > "$TMP_DIR/frame3.txt" <<'EOF'
$ python3 scripts/ai_tool_auditor.py audit --tool codex --days 30
recommended_plugins=7
recommended_agents=27
recommended_skills=119
recommended_mcps=2
CSV written:
- plugins.csv
- agents.csv
- skills.csv
- mcps.csv
EOF

cat > "$TMP_DIR/frame4.txt" <<'EOF'
$ python3 scripts/ai_tool_auditor.py delete \
  --csv recommended_deletions.csv --indexes 3,8

Preview mode only
No files deleted
Review candidates first
Apply only after explicit confirmation
EOF

render_terminal_frame() {
  local textfile="$1"
  local output="$2"

  ffmpeg -y \
    -f lavfi -i "color=c=0b1020:s=1280x720:d=1" \
    -vf "
      drawgrid=width=64:height=64:thickness=1:color=white@0.05,
      drawbox=x=72:y=84:w=1136:h=552:color=111827:t=fill,
      drawbox=x=72:y=84:w=1136:h=58:color=1f2937:t=fill,
      drawbox=x=72:y=84:w=1136:h=552:color=60a5fa@0.7:t=3,
      drawtext=fontfile='${SANS_FONT}':text='AI Tool Auditor':fontcolor=white:fontsize=28:x=112:y=101,
      drawtext=fontfile='${SANS_FONT}':text='preview-first cleanup for Codex and Claude Code':fontcolor=0xb6c2d9:fontsize=18:x=112:y=133,
      drawbox=x=96:y=184:w=36:h=22:color=34d399:t=fill,
      drawtext=fontfile='${SANS_FONT}':text='safe by default':fontcolor=0xcfe4ff:fontsize=20:x=150:y=182,
      drawtext=fontfile='${MONO_FONT}':textfile='${textfile}':reload=0:fontcolor=0xdbeafe:fontsize=26:line_spacing=12:x=110:y=248
    " \
    -frames:v 1 \
    "$output" >/dev/null 2>&1
}

render_terminal_frame "$TMP_DIR/frame1.txt" "$TMP_DIR/frame-1.png"
render_terminal_frame "$TMP_DIR/frame2.txt" "$TMP_DIR/frame-2.png"
render_terminal_frame "$TMP_DIR/frame3.txt" "$TMP_DIR/frame-3.png"
render_terminal_frame "$TMP_DIR/frame4.txt" "$TMP_DIR/frame-4.png"

ffmpeg -y \
  -f lavfi -i "color=c=09111f:s=1280x640:d=1" \
  -vf "
    drawgrid=width=64:height=64:thickness=1:color=white@0.04,
    drawtext=fontfile='${SANS_FONT}':text='Audit your AI toolchain':fontcolor=white:fontsize=46:x=76:y=74,
    drawtext=fontfile='${SANS_FONT}':text='before you clean it':fontcolor=0x9ec5ff:fontsize=30:x=76:y=132,
    drawtext=fontfile='${SANS_FONT}':text='Codex / Claude Code skill for inventory, CSV export,':fontcolor=0xcbd5e1:fontsize=25:x=76:y=214,
    drawtext=fontfile='${SANS_FONT}':text='and preview-before-apply cleanup.':fontcolor=0xcbd5e1:fontsize=25:x=76:y=252,
    drawbox=x=690:y=86:w=514:h=448:color=111827:t=fill,
    drawbox=x=690:y=86:w=514:h=52:color=1f2937:t=fill,
    drawbox=x=690:y=86:w=514:h=448:color=34d399@0.75:t=3,
    drawtext=fontfile='${SANS_FONT}':text='ai-tool-auditor':fontcolor=white:fontsize=24:x=726:y=102,
    drawtext=fontfile='${MONO_FONT}':textfile='${TMP_DIR}/social_terminal.txt':reload=0:fontcolor=0xdbeafe:fontsize=20:line_spacing=10:x=718:y=164,
    drawbox=x=76:y=366:w=250:h=56:color=0f766e:t=fill,
    drawtext=fontfile='${SANS_FONT}':text='CSV + cleanup preview':fontcolor=white:fontsize=22:x=98:y=382,
    drawbox=x=76:y=442:w=220:h=56:color=1d4ed8:t=fill,
    drawtext=fontfile='${SANS_FONT}':text='safe by default':fontcolor=white:fontsize=22:x=117:y=458,
    scale=960:480
  " \
  -frames:v 1 \
  -q:v 20 \
  "$ASSET_DIR/social-preview.jpg" >/dev/null 2>&1

printf "file '%s'\n" "$TMP_DIR/frame-1.png" > "$TMP_DIR/frames.txt"
printf "duration 1.2\n" >> "$TMP_DIR/frames.txt"
printf "file '%s'\n" "$TMP_DIR/frame-2.png" >> "$TMP_DIR/frames.txt"
printf "duration 1.2\n" >> "$TMP_DIR/frames.txt"
printf "file '%s'\n" "$TMP_DIR/frame-3.png" >> "$TMP_DIR/frames.txt"
printf "duration 1.4\n" >> "$TMP_DIR/frames.txt"
printf "file '%s'\n" "$TMP_DIR/frame-4.png" >> "$TMP_DIR/frames.txt"
printf "duration 1.6\n" >> "$TMP_DIR/frames.txt"
printf "file '%s'\n" "$TMP_DIR/frame-4.png" >> "$TMP_DIR/frames.txt"

ffmpeg -y \
  -f concat -safe 0 -i "$TMP_DIR/frames.txt" \
  -vf "fps=6,scale=560:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=8[p];[s1][p]paletteuse" \
  -loop 0 \
  "$ASSET_DIR/ai-tool-auditor-demo.gif" >/dev/null 2>&1

echo "Generated:"
echo "  $ASSET_DIR/social-preview.jpg"
echo "  $ASSET_DIR/ai-tool-auditor-demo.gif"
