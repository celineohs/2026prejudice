# -*- coding: utf-8 -*-
"""
Google Drive OAuth refresh token 발급용 (로컬에서 1회 실행).

필요:
- Google Cloud Console에서 OAuth client 생성 (Desktop app 권장)
- client_id / client_secret 준비

실행:
  python generate_drive_refresh_token.py

출력된 refresh_token을 Streamlit Secrets에 넣으면,
Streamlit Cloud에서 사용자 Drive 용량으로 자동 업로드가 가능해집니다.
"""

import json


def main():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError as e:
        raise SystemExit(f"Missing dependency: {e}. Install: pip install google-auth-oauthlib") from e

    scopes = ["https://www.googleapis.com/auth/drive.file"]

    print("Paste your OAuth Client ID:")
    client_id = input("> ").strip()
    print("Paste your OAuth Client Secret:")
    client_secret = input("> ").strip()

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    print("\n=== COPY THESE INTO Streamlit Secrets ===\n")
    print(f'GOOGLE_DRIVE_OAUTH_CLIENT_ID = "{client_id}"')
    print(f'GOOGLE_DRIVE_OAUTH_CLIENT_SECRET = "{client_secret}"')
    if not creds.refresh_token:
        print(
            "\nERROR: refresh_token was not returned.\n"
            "- Make sure prompt='consent' and access_type='offline'\n"
            "- If you already authorized before, revoke access and retry:\n"
            "  https://myaccount.google.com/permissions\n"
        )
    else:
        print(f'GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN = "{creds.refresh_token}"')

    # Helpful: show authorized_user json shape if needed
    print("\n--- Debug (authorized_user info) ---")
    info = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": creds.refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "scopes": scopes,
    }
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

