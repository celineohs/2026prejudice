# -*- coding: utf-8 -*-
"""
Google Drive 업로드 유틸 (Study1 대화 로그용).
GOOGLE_DRIVE_FOLDER_ID, GOOGLE_DRIVE_CREDENTIALS_JSON 이 설정된 경우에만 업로드 시도.
get_env(key) 는 st.secrets / os.getenv 를 쓰는 앱의 _get_env 함수를 넘기면 됨.
"""

import json
import os


def upload_file_to_drive(file_path: str, get_env) -> tuple:
    """
    file_path 의 파일을 설정된 Google Drive 폴더에 업로드한다.
    get_env: (key: str, default=None) -> str 형태의 함수 (예: 앱의 _get_env)
    반환: (성공 여부, 메시지)
    """
    folder_id = (get_env("GOOGLE_DRIVE_FOLDER_ID") or "").strip()
    creds_json = (get_env("GOOGLE_DRIVE_CREDENTIALS_JSON") or "").strip()
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
        # "Invalid control character" = private_key 안에 실제 줄바꿈이 들어간 경우. TOML이 \n을 줄바꿈으로 바꿔서 생김 → 되돌려서 재시도
        err_msg = str(e)
        if "control character" in err_msg.lower():
            fixed = creds_json.replace("\r\n", "\\n").replace("\r", "\\n").replace("\n", "\\n")
            try:
                creds_dict = json.loads(fixed)
            except json.JSONDecodeError:
                return False, (
                    f"GOOGLE_DRIVE_CREDENTIALS_JSON JSON 파싱 실패: {e}. "
                    "Secrets에서 private_key 값은 반드시 한 줄로, 줄바꿈은 \\n (백슬래시+n) 두 글자로 넣어주세요."
                )
        else:
            return False, (
                f"GOOGLE_DRIVE_CREDENTIALS_JSON JSON 파싱 실패: {e}. "
                "Streamlit Secrets에는 JSON 전체를 한 줄로 넣고, 키 이름은 쌍따옴표(\")로 적어주세요."
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
