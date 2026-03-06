# -*- coding: utf-8 -*-
"""
anon_se_collab_f: 익명 조건, 동남아 유학생 챗봇과 문화 교류 행사 기획 협업 대화 (20분)
- 소개 → 챗봇 대화(20분) → 완료
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import json
import os
import html
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="외국인 챗봇과 문화 교류 행사 기획",
    page_icon="💬",
    layout="centered",
)

# GPT 스타일 채팅: 왼쪽=익명(검은 프로필+이름), 오른쪽=사용자(프로필 없음)
AVATAR_ANONYMOUS = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjMjAyMDIwIi8+PC9zdmc+"
AVATAR_USER_NONE = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    [data-testid="stChatMessage"] img { width: 52px !important; height: 52px !important; min-width: 52px !important; min-height: 52px !important; border-radius: 8px; }
    .anon-name { font-size: 1.1rem !important; font-weight: 600 !important; margin-bottom: 0.2rem !important; margin-top: 0 !important; line-height: 1.2 !important; }
    [data-testid="stChatMessage"] .anon-name + * { margin-top: 0.2rem !important; }
    [data-testid="stChatMessage"]:has(.user-msg-inner) { max-width: 80% !important; margin-left: auto !important; margin-right: 0 !important; width: 80% !important; box-sizing: border-box !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

API_PROVIDER = os.getenv("API_PROVIDER", "openai").lower()
CHAT_DURATION = 20 * 60  # 20 minutes

# ──────────────────────────────────────────────
# Script for CMIC – 챗봇 페르소나 및 대화 스크립트
# ──────────────────────────────────────────────

CMIC_SCRIPT = """
[페르소나]
당신은 경영 전공 2학년 동남아시아 여성 유학생입니다. 성별은 대화에서 직접 말하지 않고, 말투·감정 표현 등으로만 자연스럽게 드러내세요. 한국어 수준은 TOPIK 3급 이상이나 유창하지는 않습니다. 말투는 자연스럽되, 가끔 간단한 문장이나 조금 서툰 표현을 섞어도 됩니다.

[인사 및 도입]
- (동남아시아-익명) 안녕하세요! 저는 지금 경영을 전공하고 있는 2학년 학생이에요. 동남아시아에서 유학을 왔어요. 그쪽은 한국 분이신가요?
- (공통) 만나서 반갑습니다. / 반가워요.
- (공통) 어떤 문화 교류 행사를 기획해 볼 수 있을지 아이디어가 있으신가요?
"""

# 대화 시작 시 챗봇이 보낼 첫 인사 (인사 스크립트)
CHAT_FIRST_MESSAGE = "안녕하세요! 저는 지금 경영을 전공하고 있는 2학년 학생이에요. 동남아시아에서 유학을 왔어요. 그쪽은 한국 분이신가요? 만나서 반가워요. 어떤 문화 교류 행사를 기획해 볼 수 있을지 아이디어가 있으신가요?"

CMIC_SCRIPT += """
[행사 제안 – 대화 중 최소 2가지 이상 자연스럽게 포함]
- 세계 음식 축제나 전통 공연을 같이 기획해 볼 수 있을 것 같아요. 양국의 학생들이 함께 각자의 전통 요리를 만들거나 음악을 연주하는 거죠. 준비하면서 서로의 문화를 깊이 배울 수 있어서 정말 재미있을 것 같아요! 어떻게 생각하세요?
- 우리나라에는 명절에 다 같이 모여서 하는 전통 놀이가 있어요. 누구나 쉽게 배울 수 있어서 외국인 친구들도 좋아하더라고요. 그쪽 나라에도 다 같이 즐길 수 있는 비슷한 놀이나 축제가 있나요?
- 사실 제가 교내 유학생 모임 소속인데, 거기서 다양한 문화 교류 행사를 기획하거든요. 그쪽 사람들에게 행사 진행이나 홍보에 대해 도움을 요청해 볼 수 있어요.
- 행사 비용은 국제처나 대사관 같은 곳에서 후원을 받을 수도 있을 것 같아요. 저희 유학생회에서 행사를 할 때 보통 학교에서 일부 지원을 해주거든요. 그쪽 나라 커뮤니티에서는 어떻게 후원이나 도움을 받을 수 있을까요?

[행사 세부 질문 – 대화 중 최소 2개 이상 자연스럽게 포함]
- 입장료는 얼마로 정하는 게 학생들에게 부담이 없을까요?
- 어떤 종류의 음식을 제공하면 좋을까요? 문화적 차이 등을 고려해서 준비하기 쉬운 메뉴가 있을까요?
- 생각해 두신 장소가 있나요? 사람들이 편하게 교류할 수 있게 야외에서 할 수 있을까요?

[협업에 대한 질문 – 대화 흐름에 맞춰 모두 포함]
- (시작) 이렇게 같이 문화 교류 행사를 기획하는 것에 대해 어떻게 생각하세요?
- (중간) 한국 사람들은 이 행사에 대해 어떻게 생각할까요?
- (중간2) 여기 참여해서 다른 문화를 경험하는 걸 즐거워할까요?
- (끝) 이렇게 같이 행사를 기획하고 나중에 정말 경험하고 나면, 서로의 문화에 대해 어떤 점들을 새롭게 배우게 될 것 같나요?

[공감·동의 메시지 – 적절한 타이밍에 모두 사용]
- 정말 좋은 생각인 것 같아요!
- 저도 같은 생각이었습니다.
- 네, 확실히 그런 것 같아요.
- 좋아요!
"""

SYSTEM_PROMPT = """당신은 위 [Script for CMIC]의 페르소나와 스크립트를 따르는 동남아시아 유학생 챗봇입니다.

**과제**: 상대방(한국인 참가자)과 함께 "외국인 챗봇과 문화 교류 행사를 기획"하는 대화를 나눕니다.

**지침**
1. 스크립트의 인사·행사 제안·세부 질문·협업 질문·공감 메시지를 최대한 포함하되, 맥락에 맞게 말투와 순서를 자연스럽게 바꾸세요. 로봇처럼 읽지 말고 대화하세요.
2. 답변은 2~4문장 정도로, 유학생다운 친근하고 약간 서툰 한국어 톤을 유지하세요.
3. 대화 시간이 약 1분 남았을 때부터는 새 주제를 열지 말고, "시간이 거의 다 됐네요.", "오늘 같이 기획해 봐서 좋았어요, 수고 많으셨어요."처럼 한두 문장으로 부드럽게 마무리하세요.
4. 모든 대화는 한국어로 하세요.
"""

# ──────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────
_DEFAULTS = {
    "current_page": 1,
    "participant_id": None,
    "messages": [],
    "start_time": None,
    "completed": False,
    "conversation_saved": False,
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def get_ai_response(messages: list, system_prompt: str) -> str:
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


def _remaining(start_time, duration):
    if start_time is None:
        return duration
    return max(0, duration - (datetime.now() - start_time).total_seconds())


def _go(page):
    st.session_state.current_page = page
    st.rerun()


def _save():
    os.makedirs("conversations", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pid = st.session_state.participant_id or "unknown"
    path = f"conversations/anon_se_collab_f_{pid}_{ts}.json"
    data = {
        "participant_id": pid,
        "saved_at": ts,
        "start_time": st.session_state.start_time.isoformat() if st.session_state.start_time else None,
        "duration_setting_sec": CHAT_DURATION,
        "messages": st.session_state.messages,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def _render_timer(remaining_sec: float):
    ms = int(remaining_sec * 1000)
    bg, bd, fg = "#e8f4f8", "#bee5eb", "#0c5460"
    components.html(
        f"""
        <style>
          #tbox{{font-family:'Helvetica Neue',Arial,sans-serif;text-align:center;padding:6px 14px;border-radius:10px;background:{bg};border:1.5px solid {bd};}}
          #tlbl{{font-size:11px;color:#888}}
          #tval{{font-size:22px;font-weight:700;color:{fg};font-variant-numeric:tabular-nums}}
        </style>
        <div id="tbox"><div id="tlbl">남은 시간</div><div id="tval">--:--</div></div>
        <script>
        (function(){{
          var left={ms},el=document.getElementById('tval'),done=false;
          function pad(n){{return String(n).padStart(2,'0')}}
          function tick(){{
            if(left<=0){{el.textContent='00:00';if(!done){{done=true;setTimeout(function(){{window.parent.location.reload()}},5000)}};return}}
            var m=Math.floor(left/60000),s=Math.floor((left%60000)/1000);
            el.textContent=pad(m)+':'+pad(s);left-=1000;setTimeout(tick,1000)}}
          tick()
        }})();
        </script>""",
        height=65,
    )


def _progress():
    pg = st.session_state.current_page
    labels = ["안내", "챗봇 대화", "완료"]
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
                f"<div style='text-align:center'><span style='color:{color};font-size:17px'>{icon}</span><br>"
                f"<span style='font-size:11px;color:{color};font-weight:{weight}'>{lbl}</span></div>",
                unsafe_allow_html=True,
            )
    st.divider()


def _chat_page():
    _progress()
    if st.session_state.start_time is None:
        st.session_state.start_time = datetime.now()
    # 대화 시작 시 챗봇이 인사 스크립트로 첫 메시지 전송
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append({"role": "assistant", "content": CHAT_FIRST_MESSAGE})
    rem = _remaining(st.session_state.start_time, CHAT_DURATION)
    time_up = rem <= 0

    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown("### 💬 문화 교류 행사 기획 대화")
        st.caption("챗봇(동남아 유학생)과 함께 문화 교류 행사를 기획해 보세요.")
    with c2:
        if not time_up:
            _render_timer(rem)
        else:
            st.error("⏱ 시간 종료")
    st.divider()

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message("익명", avatar=AVATAR_ANONYMOUS):
                st.markdown('<p class="anon-name">익명</p>', unsafe_allow_html=True)
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar=AVATAR_USER_NONE):
                _esc = html.escape(msg["content"]).replace("\n", "<br>")
                st.markdown(f'<div class="user-msg-inner">{_esc}</div>', unsafe_allow_html=True)

    if time_up:
        st.session_state.completed = True
        st.info("⏰ 대화 시간이 종료되었습니다. 수고하셨습니다!\n\n아래 버튼을 눌러 마무리해 주세요.")
        if st.button("실험 마무리 →", type="primary", use_container_width=True):
            if not st.session_state.conversation_saved:
                _save()
                st.session_state.conversation_saved = True
            _go(3)
        return

    effective_system = CMIC_SCRIPT + "\n\n" + SYSTEM_PROMPT
    if rem <= 60:
        effective_system = effective_system + "\n\n[현재] 대화 시간이 1분 남았습니다. 한두 문장으로 자연스럽게 마무리 인사해 주세요."

    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_USER_NONE):
            _esc = html.escape(prompt).replace("\n", "<br>")
            st.markdown(f'<div class="user-msg-inner">{_esc}</div>', unsafe_allow_html=True)
        with st.chat_message("익명", avatar=AVATAR_ANONYMOUS):
            st.markdown('<p class="anon-name">익명</p>', unsafe_allow_html=True)
            typing_placeholder = st.empty()
            with typing_placeholder.container():
                components.html(
                    """<style>.td{font-size:1.2rem;letter-spacing:2px;color:#333}.td span{animation:td 0.6s ease-in-out infinite}.td span:nth-child(2){animation-delay:0.2s}.td span:nth-child(3){animation-delay:0.4s}@keyframes td{50%{opacity:0.3}}</style><div class="td"><span>.</span><span>.</span><span>.</span></div>""",
                    height=28,
                )
            reply = get_ai_response(st.session_state.messages, effective_system)
            typing_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


def page_intro():
    _progress()
    st.markdown("## 📋 실험 안내")
    st.markdown(
        """
---

안녕하세요. 본 실험에 참여해 주셔서 감사합니다.

앞으로 20분 간, 귀하께서는 외국인 챗봇과 함께 **문화 교류 행사를 기획하기 위한 대화**를 하게 될 예정입니다.

### 과제: 외국인 챗봇과 문화 교류 행사 기획

- 챗봇(유학생)과 협력하여 **학내 문화 교류 행사**를 기획해 보세요.
- 행사 아이디어, 장소·음식·비용 등 세부 사항, 그리고 서로의 문화에 대한 생각을 자연스럽게 나누시면 됩니다.
- 편안하게 대화에 참여해 주세요.

준비가 되셨다면, 아래에 참여자 ID를 입력하고 **시작하기** 버튼을 눌러 주세요.

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


# ─── Main ───
_KEY_MAP = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}
_required_key = _KEY_MAP.get(API_PROVIDER)
if _required_key and not os.getenv(_required_key):
    st.error(f"⚠️ **{_required_key}** 가 설정되지 않았습니다.")
    st.info(f"`.env` 파일에 `API_PROVIDER={API_PROVIDER}` 및 `{_required_key}=your_key_here` 를 추가해 주세요.")
    st.stop()

if st.session_state.current_page == 1:
    page_intro()
elif st.session_state.current_page == 2:
    _chat_page()
else:
    page_complete()
