#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로컬에서 .env(또는 환경 변수)에 넣은 Google Drive 설정이 유효한지 확인한다.

  cd /path/to/Prejudice
  python "Study 1/Scripts/verify_google_drive.py"

성공 시: OAuth 또는 Service Account 로 access_token 발급까지 확인.
실패 시: exit code 1 (메시지에 invalid_grant 등 원인 표시).
"""
import os
import sys
from pathlib import Path

# Study 1 레이아웃: gdrive_upload 는 Study 1/ 에 있음, .env 는 보통 저장소 루트
STUDY1_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(STUDY1_ROOT))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv(REPO_ROOT / ".env")

from gdrive_upload import verify_drive_credentials

ok, msg = verify_drive_credentials(os.getenv)
print(("OK — " if ok else "FAIL — ") + msg)
sys.exit(0 if ok else 1)
