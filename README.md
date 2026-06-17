# Claude 사용량 위젯

Claude Code의 **5시간 사용량**과 **7일 누적 사용량**을 시스템 트레이에서 실시간으로 확인하는 위젯입니다.  
Windows와 Ubuntu(Linux) 환경을 모두 지원합니다.

## 기능

- 시스템 트레이 아이콘에 현재 사용량(%) 실시간 표시
- 색상으로 사용량 단계 구분 — 초록(60% 미만) / 노랑(85% 미만) / 빨강(85% 이상)
- 30분마다 자동 갱신 + 수동 새로고침 메뉴
- 5시간 제한 리셋 시각 표시
- Claude.ai 바로 열기

## 사전 요구사항

**Claude Code CLI가 설치되어 있고 로그인된 상태**여야 합니다.  
인증 파일(`~/.claude/.credentials.json`)이 없으면 동작하지 않습니다.

```bash
# Claude Code CLI 설치 (없는 경우)
npm install -g @anthropic-ai/claude-code
claude  # 로그인
```

---

## Windows 설치

### 방법 1 — EXE 직접 실행 (Python 불필요)

1. [Releases](../../releases/latest) 페이지에서 `claude_usage.exe` 다운로드
2. 원하는 폴더에 저장 후 실행

**시작 프로그램 등록 (선택)**  
`Claude 사용량 시작.vbs`를 같은 폴더에 두고, 아래 경로에 바로가기를 만들어 두세요:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

### 방법 2 — Python으로 직접 실행

```powershell
pip install pystray pillow curl_cffi
python claude_usage.py
```

### 방법 3 — EXE 직접 빌드

```powershell
pip install pyinstaller pystray pillow curl_cffi
pyinstaller claude_usage.spec
# 빌드 결과: dist\claude_usage.exe
```

---

## Ubuntu (Linux) 설치

```bash
chmod +x claude_usage_linux_setup.sh
./claude_usage_linux_setup.sh
python3 claude_usage_linux.py
```

설치 스크립트가 자동으로 수행하는 작업:
- Python 패키지 설치 (`pystray`, `pillow`, `curl_cffi`)
- GNOME AppIndicator 확장 설치 안내
- 로그인 시 자동 시작 등록 (`~/.config/autostart/`)

> **Wayland 환경**: 트레이 아이콘이 보이지 않을 경우 GNOME 확장 `AppIndicator and KStatusNotifierItem Support`를 설치하세요.  
> ```bash
> sudo apt install gnome-shell-extension-appindicator
> ```
> 설치 후 재로그인 또는 `Alt+F2` → `r` 로 GNOME Shell 재시작.
