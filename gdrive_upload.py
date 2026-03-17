# -*- coding: utf-8 -*-
"""
Google Drive 업로드 유틸 (Study1 대화 로그용).
GOOGLE_DRIVE_FOLDER_ID, GOOGLE_DRIVE_CREDENTIALS_JSON 이 설정된 경우에만 업로드 시도.
get_env(key) 는 st.secrets / os.getenv 를 쓰는 앱의 _get_env 함수를 넘기면 됨.
"""

import json
import os
import re


def upload_file_to_drive(file_path: str, get_env) -> tuple:
    """
    file_path 의 파일을 설정된 Google Drive 폴더에 업로드한다.
    get_env: (key: str, default=None) -> str 형태의 함수 (예: 앱의 _get_env)
    반환: (성공 여부, 메시지)
    """
    folder_id = (get_env("GOOGLE_DRIVE_FOLDER_ID") or "").strip()
    creds_json = (get_env("GOOGLE_DRIVE_CREDENTIALS_JSON") or "").strip()
    # TOML """ 사용 시 맨 앞에 줄바꿈/BOM이 붙으면 "line 2 column 1" 파싱 오류 → 제거
    creds_json = creds_json.lstrip("\n\r\t \ufeff").rstrip("\n\r\t ")
    if not folder_id or not creds_json:
        return False, "GOOGLE_DRIVE_FOLDER_ID 또는 GOOGLE_DRIVE_CREDENTIALS_JSON 미설정"

    if not os.path.isfile(file_path):
        return False, f"파일 없음: {file_path}"

    try:
        import google.oauth2.service_account as sa
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError as e:
        return False, f"패키지 없음: {e}. pip install google-auth google-api-python-client"

    try:
        creds_dict = json.loads(creds_json)
    except json.JSONDecodeError as e:
        err_msg = str(e)
        creds_dict = None
        # "Invalid control character" = private_key 안에 실제 줄바꿈 → 되돌려서 재시도
        if "control character" in err_msg.lower():
            fixed = creds_json.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")
            try:
                creds_dict = json.loads(fixed)
            except json.JSONDecodeError:
                pass
        # "Expecting property name... line 2 column 1" = """ 다음 줄바꿈으로 { 뒤에 빈 줄/공백 들어간 경우
        if creds_dict is None and ("Expecting property name" in err_msg or "line 2 column 1" in err_msg):
            fixed = re.sub(r"^\{\s+", "{", creds_json, count=1)
            if fixed != creds_json:
                try:
                    creds_dict = json.loads(fixed)
                except json.JSONDecodeError:
                    pass
        if creds_dict is None:
            return False, (
                f"GOOGLE_DRIVE_CREDENTIALS_JSON JSON 파싱 실패: {e}. "
                "Streamlit Secrets에는 JSON 전체를 한 줄로 넣고, 키 이름은 쌍따옴표(\")로 적어주세요. "
                "여러 줄로 넣을 때는 """ 다음 줄바꿈 없이 바로 { 부터 적어보세요."
            )

    try:
        credentials = sa.Credentials.from_service_account_info(creds_dict)
        service = build("drive", "v3", credentials=credentials)
        file_name = os.path.basename(file_path)
        metadata = {"name": file_name, "parents": [folder_id]}
        media = MediaFileUpload(file_path, mimetype="application/json", resumable=True)
        service.files().create(body=metadata, media_body=media, fields="id").execute()
        return True, "Google Drive 업로드 완료"
    except Exception as e:
        return False, f"Google Drive 업로드 실패: {e}"
