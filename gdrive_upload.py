# -*- coding: utf-8 -*-
"""
Google Drive 업로드 유틸 (Study1 대화 로그용).

지원 방식
- OAuth (권장, Shared drives 없이도 가능): 사용자의 Google Drive 용량 사용
  - GOOGLE_DRIVE_FOLDER_ID
  - GOOGLE_DRIVE_OAUTH_CLIENT_ID
  - GOOGLE_DRIVE_OAUTH_CLIENT_SECRET
  - GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN

- Service Account (Shared drives 필요할 수 있음):
  - GOOGLE_DRIVE_FOLDER_ID
  - GOOGLE_DRIVE_CREDENTIALS_JSON

get_env(key)는 st.secrets / os.getenv 를 쓰는 앱의 _get_env 함수를 넘기면 됨.
"""

import json
import os
import re
from typing import Optional, Tuple


_DRIVE_SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_oauth_credentials(get_env) -> Optional[object]:
    client_id = (get_env("GOOGLE_DRIVE_OAUTH_CLIENT_ID") or "").strip()
    client_secret = (get_env("GOOGLE_DRIVE_OAUTH_CLIENT_SECRET") or "").strip()
    refresh_token = (get_env("GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN") or "").strip()
    if not (client_id and client_secret and refresh_token):
        return None

    try:
        from google.oauth2.credentials import Credentials
    except ImportError:
        return None

    return Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=_DRIVE_SCOPES,
    )


def _get_service_account_credentials(get_env) -> Tuple[Optional[object], Optional[str]]:
    creds_json = (get_env("GOOGLE_DRIVE_CREDENTIALS_JSON") or "").strip()
    # TOML """ 사용 시 맨 앞에 줄바꿈/BOM이 붙으면 "line 2 column 1" 파싱 오류 → 제거
    creds_json = creds_json.lstrip("\n\r\t \ufeff").rstrip("\n\r\t ")
    if not creds_json:
        return None, "GOOGLE_DRIVE_CREDENTIALS_JSON 미설정"

    try:
        import google.oauth2.service_account as sa
    except ImportError as e:
        return None, f"패키지 없음: {e}. pip install google-auth google-api-python-client"

    try:
        creds_dict = json.loads(creds_json)
    except json.JSONDecodeError as e:
        err_msg = str(e)
        creds_dict = None
        if "control character" in err_msg.lower():
            fixed = creds_json.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")
            try:
                creds_dict = json.loads(fixed)
            except json.JSONDecodeError:
                pass
        if creds_dict is None and ("Expecting property name" in err_msg or "line 2 column 1" in err_msg):
            fixed = re.sub(r"^\{\s+", "{", creds_json, count=1)
            if fixed != creds_json:
                try:
                    creds_dict = json.loads(fixed)
                except json.JSONDecodeError:
                    pass
        if creds_dict is None:
            return None, (
                f"GOOGLE_DRIVE_CREDENTIALS_JSON JSON 파싱 실패: {e}. "
                "Secrets에는 JSON을 한 줄로 넣고 키 이름은 쌍따옴표(\")를 사용하세요."
            )

    try:
        return sa.Credentials.from_service_account_info(creds_dict), None
    except Exception as e:
        return None, f"서비스 계정 credentials 생성 실패: {e}"


def upload_file_to_drive(file_path: str, get_env) -> tuple:
    """
    file_path 의 파일을 설정된 Google Drive 폴더에 업로드한다.
    get_env: (key: str, default=None) -> str 형태의 함수 (예: 앱의 _get_env)
    반환: (성공 여부, 메시지)
    """
    folder_id = (get_env("GOOGLE_DRIVE_FOLDER_ID") or "").strip()
    if not folder_id:
        return False, "GOOGLE_DRIVE_FOLDER_ID 미설정"

    if not os.path.isfile(file_path):
        return False, f"파일 없음: {file_path}"

    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as e:
        return False, f"패키지 없음: {e}. pip install google-auth google-api-python-client"

    # 1) OAuth 우선 (Shared drives 없어도 사용자 Drive 용량 사용)
    oauth_creds = _get_oauth_credentials(get_env)
    if oauth_creds is not None:
        try:
            service = build("drive", "v3", credentials=oauth_creds)
            file_name = os.path.basename(file_path)
            metadata = {"name": file_name, "parents": [folder_id]}
            media = MediaFileUpload(file_path, mimetype="application/json", resumable=True)
            service.files().create(body=metadata, media_body=media, fields="id").execute()
            return True, "Google Drive 업로드 완료 (OAuth)"
        except Exception as e:
            return False, f"Google Drive 업로드 실패(OAuth): {e}"

    # 2) Service Account fallback
    sa_creds, sa_err = _get_service_account_credentials(get_env)
    if sa_creds is None:
        return False, sa_err or "Google Drive 인증 미설정"

    try:
        service = build("drive", "v3", credentials=sa_creds)
        file_name = os.path.basename(file_path)
        metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaFileUpload(file_path, mimetype="application/json", resumable=True)
        service.files().create(body=metadata, media_body=media, fields="id").execute()
        return True, "Google Drive 업로드 완료 (Service Account)"
    except Exception as e:
        return False, f"Google Drive 업로드 실패(Service Account): {e}"
