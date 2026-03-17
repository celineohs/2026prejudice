# Google Drive 채팅 로그 저장 – 처음부터 설정하기

Streamlit 실험 앱에서 **대화 종료 시 채팅 로그(JSON)가 자동으로 Google Drive 폴더에 업로드**되도록 하려면 아래 순서대로 진행하세요.

---

## 1. Google Cloud Console 접속

1. 브라우저에서 **https://console.cloud.google.com/** 접속
2. Google 계정으로 로그인

---

## 2. 프로젝트 만들기(또는 선택)

1. 상단 **프로젝트 선택** 드롭다운 클릭
2. **「새 프로젝트」** 클릭
3. 프로젝트 이름 입력 (예: `prejudice-chat-log`)
4. **만들기** 클릭
5. 만들어진 프로젝트가 선택된 상태인지 확인 (상단에 프로젝트 이름 표시)

---

## 3. Google Drive API 사용 설정

1. 왼쪽 메뉴 **「API 및 서비스」** → **「라이브러리」** 클릭  
   (또는 상단 검색창에 "API 라이브러리" 검색)
2. **「Google Drive API」** 검색
3. **Google Drive API** 카드 클릭
4. **「사용」** 버튼 클릭
5. 사용 설정되면 **「API 및 서비스」** 대시보드로 돌아가면 됨

---

## 4. 서비스 계정 만들기

1. 왼쪽 메뉴 **「API 및 서비스」** → **「사용자 인증 정보」** 클릭
2. 상단 **「+ 사용자 인증 정보 만들기」** 클릭
3. **「서비스 계정」** 선택
4. **서비스 계정 세부정보**
   - 서비스 계정 이름: 예) `streamlit-chat-log`
   - 서비스 계정 ID는 자동 생성됨
   - **「만들기 및 계속하기」** 클릭
5. **역할 선택(선택사항)**  
   - 건너뛰어도 됨 → **「계속」** 클릭
6. **사용자 액세스(선택사항)**  
   - 건너뛰어도 됨 → **「완료」** 클릭

---

## 5. 서비스 계정 키(JSON) 다운로드

1. **「사용자 인증 정보」** 페이지에서 **서비스 계정** 목록이 보임
2. 방금 만든 서비스 계정(예: `streamlit-chat-log@...`) **이메일** 클릭
3. 상단 **「키」** 탭 클릭
4. **「키 추가」** → **「새 키 만들기」** 선택
5. 키 유형: **JSON** 선택 → **만들기** 클릭
6. JSON 파일이 PC에 다운로드됨  
   - 이 파일 내용이 **GOOGLE_DRIVE_CREDENTIALS_JSON** 에 넣을 값입니다.  
   - **절대 Git에 올리거나 다른 사람에게 공유하지 마세요.**

---

## 6. Google Drive 폴더 준비 및 공유

1. **https://drive.google.com** 접속 (일반 Google 계정으로)
2. **새로 만들기** → **폴더** 로 폴더 생성 (예: `study1_대화로그`)
3. 해당 폴더를 **우클릭** → **공유** 클릭
4. **사용자 추가** 칸에 **서비스 계정 이메일** 입력  
   - 이메일은 5단계에서 연 **서비스 계정 상세** 페이지 상단에 있음  
   - 형식: `xxxx@프로젝트이름.iam.gserviceaccount.com`  
   - 또는 다운로드한 JSON 파일을 텍스트 에디터로 열어 **`client_email`** 값 복사
5. 권한을 **편집자**로 설정 후 **전송** (링크 알림 보내기는 해제해도 됨)

> ⚠️ **중요**: 서비스 계정 이메일을 **편집자**로 공유하지 않으면 업로드가 실패합니다. "액세스 거부" 오류가 나면 이 단계를 다시 확인하세요.

---

## 7. 폴더 ID 복사

1. Drive에서 방금 공유한 **폴더**를 연 상태로
2. 브라우저 주소창 URL 확인  
   - 형식: `https://drive.google.com/drive/folders/1ABC...긴문자열...xyz`
3. **`/folders/` 뒤부터 끝까지**가 폴더 ID  
   - 예: `1ABC...긴문자열...xyz` 전체 복사  
   - 이 값이 **GOOGLE_DRIVE_FOLDER_ID** 입니다.

---

## 8. Streamlit Cloud Secrets에 넣기 (배포 시)

1. Streamlit Cloud → 해당 앱 → **Settings** → **Secrets** 열기
2. 아래 형식으로 추가 (기존 API 키 등은 그대로 두고 아래 두 항목 추가):

```toml
# 기존 키들 (API_PROVIDER, ANTHROPIC_API_KEY 등) 아래에 추가

GOOGLE_DRIVE_FOLDER_ID = "7단계에서 복사한 폴더 ID"

# CREDENTIALS: 반드시 한 줄로 넣기 (여러 줄로 넣으면 TOML이 \n 을 줄바꿈으로 바꿔서 파싱 오류 남)
# JSON 파일을 메모장 등으로 열어, 줄바꿈·공백 없이 한 줄로 붙인 뒤 아래처럼 따옴표로 감싸기
GOOGLE_DRIVE_CREDENTIALS_JSON = "{\"type\":\"service_account\",\"project_id\":\"...\",\"private_key_id\":\"...\",\"private_key\":\"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n\",\"client_email\":\"...@....iam.gserviceaccount.com\",\"client_id\":\"...\",...}"
```

- **한 줄 만드는 방법**: [JSON minifier](https://www.minifier.org/json) 등에 키 파일 내용을 붙여넣어 한 줄로 만든 뒤, Secrets에 붙여넣기.  
  TOML에서 따옴표 이스케이프: 값 안에 `"` 가 있으면 `\"` 로 적기. 또는 값 전체를 작은따옴표로 감싸면 됨:  
  `GOOGLE_DRIVE_CREDENTIALS_JSON = '{"type":"service_account",...}'` (값 안의 `"` 는 그대로)

3. **Save** 후 앱이 재시작되면, 다음 실험부터 **실험 종료 시 해당 Drive 폴더에 JSON이 자동 업로드**됩니다.

---

## 9. 로컬 실행 시 (.env)

로컬에서 `streamlit run study1-cond7-f.py` 등으로 실행할 때는 프로젝트 루트의 **`.env`** 파일에 같은 키를 넣습니다.

```bash
# Google Drive 대화 로그 업로드 (선택)
GOOGLE_DRIVE_FOLDER_ID=1ABC...폴더ID...xyz
GOOGLE_DRIVE_CREDENTIALS_JSON={"type":"service_account","project_id":"...","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n","client_email":"...@....iam.gserviceaccount.com","client_id":"...",...}
```

- `GOOGLE_DRIVE_CREDENTIALS_JSON` 은 JSON 전체를 **한 줄**로 넣고, 따옴표는 이스케이프하거나 minify된 한 줄 문자열로 저장하세요.
- `.env` 파일은 절대 Git에 커밋하지 마세요 (이미 `.gitignore`에 포함됨).

---

## 요약 체크리스트

- [ ] Google Cloud Console에서 프로젝트 생성/선택
- [ ] **Google Drive API** 사용 설정 (라이브러리에서 검색 후 사용)
- [ ] 서비스 계정 생성
- [ ] 서비스 계정 키(JSON) 다운로드
- [ ] Drive에 폴더 생성 후 **서비스 계정 이메일**을 **편집자**로 공유
- [ ] 폴더 URL에서 **폴더 ID** 복사 (`/folders/` 뒤 문자열)
- [ ] Streamlit Cloud: **Secrets**에 `GOOGLE_DRIVE_FOLDER_ID`, `GOOGLE_DRIVE_CREDENTIALS_JSON` 추가
- [ ] 로컬: **`.env`**에 위 두 키 추가

이후 참가자가 실험을 마칠 때마다 `study1-condX_{참여자ID}_{타임스탬프}.json` 파일이 해당 Drive 폴더에 쌓입니다.

---

## 자주 하는 실수 / 문제 해결

| 증상 | 확인할 것 |
|------|------------|
| 업로드가 아예 안 됨 | `GOOGLE_DRIVE_FOLDER_ID`, `GOOGLE_DRIVE_CREDENTIALS_JSON` 이 모두 설정되었는지 확인. 하나라도 비어 있으면 로컬에만 저장되고 Drive 업로드는 건너뜀. |
| "액세스 거부" / 403 | Drive 폴더를 **서비스 계정 이메일**(JSON의 `client_email`)과 **편집자**로 공유했는지 확인. |
| "API 사용 설정되지 않음" | Google Cloud Console → API 및 서비스 → 라이브러리에서 **Google Drive API**를 사용 설정했는지 확인. |
| Secrets 저장 후에도 반영 안 됨 | Streamlit Cloud에서 Secrets 저장 후 앱이 재시작될 때까지 잠시 기다리거나, 앱을 한 번 재배포. |
| JSON 파싱 오류 (Expecting property name... line 2) | Secrets에 **한 줄(줄바꿈 없이)** 로 넣기. 여러 줄로 넣으면 TOML이 `\n` 을 실제 줄바꿈으로 바꿔서 JSON이 깨짐. Minify한 한 줄 JSON + 작은따옴표로 감싸기: `GOOGLE_DRIVE_CREDENTIALS_JSON = '{"type":"service_account",...}'` |
