# Study 1 Streamlit 실행 경로

앱 파일은 `Code/` 안에 있습니다. **저장소 루트**에서 아래처럼 실행하는 것을 권장합니다.

```bash
cd /path/to/2026prejudice
pip install -r requirements.txt
streamlit run "Study 1/Code/study1-cond1.py"
```

조건에 따라 `study1-cond2.py`, `study1-cond3-f.py` 등 파일명만 바꿉니다.

## Streamlit Cloud

- **Main file path**: `Study 1/Code/study1-condN....py` (배포할 조건으로 지정)
- **프로필 이미지**: `Study 1/study1_profile/*.jpg` (저장소에 포함됨)

## Google Drive 점검 (로컬)

저장소 루트의 `.env`를 사용합니다.

```bash
python "Study 1/Scripts/verify_google_drive.py"
```
