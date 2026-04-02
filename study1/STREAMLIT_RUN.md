# Study 1 Streamlit 실행 경로

앱 파일은 `Code/` 안에 있습니다. **저장소 루트**에서 아래처럼 실행하는 것을 권장합니다.

> **저장소별 경로**
> - **`thesis-study1` 등 단독 저장소**(이 폴더가 곧 리포지토리 루트): 아래 명령을 그대로 사용합니다.
> - **`2026prejudice` 모노레포** 안에서 돌릴 때: 경로 앞에 `study1/` 를 붙입니다.  
>   예: `streamlit run "study1/Code/study1-cond1.py"`

```bash
cd /path/to/thesis-study1
pip install -r requirements.txt
streamlit run "Code/study1-cond1.py"
```

조건에 따라 `study1-cond2.py`, `study1-cond3-f.py` 등 파일명만 바꿉니다.

## Streamlit Cloud

- **Main file path** (단독 저장소 기준): `Code/study1-condN....py` (배포할 조건으로 지정)
- **프로필 이미지**: 저장소 루트의 `study1_profile/*.jpg` (리포에 포함됨)
- **테마**: 리포 루트 `.streamlit/config.toml`(이 폴더 기준으로는 `study1/.streamlit/config.toml`) — 라이트 기본 + 다크 선택 시에도 밝은 팔레트 유지.

**참고:** `2026prejudice`에서 저장소 루트로 `streamlit run study1/Code/...` 하면 **저장소 최상단** `.streamlit/`이 적용됩니다. `thesis-study1`과 동일한 테마를 로컬에서도 쓰려면 루트 `.streamlit/config.toml`을 `study1/.streamlit/config.toml`과 맞추면 됩니다.

## Google Drive 점검 (로컬)

저장소 루트의 `.env`를 사용합니다.

```bash
python Scripts/verify_google_drive.py
```

모노레포에서는: `python study1/Scripts/verify_google_drive.py`
