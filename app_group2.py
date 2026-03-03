import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import json
import os
import html
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI 챗봇 실험 (집단 2)",
    page_icon="💬",
    layout="centered",
)

# GPT 스타일 채팅: 왼쪽=익명(검은 프로필+이름), 오른쪽=사용자(프로필 없음)
# 48x48 검은 네모 SVG (CSS로 더 크게 표시)
AVATAR_ANONYMOUS = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjMjAyMDIwIi8+PC9zdmc+"
AVATAR_USER_NONE = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"  # 1x1 투명(프로필 없음)

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    /* 익명(챗봇) 아바타만 크게 */
    [data-testid="stChatMessage"] img { width: 52px !important; height: 52px !important; min-width: 52px !important; min-height: 52px !important; border-radius: 8px; }
    /* 익명 이름: 폰트 크게, 이름-본문 간격 줄이기 */
    .anon-name { font-size: 1.1rem !important; font-weight: 600 !important; margin-bottom: 0.2rem !important; margin-top: 0 !important; line-height: 1.2 !important; }
    /* 익명 말풍선 안에서 이름 다음 요소 간격 */
    [data-testid="stChatMessage"] .anon-name + * { margin-top: 0.2rem !important; }
    /* 사용자 말풍선(회색 배경 전체) 가로 4/5, 왼쪽 여백 — 메시지 블록 전체에 적용 */
    [data-testid="stChatMessage"]:has(.user-msg-inner) { max-width: 80% !important; margin-left: auto !important; margin-right: 0 !important; width: 80% !important; box-sizing: border-box !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# Configuration (edit these or use .env)
# ──────────────────────────────────────────────
API_PROVIDER = os.getenv("API_PROVIDER", "openai").lower()

PHASE1_DURATION = 5 * 60       # 5 minutes  (seconds)
PHASE2_DURATION = 20 * 60      # 20 minutes (seconds)
# 타이머는 항상 중립 색상만 사용 (참가자 부담·평가 압박 감소)

SYSTEM_PROMPT_PHASE1 = """당신은 친근하고 따뜻한 대화 상대입니다.
상대방과 처음 만나 서로를 알아가는 시간입니다.
자연스럽고 편안한 일상 대화를 나누세요. 자기소개를 하고, 상대방에게도 관심을 가져주세요.
답변은 2-3문장 정도로 자연스럽게 해주세요.
한국어로 대화하세요."""

SYSTEM_PROMPT_PHASE2 = """당신은 친근하고 도움이 되는 대화 상대입니다.
주어진 과제에 대해 상대방과 함께 논의하고 대화를 나누세요.
자연스럽고 진솔한 대화를 유지하세요.
답변은 2-3문장 정도로 자연스럽게 해주세요.
한국어로 대화하세요.

[시간 종료 직전] 대화 시간이 약 1분 남았을 때부터는 자연스럽게 마무리하는 말을 해주세요.
예: "시간이 거의 다 됐네요.", "오늘 대화 정말 좋았어요, 수고 많으셨어요."처럼 한두 문장으로 부드럽게 마무리하고, 새 주제를 길게 열지 마세요."""

# ──────────────────────────────────────────────
# Session state defaults
# ──────────────────────────────────────────────
_DEFAULTS = {
    "current_page": 1,
    "participant_id": None,
    "phase1_messages": [],
    "phase2_messages": [],
    "phase1_start_time": None,
    "phase2_start_time": None,
    "phase1_completed": False,
    "phase2_completed": False,
    "conversation_saved": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ──────────────────────────────────────────────
# API helpers
# ──────────────────────────────────────────────

def get_ai_response(messages: list[dict], system_prompt: str) -> str:
    """Route to the configured API provider and return the assistant reply."""
    try:
        if API_PROVIDER == "openai":
            from openai import OpenAI

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[{"role": "system", "content": system_prompt}, *messages],
                temperature=0.7,
                max_tokens=800,
            )
            return resp.choices[0].message.content

        elif API_PROVIDER == "anthropic":
            import anthropic

            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            resp = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                max_tokens=800,
                system=system_prompt,
                messages=messages,
            )
            return resp.content[0].text

        elif API_PROVIDER == "gemini":
            import google.generativeai as genai

            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel(
                model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                system_instruction=system_prompt,
            )
            history = []
            for msg in messages[:-1]:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            chat = model.start_chat(history=history)
            resp = chat.send_message(messages[-1]["content"])
            return resp.text

        return f"지원하지 않는 API 제공자입니다: {API_PROVIDER}"

    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}"

# ──────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────

def _remaining(start_time, duration):
    if start_time is None:
        return duration
    return max(0, duration - (datetime.now() - start_time).total_seconds())


def _fmt(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _go(page):
    st.session_state.current_page = page
    st.rerun()


def _save():
    """대화 기록 저장 위치: 프로젝트 루트의 conversations/ 폴더.
    파일명: group2_{참여자ID}_{타임스탬프}.json
    동시 참여: Streamlit은 브라우저 세션마다 별도 session_state를 사용하므로
    다른 참여자(다른 ID)가 동시에 참여해도 서로 충돌하지 않습니다."""
    os.makedirs("conversations", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pid = st.session_state.participant_id or "unknown"
    path = f"conversations/group2_{pid}_{ts}.json"
    data = {
        "participant_id": pid,
        "group": 2,
        "saved_at": ts,
        "phase1": {
            "start_time": (
                st.session_state.phase1_start_time.isoformat()
                if st.session_state.phase1_start_time
                else None
            ),
            "duration_setting_sec": PHASE1_DURATION,
            "messages": st.session_state.phase1_messages,
        },
        "phase2": {
            "start_time": (
                st.session_state.phase2_start_time.isoformat()
                if st.session_state.phase2_start_time
                else None
            ),
            "duration_setting_sec": PHASE2_DURATION,
            "messages": st.session_state.phase2_messages,
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

# ──────────────────────────────────────────────
# JS countdown timer component
# ──────────────────────────────────────────────

def _render_timer(remaining_sec: float):
    """
    Client-side JS timer. 항상 중립 색상만 사용 (참가자 부담·평가 압박 감소).
    시간 종료 시 5초 후 자동 새로고침하여 전환 UI 표시.
    """
    ms = int(remaining_sec * 1000)
    bg, bd, fg = "#e8f4f8", "#bee5eb", "#0c5460"

    components.html(
        f"""
        <style>
          #tbox{{font-family:'Helvetica Neue',Arial,sans-serif;text-align:center;
                 padding:6px 14px;border-radius:10px;background:{bg};
                 border:1.5px solid {bd};}}
          #tlbl{{font-size:11px;color:#888}}
          #tval{{font-size:22px;font-weight:700;color:{fg};
                 font-variant-numeric:tabular-nums}}
        </style>
        <div id="tbox">
          <div id="tlbl">남은 시간</div>
          <div id="tval">--:--</div>
        </div>
        <script>
        (function(){{
          var left={ms},el=document.getElementById('tval'),done=false;
          function pad(n){{return String(n).padStart(2,'0')}}
          function tick(){{
            if(left<=0){{
              el.textContent='00:00';
              if(!done){{done=true;setTimeout(function(){{
                window.parent.location.reload()}},5000)}}
              return}}
            var m=Math.floor(left/60000),s=Math.floor((left%60000)/1000);
            el.textContent=pad(m)+':'+pad(s);
            left-=1000;setTimeout(tick,1000)}}
          tick()
        }})();
        </script>""",
        height=65,
    )

# ──────────────────────────────────────────────
# Progress indicator
# ──────────────────────────────────────────────

def _progress():
    pg = st.session_state.current_page
    labels = ["안내", "일상 대화", "과제 안내", "과제 대화"]
    cols = st.columns(len(labels))
    for i, (col, lbl) in enumerate(zip(cols, labels)):
        step = i + 1
        with col:
            if step < pg:
                icon, color, weight = "✓", "#28a745", "400"
            elif step == pg:
                icon, color, weight = "●", "#007bff", "700"
            else:
                icon, color, weight = "○", "#adb5bd", "400"
            st.markdown(
                f"<div style='text-align:center'>"
                f"<span style='color:{color};font-size:17px'>{icon}</span><br>"
                f"<span style='font-size:11px;color:{color};font-weight:{weight}'>"
                f"{lbl}</span></div>",
                unsafe_allow_html=True,
            )
    st.divider()

# ──────────────────────────────────────────────
# Chat page helper (shared by phase 1 & 2)
# ──────────────────────────────────────────────

def _chat_page(
    *,
    title: str,
    caption: str,
    messages_key: str,
    start_time_key: str,
    completed_key: str,
    duration: int,
    system_prompt: str,
    on_finish_page: int,
    finish_label: str,
):
    """
    Generic two-column chat page with countdown timer.

    Graceful ending strategy
    ────────────────────────
    • The JS timer counts down in real-time on the client.
    • When time runs out the page auto-refreshes (5 s grace).
    • On the server side we check the remaining time:
      - If > 0  → render chat input normally.
      - If ≤ 0  → hide chat input, show a friendly notice and
                   a button to proceed.  The *last* AI reply has
                   already been saved, so no conversation is cut off
                   mid-exchange.
    """
    _progress()

    # Start timer on first visit
    if st.session_state[start_time_key] is None:
        st.session_state[start_time_key] = datetime.now()

    rem = _remaining(st.session_state[start_time_key], duration)
    time_up = rem <= 0

    # ── header ──
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(f"### {title}")
        st.caption(caption)
    with c2:
        if not time_up:
            _render_timer(rem)
        else:
            st.error(f"⏱ 시간 종료")

    st.divider()

    # ── message history (GPT 스타일: 왼쪽 익명=검은 프로필+이름, 오른쪽 사용자=프로필 없음) ──
    for msg in st.session_state[messages_key]:
        if msg["role"] == "assistant":
            with st.chat_message("익명", avatar=AVATAR_ANONYMOUS):
                st.markdown('<p class="anon-name">익명</p>', unsafe_allow_html=True)
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar=AVATAR_USER_NONE):
                _esc = html.escape(msg["content"]).replace("\n", "<br>")
                st.markdown(f'<div class="user-msg-inner">{_esc}</div>', unsafe_allow_html=True)

    # ── time-up: graceful transition ──
    if time_up:
        st.session_state[completed_key] = True
        st.info(
            "⏰ 대화 시간이 종료되었습니다. 수고하셨습니다!\n\n"
            "아래 버튼을 눌러 다음 단계로 진행해 주세요."
        )
        if st.button(finish_label, type="primary", use_container_width=True):
            if on_finish_page == 5 and not st.session_state.conversation_saved:
                _save()
                st.session_state.conversation_saved = True
            _go(on_finish_page)
        return

    # ── chat input (only while time remains) ──
    # 20분 과제 대화 후반 1분: wrap-up 지시를 시스템 프롬프트에 추가
    effective_system = system_prompt
    if duration == PHASE2_DURATION and rem <= 60:
        effective_system = system_prompt + "\n\n[현재] 대화 시간이 1분 남았습니다. 한두 문장으로 자연스럽게 마무리 인사해 주세요."

    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state[messages_key].append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar=AVATAR_USER_NONE):
            _esc = html.escape(prompt).replace("\n", "<br>")
            st.markdown(f'<div class="user-msg-inner">{_esc}</div>', unsafe_allow_html=True)

        with st.chat_message("익명", avatar=AVATAR_ANONYMOUS):
            st.markdown('<p class="anon-name">익명</p>', unsafe_allow_html=True)
            typing_placeholder = st.empty()
            with typing_placeholder.container():
                components.html(
                    """
                    <style>
                    .td { font-size: 1.2rem; letter-spacing: 2px; color: #333; }
                    .td span { animation: td 0.6s ease-in-out infinite; }
                    .td span:nth-child(2) { animation-delay: 0.2s; }
                    .td span:nth-child(3) { animation-delay: 0.4s; }
                    @keyframes td { 50% { opacity: 0.3; } }
                    </style>
                    <div class="td"><span>.</span><span>.</span><span>.</span></div>
                    """,
                    height=28,
                )
            reply = get_ai_response(
                st.session_state[messages_key], effective_system
            )
            typing_placeholder.markdown(reply)
            st.session_state[messages_key].append(
                {"role": "assistant", "content": reply}
            )

        st.rerun()

# ──────────────────────────────────────────────
# Page 1 – 안내
# ──────────────────────────────────────────────

def page_intro():
    _progress()
    st.markdown("## 📋 실험 안내")
    st.markdown(
        """
---

안녕하세요! 본 실험에 참여해 주셔서 감사합니다.

이제 **AI 챗봇**과 대화를 나누게 됩니다.

먼저 **약 5분간** 챗봇과 자유롭게 일상적인 대화를 나누며
서로 알아가는 시간을 가질 예정입니다.

편안하게 대화에 참여해 주세요.

준비가 되셨다면, 아래에 참여자 ID를 입력하고 **시작하기** 버튼을 눌러주세요.

---
"""
    )

    pid = st.text_input("참여자 ID", placeholder="예: P001", key="pid_input")

    if st.button("대화 시작하기 →", type="primary", use_container_width=True):
        if pid and pid.strip():
            st.session_state.participant_id = pid.strip()
            _go(2)
        else:
            st.error("참여자 ID를 입력해 주세요.")

# ──────────────────────────────────────────────
# Page 2 – 일상 대화 (5 min)
# ──────────────────────────────────────────────

def page_phase1():
    _chat_page(
        title="💬 일상 대화",
        caption="챗봇과 편하게 대화를 나눠보세요.",
        messages_key="phase1_messages",
        start_time_key="phase1_start_time",
        completed_key="phase1_completed",
        duration=PHASE1_DURATION,
        system_prompt=SYSTEM_PROMPT_PHASE1,
        on_finish_page=3,
        finish_label="다음 단계로 진행 →",
    )

# ──────────────────────────────────────────────
# Page 3 – 과제 안내
# ──────────────────────────────────────────────

def page_task_intro():
    _progress()
    st.markdown("## 📋 과제 안내")
    st.markdown(
        """
---

지금까지 챗봇과 대화를 잘 나누셨습니다!

이제 **약 20분간** 아래의 과제를 바탕으로 챗봇과 대화를 이어가게 됩니다.

### 과제 내용

*(추후 수정 예정)*

과제 내용을 잘 읽고, 준비가 되셨다면 아래 버튼을 눌러 시작해 주세요.

---
"""
    )

    if st.button("과제 대화 시작하기 →", type="primary", use_container_width=True):
        _go(4)

# ──────────────────────────────────────────────
# Page 4 – 과제 대화 (20 min)
# ──────────────────────────────────────────────

def page_phase2():
    _chat_page(
        title="💬 과제 대화",
        caption="과제에 대해 챗봇과 대화를 나눠보세요.",
        messages_key="phase2_messages",
        start_time_key="phase2_start_time",
        completed_key="phase2_completed",
        duration=PHASE2_DURATION,
        system_prompt=SYSTEM_PROMPT_PHASE2,
        on_finish_page=5,
        finish_label="실험 마무리 →",
    )

# ──────────────────────────────────────────────
# Page 5 – 완료
# ──────────────────────────────────────────────

def page_complete():
    st.markdown("## ✅ 실험 완료")
    st.balloons()
    st.markdown(
        """
---

모든 대화가 완료되었습니다.

실험에 참여해 주셔서 진심으로 감사드립니다!

이제 이 창을 닫으셔도 됩니다.

---
"""
    )

    if not st.session_state.conversation_saved:
        _save()
        st.session_state.conversation_saved = True

    st.success("대화 기록이 안전하게 저장되었습니다.")

# ──────────────────────────────────────────────
# Main – API key guard & router
# ──────────────────────────────────────────────

_KEY_MAP = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

_required_key = _KEY_MAP.get(API_PROVIDER)
if _required_key and not os.getenv(_required_key):
    st.error(f"⚠️ **{_required_key}** 가 설정되지 않았습니다.")
    st.info(
        f"`.env` 파일에 다음을 추가해 주세요:\n\n"
        f"```\nAPI_PROVIDER={API_PROVIDER}\n{_required_key}=your_key_here\n```"
    )
    st.stop()

{1: page_intro, 2: page_phase1, 3: page_task_intro, 4: page_phase2}.get(
    st.session_state.current_page, page_complete
)()
