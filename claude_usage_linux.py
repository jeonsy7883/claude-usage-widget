#!/usr/bin/env python3
"""Claude 사용량 시스템 트레이 모니터 (Linux)"""

import json, os, time, threading, webbrowser, datetime, subprocess
from pathlib import Path

from curl_cffi import requests as cf
import pystray
from PIL import Image, ImageDraw, ImageFont

# ── 설정 ──────────────────────────────────────────────────────────────────────
CREDS_FILE  = Path.home() / '.claude' / '.credentials.json'
REFRESH_MIN = 30

API_URL  = 'https://api.anthropic.com/v1/messages'
API_HDR  = {'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'}
API_BODY = {
    'model': 'claude-haiku-4-5-20251001',
    'max_tokens': 1,
    'messages': [{'role': 'user', 'content': '.'}]
}

# Linux 폰트 경로 우선순위
FONT_PATHS = [
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
    '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf',
]

def _find_font(size: int):
    for p in FONT_PATHS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

# ── 사용량 조회 ───────────────────────────────────────────────────────────────
def _get_token() -> str:
    if not CREDS_FILE.exists():
        raise FileNotFoundError(
            f'인증 파일 없음: {CREDS_FILE}\n'
            'Claude Code CLI 설치 후 로그인하세요: npm install -g @anthropic-ai/claude-code'
        )
    return json.loads(CREDS_FILE.read_text())['claudeAiOauth']['accessToken']

def fetch_usage() -> tuple:
    """(pct_5h, pct_7d, reset_epoch) 반환. 실패 시 예외."""
    r = cf.post(
        API_URL,
        headers={**API_HDR, 'Authorization': f'Bearer {_get_token()}'},
        json=API_BODY,
        impersonate='chrome120',
        timeout=15,
    )
    if r.status_code != 200:
        raise RuntimeError(f'API {r.status_code}: {r.text[:80]}')
    h = r.headers
    u5  = float(h.get('anthropic-ratelimit-unified-5h-utilization',  -1))
    u7  = float(h.get('anthropic-ratelimit-unified-7d-utilization',  -1))
    rst = int(h.get('anthropic-ratelimit-unified-5h-reset') or 0)
    return round(u5 * 100, 1), round(u7 * 100, 1), rst

# ── 아이콘 생성 ───────────────────────────────────────────────────────────────
def _color(pct: float):
    if pct < 0:   return (130, 130, 130, 255)
    if pct < 60:  return (72,  199, 116, 255)   # 초록
    if pct < 85:  return (255, 180,   0, 255)   # 노랑
    return             (220,  60,  60, 255)      # 빨강

def make_icon(pct: float) -> Image.Image:
    S = 64
    img  = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([1, 1, S-1, S-1], fill=(30, 30, 30, 220))
    if pct >= 0:
        draw.arc([5, 5, S-5, S-5], -90, -90 + (pct / 100) * 360,
                 fill=_color(pct), width=9)
    label = '?' if pct < 0 else f'{int(pct)}%'
    font  = _find_font(17)
    bb    = draw.textbbox((0, 0), label, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text(((S - tw) // 2, (S - th) // 2 + 1), label,
              font=font, fill=(255, 255, 255, 255))
    return img

# ── 앱 ───────────────────────────────────────────────────────────────────────
class App:
    def __init__(self):
        self.p5    = -1.0
        self.p7    = -1.0
        self.reset = 0
        self.err   = ''
        self._lock = threading.Lock()

        self.tray = pystray.Icon(
            'claude_usage', make_icon(-1), 'Claude 사용량: 로딩 중...',
            menu=pystray.Menu(
                pystray.MenuItem(self._line1, None, enabled=False),
                pystray.MenuItem(self._line2, None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem('새로고침',       self._on_refresh),
                pystray.MenuItem('Claude.ai 열기', lambda _: webbrowser.open('https://claude.ai')),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem('종료', lambda _: self.tray.stop()),
            ),
        )

    def _line1(self, _=None):
        with self._lock:
            if self.p5 < 0:
                return f'5시간 사용량: {self.err or "로딩 중..."}'
            rst = ''
            if self.reset:
                dt  = datetime.datetime.fromtimestamp(self.reset)
                rst = f'  (리셋 {dt.strftime("%H:%M")})'
            return f'5시간 사용량: {self.p5:.1f}%{rst}'

    def _line2(self, _=None):
        with self._lock:
            if self.p7 < 0:
                return '7일 사용량: 데이터 없음'
            return f'7일 누적: {self.p7:.1f}%'

    def _apply(self, p5, p7, rst, err=''):
        with self._lock:
            self.p5    = p5
            self.p7    = p7
            self.reset = rst
            self.err   = err
        self.tray.icon  = make_icon(p5)
        self.tray.title = (f'Claude {p5:.1f}% 사용 중 (5h)' if p5 >= 0
                           else f'Claude: {err or "오류"}')
        self.tray.update_menu()

    def _on_refresh(self, _=None):
        threading.Thread(target=self._do_fetch, daemon=True).start()

    def _do_fetch(self):
        try:
            p5, p7, rst = fetch_usage()
            self._apply(p5, p7, rst)
        except Exception as e:
            self._apply(-1, -1, 0, str(e)[:60])

    def _loop(self):
        while True:
            self._do_fetch()
            time.sleep(REFRESH_MIN * 60)

    def run(self):
        threading.Thread(target=self._loop, daemon=True).start()
        self.tray.run()


if __name__ == '__main__':
    App().run()
