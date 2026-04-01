# Google Drive 채팅 로그 저장 – 처음부터 설정하기

Streamlit 실험 앱에서 **대화 종료 시 채팅 로그(JSON)가 자동으로 Google Drive 폴더에 업로드**되도록 하려면 아래 순서대로 진행하세요.

---

## 연결하려면 해야 할 일 (요약)

| 순서 | 할 일 |
|------|--------|
| 1 | Google Cloud Console 접속 → 프로젝트 만들기/선택 |
| 2 | **Google Drive API** 사용 설정 (라이브러리에서 검색 후 사용) |
| 3 | 서비스 계정 만들기 → **키(JSON)** 다운로드 |
| 4 | Google Drive에 폴더 만들기 → 그 폴더를 **서비스 계정 이메일**로 **편집자** 공유 |
| 5 | 폴더 URL에서 **폴더 ID** 복사 (`/folders/` 뒤의 긴 문자열) |
| 6 | **Streamlit Cloud → 해당 앱 → Settings → Secrets** 에서 아래 두 개 추가 |

**Secrets에 넣는 형식 (JSON 오류 나지 않게):**

- `GOOGLE_DRIVE_FOLDER_ID` = 5번에서 복사한 폴더 ID를 **큰따옴표로 감싼 한 줄**
- 업로드 방식은 2가지 중 택 1
  - **옵션 1(서비스 계정)**: `GOOGLE_DRIVE_CREDENTIALS_JSON` (아래 8번). 단, Shared drives가 꺼져 있으면 403(quota)로 막힐 수 있음.
  - **옵션 2(OAuth 권장)**: `GOOGLE_DRIVE_OAUTH_CLIENT_ID / SECRET / REFRESH_TOKEN` (아래 8번-옵션2). Shared drives 없어도 **내 Drive 용량**으로 업로드됨.

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

## 8. Streamlit Cloud Secrets에 넣기 (배포 시) – JSON 오류 없이

**"Expecting property name... line 2 column 1" 오류는 Secrets에 JSON을 여러 줄로 넣었을 때 납니다. 아래만 지키면 됩니다.**

### 8-1. GOOGLE_DRIVE_FOLDER_ID

- 7단계에서 복사한 **폴더 ID**를 그대로 큰따옴표로 감싸서 한 줄로 넣기.

```toml
GOOGLE_DRIVE_FOLDER_ID = "1ABC...폴더ID전체...xyz"
```

### 8-2. GOOGLE_DRIVE_CREDENTIALS_JSON (한 줄 + 작은따옴표로 감싸기)

1. PC에 받아 둔 **서비스 계정 키 JSON 파일**을 메모장(또는 VS Code 등)으로 연다.
2. **전체 선택(Ctrl+A / Cmd+A)** → **복사**.
3. **[JSON Minifier](https://www.minifier.org/json)** 사이트 접속 → 큰 칸에 **붙여넣기** → **Minify** 버튼 클릭.
4. 아래쪽에 나온 **한 줄로 된 JSON**을 **전체 선택 후 복사**.
5. Streamlit Cloud → 해당 앱 → **Settings** → **Secrets** 로 이동.
6. Secrets 편집 칸에 아래처럼 **한 줄**로 적는다. (기존 키들은 그대로 두고 추가)

   - 먼저 적기:  
     `GOOGLE_DRIVE_CREDENTIALS_JSON = '`
   - **바로 이어서** 4번에서 복사한 **한 줄 JSON 전체**를 붙여넣기. (줄바꿈 없이)
   - 맨 끝에 작은따옴표 하나 추가:  
     `'`

   **최종 모양 예시 (한 줄):**

   ```toml
   GOOGLE_DRIVE_CREDENTIALS_JSON = '{"type":"service_account","project_id":"프로젝트이름","private_key_id":"...","private_key":"-----BEGIN PRIVATE KEY-----\nMIIE...\n-----END PRIVATE KEY-----\n","client_email":"...@....iam.gserviceaccount.com","client_id":"..."}'
   ```

   - **반드시 지킬 것:**  
     - JSON은 **한 줄** (Minifier로 만든 것 그대로).  
     - 값 전체를 **작은따옴표 `'`** 로 감싸기. (TOML에서 이렇게 하면 안쪽 큰따옴표 `"` 는 그대로 둬도 됨.)  
     - **Secrets에는 여러 줄로 넣지 말 것.** (넣으면 "Expecting property name... line 2" 오류 남.)

7. **Save** 클릭. 앱이 재시작되면 실험 종료 시 해당 Drive 폴더에 JSON이 자동 업로드됩니다.

---

## 8 (옵션 2). OAuth로 자동 업로드 (Shared drives 없어도 가능, 권장)

서비스 계정 방식에서 `Service Accounts do not have storage quota` (403) 이 뜨거나, **Shared drives 메뉴가 없는 학교 계정**이면 이 방식이 가장 안정적입니다.  
한 번만 refresh token을 발급해 Secrets에 넣으면 이후에는 자동 업로드됩니다.

### 8-옵션2-1. Google Cloud Console에서 OAuth Client 만들기

1. Google Cloud Console → **APIs & Services** → **Credentials**
2. **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app** (권장)
4. Create 후 **Client ID / Client secret** 복사

### 8-옵션2-2. 로컬에서 refresh token 발급 (1회)

프로젝트 루트에서 아래 파일을 실행합니다.

```bash
python generate_drive_refresh_token.py
```

실행하면 브라우저가 열리고 Google 로그인/동의를 한 뒤, 터미널에 아래 3개가 출력됩니다:

- `GOOGLE_DRIVE_OAUTH_CLIENT_ID`
- `GOOGLE_DRIVE_OAUTH_CLIENT_SECRET`
- `GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN`

### 8-옵션2-3. Streamlit Secrets에 추가

Streamlit Cloud → 앱 → **Settings** → **Secrets** 에 아래를 추가합니다.

```toml
GOOGLE_DRIVE_FOLDER_ID = "Drive에서 만든 폴더 ID"
GOOGLE_DRIVE_OAUTH_CLIENT_ID = "..."
GOOGLE_DRIVE_OAUTH_CLIENT_SECRET = "..."
GOOGLE_DRIVE_OAUTH_REFRESH_TOKEN = "..."
```

이후부터는 앱이 **OAuth(내 계정)** 으로 업로드를 시도하며, 성공 시 “Google Drive 업로드 완료 (OAuth)”로 표시됩니다.  
서비스 계정 키(`GOOGLE_DRIVE_CREDENTIALS_JSON`)는 없어도 됩니다.

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
