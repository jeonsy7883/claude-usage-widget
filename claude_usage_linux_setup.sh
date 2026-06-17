#!/bin/bash
# Claude 사용량 위젯 설치 스크립트 (Ubuntu)

set -e

echo "=== Claude 사용량 위젯 설치 ==="

# 1. Python 패키지 설치
echo "[1/3] Python 패키지 설치 중..."
pip3 install --user pystray pillow curl_cffi

# 2. GNOME AppIndicator 확장 안내 (트레이 아이콘 표시에 필요)
echo ""
echo "[2/3] GNOME 트레이 지원 확인 중..."
if ! gnome-extensions list 2>/dev/null | grep -q "appindicatorsupport"; then
    echo "  [!] AppIndicator 확장이 없습니다. 트레이 아이콘이 안 보일 수 있어요."
    echo "  아래 명령어로 설치하세요:"
    echo "    sudo apt install gnome-shell-extension-appindicator"
    echo "  설치 후 재부팅 또는 GNOME Shell 재시작 필요 (Alt+F2 → 'r' 입력)"
else
    echo "  [OK] AppIndicator 확장 확인됨"
fi

# 3. 자동 시작 등록
echo ""
echo "[3/3] 자동 시작 등록 중..."
AUTOSTART_DIR="$HOME/.config/autostart"
SCRIPT_PATH="$(realpath "$(dirname "$0")/claude_usage_linux.py")"
mkdir -p "$AUTOSTART_DIR"

cat > "$AUTOSTART_DIR/claude-usage.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Claude 사용량 위젯
Exec=python3 $SCRIPT_PATH
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

echo "  [OK] 자동 시작 등록: $AUTOSTART_DIR/claude-usage.desktop"

echo ""
echo "=== 설치 완료 ==="
echo "지금 바로 실행: python3 claude_usage_linux.py"
echo "다음 로그인부터 자동 시작됩니다."
