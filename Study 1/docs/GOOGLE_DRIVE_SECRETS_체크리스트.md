# Google Drive 연결 – Secrets 넣을 때 할 일 (체크리스트)

**"Expecting property name... line 2 column 1" 오류가 나면** → Secrets에 JSON을 **한 줄 + 작은따옴표**로 넣지 않은 경우입니다. 아래만 따라하면 됩니다.

---

## 1. Google 쪽에서 할 일

- [ ] Google Cloud Console에서 프로젝트 만들기/선택
- [ ] **Google Drive API** 사용 설정 (라이브러리에서 검색 후 사용)
- [ ] 서비스 계정 만들기 → **키(JSON)** 다운로드
- [ ] Google Drive에 폴더 만들기 → 그 폴더를 **서비스 계정 이메일**로 **편집자** 공유
- [ ] 폴더 주소에서 **폴더 ID** 복사: `https://drive.google.com/drive/folders/여기부터끝까지` 의 **여기부터끝까지** 부분

---

## 2. Streamlit Secrets에 넣을 때 (JSON 오류 없이)

### GOOGLE_DRIVE_FOLDER_ID

- [ ] 폴더 ID를 **큰따옴표로 감싼 한 줄**로 넣기  
  예: `GOOGLE_DRIVE_FOLDER_ID = "1ABC...긴문자열...xyz"`

### GOOGLE_DRIVE_CREDENTIALS_JSON

- [ ] **JSON 파일 전체**를 메모장 등으로 열어 **전체 복사**
- [ ] **[https://www.minifier.org/json](https://www.minifier.org/json)** 에 붙여넣기 → **Minify** 클릭
- [ ] 나온 **한 줄 JSON** 전체 복사
- [ ] Secrets에 아래처럼 **한 줄**로만 넣기:
  - `GOOGLE_DRIVE_CREDENTIALS_JSON = '` 입력
  - **바로 이어서** 방금 복사한 한 줄 JSON 붙여넣기 (줄바꿈 없음)
  - 맨 끝에 `'` 하나 입력
- [ ] **여러 줄로 나누어 넣지 않기** (넣으면 "Expecting property name... line 2" 오류 남)
- [ ] **Save** 클릭

---

## 3. 확인

- [ ] 앱 재시작 후, 실험 한 번 끝까지 진행해 보기
- [ ] Google Drive 해당 폴더에 `.json` 파일이 생겼는지 확인

자세한 단계는 **GOOGLE_DRIVE_SETUP.md** 를 보세요.
