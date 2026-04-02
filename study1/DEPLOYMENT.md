# 배포 가이드 (비대면 실험용)

## 옵션 1: Streamlit Cloud (추천)

1. GitHub에 저장소 푸시
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. "New app" 클릭
4. GitHub 저장소 선택
5. **Secrets 설정** (로컬 .env 대신 사용):
   - Settings → Secrets
   - TOML 형식 예시:
     ```toml
     API_PROVIDER = "anthropic"
     ANTHROPIC_API_KEY = "sk-ant-your-key-here"
     ```
     또는 OpenAI 사용 시:
     ```toml
     API_PROVIDER = "openai"
     OPENAI_API_KEY = "your_openai_key_here"
     ```
   - 조건 앱(`Code/study1-cond*.py`. 모노레포 `2026prejudice`에서는 `study1/Code/...`)도 동일한 방식으로 Secrets 설정
6. **메인 파일**: 배포할 조건에 따라 예) 단독 저장소 기준 `Code/study1-cond1.py` 지정 (모노레포면 `study1/Code/study1-cond1.py`)
7. 배포 완료 후 공개 URL 받기

## 옵션 2: 로컬 서버 + ngrok

1. 로컬에서 Streamlit 실행 (저장소 루트에서)
   ```bash
   streamlit run "Code/study1-cond1.py"
   ```
   (`2026prejudice` 모노레포: `study1/Code/study1-cond1.py`)

2. ngrok 설치 및 실행
   ```bash
   # ngrok 설치 (macOS)
   brew install ngrok
   
   # 또는 https://ngrok.com/download 에서 다운로드
   
   # 터널 생성
   ngrok http 8501
   ```

3. ngrok이 제공하는 공개 URL을 참가자에게 공유

## 옵션 3: 클라우드 서버 (AWS, GCP 등)

1. 클라우드 인스턴스 생성
2. 프로젝트 파일 업로드
3. Streamlit 실행
4. 방화벽 설정 (포트 8501 개방)
5. 공개 IP 또는 도메인으로 접근

## 보안 주의사항

- ✅ API 키는 환경변수로만 관리
- ✅ `.env` 파일은 절대 Git에 커밋하지 않기
- ✅ Streamlit Cloud Secrets 사용 권장
- ⚠️ 공개 URL 공유 시 참가자 ID 관리 체계 필요
