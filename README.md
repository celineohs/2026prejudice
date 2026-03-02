# AI 챗봇과의 상호작용이 외국인 인식에 미치는 영향

IRB 승인 연구를 위한 Streamlit 기반 AI 챗봇 상호작용 플랫폼입니다.

## 집단 2 실험 플랫폼 (app_group2)

참가자가 AI 챗봇과 **안내 → 일상 대화(5분) → 과제 안내 → 과제 대화(20분)** 순서로 진행하는 4단계 실험입니다.

### 기능

- 🤖 **멀티 API**: OpenAI / Claude(Anthropic) / Gemini 중 선택
- 📄 **4단계 플로우**: 안내 → 5분 일상 대화 → 과제 안내 → 20분 과제 대화
- ⏱️ **시간 제한**: 5분·20분 타이머, 종료 시 부드럽게 다음 단계로 전환
- 💾 **대화 기록 자동 저장**: 프로젝트 루트의 `conversations/` 폴더에 `group2_{참여자ID}_{타임스탬프}.json` 형식으로 저장 (배포 시 Streamlit Secrets 사용 권장)
- 👥 **동시 참여**: 브라우저 세션마다 별도 상태를 사용하므로, 다른 참여자 ID로 여러 명이 동시에 참여해도 충돌 없이 진행됩니다
- 👤 참여자 ID 입력 후 진행

### 페이지 구성

| 단계 | 내용 |
|------|------|
| 1 | 실험 안내 + 참여자 ID 입력 |
| 2 | 챗봇과 **5분** 일상 대화 (서로 알아가기) |
| 3 | 과제 안내 (과제 내용은 코드에서 수정 가능) |
| 4 | 챗봇과 **20분** 과제 대화 |
| 5 | 실험 완료 및 저장 안내 |

---

## 설치 방법

1. **저장소 클론**
   ```bash
   git clone https://github.com/celineohs/2026prejudice.git
   cd 2026prejudice
   ```

2. **가상환경 생성 및 활성화** (선택사항)
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   # 또는  venv\Scripts\activate   # Windows
   ```

3. **패키지 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **환경변수 설정**

   프로젝트 루트에 `.env` 파일을 만들고, 사용할 API에 맞게 설정하세요.

   **OpenAI (기본값)**
   ```bash
   API_PROVIDER=openai
   OPENAI_API_KEY=sk-your-key-here
   # OPENAI_MODEL=gpt-4o-mini   # 선택사항
   ```

   **Claude (Anthropic)**
   ```bash
   API_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   # ANTHROPIC_MODEL=claude-sonnet-4-20250514   # 선택사항
   ```

   **Gemini**
   ```bash
   API_PROVIDER=gemini
   GEMINI_API_KEY=your-gemini-key-here
   # GEMINI_MODEL=gemini-2.0-flash   # 선택사항
   ```

---

## 실행 방법

```bash
streamlit run app_group2.py
```

브라우저에서 기본 주소 `http://localhost:8501` 로 열립니다.

---

## 인터넷 배포 (Streamlit Community Cloud 등)

1. 이 저장소를 GitHub에 푸시한 뒤, [Streamlit Community Cloud](https://share.streamlit.io/)에서 **New app** → 저장소 연결.

2. **메인 파일**: `app_group2.py` 지정.

3. **Secrets** (배포 환경에서는 `.env` 대신 사용 권장):
   - 좌측 **Settings → Secrets** 에서 아래 형식으로 입력.
   ```toml
   API_PROVIDER = "openai"
   OPENAI_API_KEY = "sk-your-key-here"
   ```
   또는 Anthropic/Gemini 사용 시:
   ```toml
   API_PROVIDER = "anthropic"
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
   ```toml
   API_PROVIDER = "gemini"
   GEMINI_API_KEY = "..."
   ```

4. 배포 후 생성된 URL을 참가자에게 공유하면 됩니다.

---

## 데이터 형식

저장되는 JSON 파일 예시 (`conversations/group2_{참여자ID}_{타임스탬프}.json`):

```json
{
  "participant_id": "P001",
  "group": 2,
  "saved_at": "20260302_143022",
  "phase1": {
    "start_time": "2026-03-02T14:30:22",
    "duration_setting_sec": 300,
    "messages": [{"role": "user", "content": "..."}, ...]
  },
  "phase2": {
    "start_time": "2026-03-02T14:36:00",
    "duration_setting_sec": 1200,
    "messages": [...]
  }
}
```

---

## 커스터마이즈

- **안내 문구**: `app_group2.py` 안 `page_intro()`, `page_task_intro()` 의 마크다운 수정
- **과제 내용**: `page_task_intro()` 에서 과제 설명 텍스트 수정
- **시간**: 상단 `PHASE1_DURATION`, `PHASE2_DURATION` (초 단위) 변경
- **챗봇 톤**: `SYSTEM_PROMPT_PHASE1`, `SYSTEM_PROMPT_PHASE2` 수정

---

## 주의사항

- ⚠️ API 키는 절대 공개 저장소에 올리지 마세요. 배포 시에는 Secrets 사용.
- ⚠️ `.env` 및 `conversations/` 폴더는 `.gitignore`에 포함되어 있습니다.
- OpenAI/Anthropic/Gemini API 사용 시 비용이 발생할 수 있으니 사용량을 확인하세요.

---

## 라이선스

연구 목적으로만 사용하세요.
