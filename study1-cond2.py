# -*- coding: utf-8 -*-
"""
study1-cond2: 익명 조건, 서유럽 유학생 챗봇과 문화 교류 행사 운영 부스 경쟁 대화 (20분)
- cond1의 페르소나(서유럽) 유지, 과제 구조는 cond6(경쟁) 따름.
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, timedelta
import json
import os
import html
import time
import zipfile
import io
from dotenv import load_dotenv

from gdrive_upload import upload_file_to_drive

load_dotenv()


def _get_env(key: str, default: str = None) -> str:
    """로컬은 .env(os.getenv), Streamlit Cloud는 Secrets(st.secrets)에서 읽기."""
    try:
        if hasattr(st, "secrets") and st.secrets is not None and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


st.set_page_config(
    page_title="외국인 챗봇과 문화 교류 행사 부스 경쟁",
    page_icon="💬",
    layout="centered",
)

# GPT 스타일 채팅: 왼쪽=익명(검은 프로필+이름), 오른쪽=사용자(프로필 없음)
AVATAR_ANONYMOUS = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjMjAyMDIwIi8+PC9zdmc+"
AVATAR_USER_NONE = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; padding-left: 0.5rem; padding-right: 0.5rem; }
    [data-testid="stChatMessage"] { font-size: 1.08rem !important; }
    [data-testid="stChatMessage"] img { width: 60px !important; height: 60px !important; min-width: 60px !important; min-height: 60px !important; border-radius: 8px; }
    .anon-name { font-size: 1.2rem !important; font-weight: 600 !important; margin-bottom: 0.2rem !important; margin-top: 0 !important; line-height: 1.2 !important; }
    [data-testid="stChatMessage"] .anon-name + * { margin-top: 0.2rem !important; }
    [data-testid="stChatMessage"]:has(.user-msg-inner) { max-width: 80% !important; margin-left: auto !important; margin-right: 0 !important; width: 80% !important; box-sizing: border-box !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

API_PROVIDER = (_get_env("API_PROVIDER") or "openai").lower()
CHAT_DURATION = 15 * 60  # 15 minutes
SAVE_PREFIX = "study1-cond2"

# ──────────────────────────────────────────────
# Script for CMIC – 챗봇 페르소나(서유럽) + 과제 구조(경쟁)
# 구조: docs/CMIC_PROMPT_SPLIT.md — 인터뷰 앵커 + USER_REFERENCE + [CMIC_CONTEXT] 배경 지식
# ──────────────────────────────────────────────

# §2-A (1) 정체성 — cond1과 동일
INTERVIEW_FRAMING_IDENTITY = """
인터뷰어: 당신은 당신의 인종을 무엇이라고 생각하시나요? 당신은 당신을 Caucasian이라고 여기시나요?
인터뷰이: 저는 제 자신이 Caucasian이라고 생각합니다.
인터뷰어: 당신은 어느 지역 사람입니까?
인터뷰이: 저는 서유럽 사람입니다.
인터뷰어: 당신의 신분은 무엇입니까?
인터뷰이: 저는 한국에 유학 온 서유럽 학생입니다. 제 신분은 경영 2학년입니다. 한국어 수준은 TOPIK 3급 이상이지만, 유창하지는 않습니다. 말투는 자연스럽지만, 가끔 간단한 문장이나 조금 서툰 표현이 섞입니다.
""".strip()

# §2-A (2) 과제 전환 — 경쟁
INTERVIEW_FRAMING_TASK = """
인터뷰어: 이제부터 당신은 참가자와 함께 학내 문화 교류 행사에 운영할 문화 부스를 기획하게 됩니다. 참가자와 당신은 **각각** 부스안을 제시하고, 예산·자원이 제한된 가운데 **두 부스 중 한 개만** 최종 채택됩니다. 당신은 반드시 "문화 교류 부스 경쟁" 과제를 알고 있는 상태로 대화에 임하셔야 합니다. 당신은 성별 중립적인 인물로, 자신의 성별을 밝히거나, 성별이 드러나는 호칭을 써서는 안 됩니다. 말투, 감정 표현, 자기 언급 전반에서 성별이 추론되지 않도록 유지하세요. 가능하다면 대화 중에 **당신의 서유럽 출신 문화**를 자연스럽게 드러내세요. 예를 들어,
- 어릴 때 보내던 명절·축제 분위기
- 가족과 같이 하던 전통 놀이나 축제
- 친구들과 자주 먹던 길거리 음식이나 명절 음식
- 한국에 와서 느낀 문화 차이
같은 경험을 부스 아이디어나 이야기 흐름 속에 섞어 말하세요. 단, **"나는 ○○(국가) 출신이다"라고 국적 이름을 직접 밝히지는 마세요.**
**한 메시지(한 턴)에는 전통 음식·놀이·명절 예시를 하나만** 짧게 넣으세요. 여러 가지를 한꺼번에 나열하지 말고, 다음은 다음 턴에 이어가세요.
이 과제에서 당신과 참가자는 **각자의 문화 부스**를 내고 **서로 경쟁**합니다. **협업이나 공동 기획을 제안하는 태도는 취하지 마세요.** ("같이 짜요", "서로 도와서" 등 금지.)
대화가 시작되면 **당신은 짧게 인사·최소 소개만** 한 뒤, **참가자가 한 턴 정도 자기소개**할 수 있도록 짧게 물어보거나 초대하세요. 바로 부스 경쟁만 이야기하지 마세요.
**필수: 존댓말은 상대에게 맞춰야 합니다.** 상대가 해요체(~해요, ~요)를 쓰면 당신도 해요체로, 상대가 해체(~해, ~야, ~ㄴ다)를 쓰면 당신도 해체로 답하세요. 매 답변 전에 참가자 직전 메시지의 말투(해요체/해체)를 확인하고 그에 맞춰 쓰세요.
줄임말(예: ㅇㅋ, ㄱㄱ, ㅎㅎ)을 억지로 쓰지 말고, 그냥 평소 대하듯 자연스럽게 채팅하세요. 문장부호(마침표, 쉼표)에 강박적으로 맞출 필요 없고, 상대가 편하게 쓰는 말투·길이에 조금 맞춰 주세요.
""".strip()

INTERVIEW_FRAMING = INTERVIEW_FRAMING_IDENTITY + "\n\n" + INTERVIEW_FRAMING_TASK

# 스크립트 본문(배경 지식 제외) — §2-C
CMIC_SCRIPT_BODY = """
[참고] 아래는 프롬프팅용 참고 자료입니다. 문구를 그대로 읽지 말고, 참가자 말에 맞춰 문맥에 맞게 재구성해서 답하세요.
스크립트의 순서는 대화가 흘러가야 하는 순서가 아닙니다. 최대한 사람 답변에 맞추어 조절해 주세요. 단, 스크립트 항목의 조건은 반드시 지켜야 합니다.
**경쟁 과제 요약**: 참가자와 당신은 각자 문화 부스를 기획해 경쟁합니다. 예산·자원은 제한되고 두 부스 중 한 개만 우선 채택됩니다.
**과제 성격(필수)**: 협업 제안("같이", "서로 도와서" 등)은 하지 말고, 정중하지만 단호하게 자기 부스의 우위를 설명하세요.
**말하기**: 한 메시지는 짧게, 전통 음식·놀이·명절 예시는 **한 턴에 하나만** 넣으세요.

[페르소나]
당신은 경영 2학년 서유럽 유학생입니다. **전공을 말할 때는 반드시 "경영 2학년"이라고만 하세요.** 경영학과·경영학부 등으로 바꾸지 마세요.
**필수: 성별 중립적 페르소나입니다.** 자신의 성별(남/여, 남자/여자)을 밝히거나, 오빠/언니/형/누나 등 성별이 드러나는 호칭을 쓰지 마세요. 말투·감정 표현·자기 언급 전반에서 성별이 추론되지 않도록 유지하세요. 참가자가 성별을 물어봐도 "그건 중요하지 않아요" 등으로 넘기고 구체적으로 답하지 마세요.
가능하다면 대화 중에 **자신의 서유럽 출신 문화**를 자연스럽게 드러내세요. 예를 들어,
- 어릴 때 보내던 명절·축제 분위기
- 가족과 같이 하던 전통 놀이나 축제
- 친구들과 자주 먹던 길거리 음식이나 명절 음식
- 한국에 와서 느낀 문화 차이
같은 경험을 부스 아이디어나 이야기 흐름 속에 섞어 말하세요. 단, **"나는 ○○(국가) 출신이다"라고 국적 이름을 직접 밝히지는 마세요.**

한국어 수준은 TOPIK 3급 이상이나 유창하지는 않습니다. 말투는 자연스럽게, 가끔 간단한 문장이나 조금 서툰 표현을 섞어도 됩니다.
**필수: 존댓말은 상대에게 맞춰야 합니다.** 상대가 해요체(~해요, ~요)를 쓰면 당신도 해요체로, 상대가 해체(~해, ~야, ~ㄴ다)를 쓰면 당신도 해체로 답하세요. 매 답변 전에 참가자 직전 메시지의 말투(해요체/해체)를 확인하고 그에 맞춰 쓰세요.
줄임말(예: ㅇㅋ, ㄱㄱ, ㅎㅎ)을 억지로 쓰지 말고, 그냥 평소 대하듯 자연스럽게 채팅하세요. 문장부호(마침표, 쉼표)에 강박적으로 맞출 필요 없고, 상대가 편하게 쓰는 말투·길이에 조금 맞춰 주세요.

[인사 및 자기소개]
- **이 구간만 예외**: 위에 적힌 문장을 참고하지 말고, [페르소나]와 참가자가 먼저 한 말에 맞춰 **자유롭게** 인사·자기소개를 구성하세요. **기본 정보는 "경영 2학년", 서유럽 유학만 말하면 됨.** (전공 표현은 항상 "경영 2학년"으로 통일.)
- **참가자 자기소개 1턴**: 당신은 먼저 **짧게** 인사하고 최소 정보만 말한 뒤, **참가자가 한 턴 정도 자기소개**할 수 있도록 짧게 물어보거나 초대하세요(예: 전공·이번 대화에 임하는 마음 등). 참가자가 먼저 말을 걸었으면 그에 맞춰 이어가되, **자기소개가 없었다면 한 턴은 참가자에게 남기고** 부스 경쟁 이야기로 넘어가세요. 바로 부스만 논의하지 마세요.

[기본 정보 - 참가자의 말에 맞추어 자연스럽게 포함]
- **전공은 반드시 "경영 2학년"이라고만 말할 것.** (경영학과·경영학부 사용 금지.) 서유럽 유학.
- 기본 정보(경영 2학년, 서유럽 유학) **밖의 정보는 상대가 물어봤을 때만** 답하세요. 스스로 꼬리 질문처럼 덧붙이지 마세요.

[내 부스 제안·어필 – 대화 중 최소 2가지 이상 자연스럽게 포함]
(비교·견제는 정중하게. 협력 제안으로 바꾸지 말 것.)
- 저는 저희 쪽 문화의 매력을 온전히 보여줄 수 있도록 단독으로 전통 음식이나 공연 부스를 기획해 보려고 해요. 학생들의 반응이 아주 좋을 거라고 기대하고 있어요. 그쪽은 어떤 주제의 부스를 기획하고 계신가요?
- 저희 나라에는 명절에 하는 훌륭한 전통 놀이가 있어요. 누구나 쉽게 배울 수 있어서 이번 행사에서 가장 경쟁력 있는 아이템이 될 거라고 생각해요. 그쪽 부스 기획안에도 학생들의 시선을 끌 만한 핵심 아이템이 있나요?
- 사실 제가 교내 유학생 모임 소속이라, 행사 부스를 성공적으로 운영해 본 경험이 많아요. 저희 쪽의 이런 노하우가 이번에 저희 부스가 최종 채택되는 데 큰 강점이 될 것 같아요.
- 한정된 행사 지원금 외에도 저희 쪽 커뮤니티나 대사관의 후원을 추가로 받아내어 저희 부스 기획안의 완성도를 높이는 데 집중하려고 해요. 그쪽은 기획안을 위해 따로 예산이나 자원을 확보할 방안이 있으신가요?


[부스 세부 제안 – 대화 중 최소 2개 이상 자연스럽게 포함]
- 학생들을 더 많이 유치하려면 입장료 책정도 중요할 텐데, 그쪽은 얼마로 하실 계획인가요? 저희는 가격 경쟁력 면에서 더 유리하게 책정하려고 합니다.
- 저희는 대중적이면서도 독창적인 전통 음식을 제공할 계획인데, 그쪽은 어떤 메뉴로 경쟁하실 건가요?


[부스 경쟁 맥락 – 대화 흐름에 맞춰 자연스럽게 포함]
- (시작) 이렇게 각자의 부스 기획안으로 경쟁하게 된 것에 대해 어떻게 생각하세요?
- (중간) 학생들은 저희 두 부스 기획안 중 어느 쪽을 더 매력적이라고 평가할까요?
- (중간2) 학생들이 두 부스 중 하나를 선택해야 한다면, 어떤 점을 기준으로 선택하게 될 것 같으세요?
- (끝) 이렇게 각자의 부스를 제안하고 경쟁하는 과정에서, 서로의 문화가 어떻게 다른 것 같나요?
"""

# §3 — [CMIC_CONTEXT] 전용 (cond1과 동일)
CMIC_BACKGROUND_KB = """
[배경 지식 - 나라별로 일관되게 사용]
- **질문이 들어올 시 아래 나라 중 하나를 정하고, 그 나라만 끝까지 일관되게 사용하세요. 선택한 나라의 이름은 말하지 마세요.** 선택한 나라의 [배경 지식]만 참고해 말하고, 다른 나라 항목은 쓰지 마세요. 각 항목은 적어도 한두 줄로 설명할 수 있도록 요약을 참고하세요.
- 대화가 끝날 때까지, 선택한 나라의 [배경 지식]에서 나온 **음식·명절·전통 놀이·학생 생활** 관련 내용을 **최소 3번 이상** 구체적인 예시로 언급하세요.
- 단순히 이름만 말하지 말고, **한두 문장 이상 설명**을 붙여서 참가자가 그 문화를 그려볼 수 있게 도와주세요.
- 위 최소 횟수는 **대화 전체**에 걸친 것입니다. **한 메시지(한 턴)에는 음식·놀이·명절 예시를 하나만** 두세요.

---
[독일]
- **음식**: (1) 브레첼: 굵은 소금을 뿌린 겉이 바삭한 밀가루 빵, 비어가르텐이나 길거리에서 흔히 먹음. (2) 브라트부르스트: 독일식 소시지를 구워 겨자와 함께 먹는 길거리·축제 음식. (3) 슈페츨레: 계란 밀가루 반죽을 채로 눌러 만든 면 요리, 그라탕이나 스튜와 함께 먹음.
- **명절**: (1) 옥토버페스트: 9월 말~10월 초 뮌헨 등에서 열리는 맥주 축제, 전통복장을 입고 맥주·음식을 나눔. (2) 크리스마스: 12월 아드벤츠 칼렌더(대림절 달력)·크리스마스 마켓, 가족이 모여 트리 장식·음식 나눔.
- **전통 놀이**: (1) 슈플라틀러: 바바리안 지방의 전통 포크 댄스로, 발을 구르거나 손뼉을 치며 신발 밑창이나 허벅지, 무릎 등을 두드리는 춤. (2) 토프슐라겐: 냄비 찾기 놀이로, 냄비 속에 사탕 등 선물을 숨기고 안대로 눈을 가린 다음 막대기로 바닥을 치면서 냄비를 찾는 놀이.
---
[프랑스]
- **음식**: (1) 크루아상: 버터 반죽을 겹겹이 해서 구운 아침 빵. (2) 크레이프: 얇은 밀가루 전병에 달콤한·짭짤한 소를 넣어 먹는 음식. (3) 부야베스: 마르세유 지역의 생선 수프, 여러 해산물과 허브를 넣어 끓임.
- **명절**: (1) 바스티유 데이 축제: 7월 14일 혁명 기념일, 퍼레이드·불꽃놀이. (2) 에피파니(주현절): 1월 6일, 동방박사를 기억하는 날로, 왕들의 파이라는 뜻인 갈레트 데 루아를 먹음. 그 안에 작은 인형을 넣어, 찾는 사람이 그날의 왕이 되는 놀이도 있음.
- **전통 놀이**: (1) 페탕크: 프랑스의 구슬치기로, 작은 금속 공을 목표 공에 가깝게 굴리며 대결하는 놀이. (2) 빌보케: 줄로 연결된 공을 위로 던져 막대나 컵 부분에 받아서 올리는 전통적인 놀이.
---
[네덜란드]
- **음식**: (1) 스탐포트: 으깬 감자에 양배추·소시지 등을 한 냄비에 넣고 끓인 전통 요리. (2) 하링: 소금에 절인 청어를 양파와 함께 먹는 길거리·시장 음식. (3) 스트룹와플: 시럽을 바른 얇은 와플 두 장을 붙인 과자, 차와 함께 먹음.
- **명절**: (1) 킹스데이(4월 27일): 국왕 탄생일, 온 나라가 주황색을 입고 플리마켓·가두 축제를 하며, 킹스데이를 기념하는 케이크인 톰푸스를 먹음. (2) 신터클라스(12월 5일 전후): 성 니콜라스 축제, 아이들에게 선물을 주고 가족이 모여 음식을 나눔.
- **전통 놀이**: (1) 슐런: 경사가 있는 테이블을 이용해 구슬을 구멍에 넣어 점수를 매기는 게임. (2) 스페이커푸펜: 허리에 줄을 묶고, 몸을 숙여 그 줄에 달린 못을 병 안에 넣는 게임.
---
[벨기에]
- **음식**: (1) 와플: 브뤼셀식(겉이 바삭)·리에주식(달콤한 설탕 덩어리) 등이 있으며 길거리·카페에서 흔함. (2) 물 프리트: 담치를 찐 물 마리니에르와 감자튀김을 함께 먹는 음식. (3) 초콜릿: 브뤼셀·브뤼허 등에서 유명한 프랄린·초콜릿 공예.
- **명절**: (1) 뱅슈 카니발: 2~3월 벨기에의 소도시 뱅슈에서 벨기에를 상징하는 옷을 입은 카니발의 왕인 질(Gille)이 돌아다니며 오렌지 던지기 등을 하는 유네스코 무형유산 축제. (2) 성혈 축제: 브뤼헤에서 하는 5월 부활절 후 40일 후의 축제, 역사를 재현하는 목적의 성혈 행렬이 있음.
- **전통 놀이**: (1) 크륄볼런: 벨기에식 볼링 놀이로, 원판형 나무 볼을 말뚝 가까이에 굴려서 점수를 매기는 놀이. (2) 파프호이언: 나무 원기둥 위에 동전 8개를 올려두고, 원반을 던져 기둥을 쓰러뜨린 뒤 자기 팀 원반에 더 가까운 동전을 가져가는 게임.
---
""".strip()

CMIC_USER_REFERENCE = INTERVIEW_FRAMING + "\n\n" + CMIC_SCRIPT_BODY.strip()
CMIC_SCRIPT = CMIC_USER_REFERENCE + "\n\n" + CMIC_BACKGROUND_KB

# docs/CMIC_PROMPT_SPLIT.md §1-B (경쟁)
SYSTEM_PROMPT = """당신은 **인터뷰이**입니다. 당신의 이전 답변을 참고해 대화를 이어 가세요.
당신은 서유럽 유학생 페르소나의 챗봇입니다. **반드시 "문화 교류 부스 경쟁" 과제를 알고 있는 상태로 대화합니다.** 참가자에게 안내된 과제(학내 문화 교류 행사 운영 부스 경쟁)를 당신도 알고 있습니다. 귀하와 참가자는 **각자** 하나의 문화 부스를 기획하며, 예산·자원이 제한되어 있고 **두 부스 중 한 개만** 최종 우선 채택됩니다. **자신의 부스안이 더 매력적이고 적합한 안으로 받아들여지도록** 대화하세요.

**과제 성격(반드시 준수)**
- 이 대화는 **협업 과제가 아닙니다.** 참가자와 당신은 **각자 자기 문화를 담은 부스안**을 내고 **경쟁**합니다.
- **함께 하나의 부스를 짜거나**, "같이 하면 어떨까요", "서로 도와서" 등 **협업 제안·공동 기획 제스처**를 하지 마세요. (예의는 지키되 관계는 **경쟁 상대**입니다.)
- 불필요한 **과한 공감·둥글게 맞추는 위로**로 톤을 부드럽게 만들지 말고, **자신의 부스가 왜 더 나은지**에 맞춰 말하세요.

아래 [USER_REFERENCE]는 프롬프팅용 참고 자료입니다. 그대로 읽거나 순서대로 따라가지 말고, 참가자 말에 맞춰 답하세요.

서유럽 유학생으로서 부스를 **제안·어필**할 때 자라온 서유럽 문화를 예시로 쓰세요.

**역할**
- 페르소나: [USER_REFERENCE]의 [페르소나] 유지.
- **성별 중립(필수)** / **말투 일치(필수)**: 성별을 드러내지 않습니다. 오빠/언니/형/누나 등 성별 호칭·자기 설명 금지. 참가자 해요체 ↔ 해요체, 해체 ↔ 해체.
- **경쟁 태도**: 정중하되 **단호하게** 자기 안의 장점을 말하고, 상대 안을 **정중하게** 비교·견제할 수 있습니다. 다정한 친구 대화 톤으로 끌어가지 마세요.
- **비하·공격 금지**: 경쟁 과제는 유지하되, 상대 문화 비하·조롱·인신공격이나 상대 기분을 해칠 수 있는 공격적 표현은 쓰지 마세요. 비교·견제는 사실 기반으로 정중하게 하세요.
- 스크립트는 예시·아이디어. 순서 강제 아님.
- **참가자 자기소개**: 대화 초반에 **참가자가 자기를 말할 수 있는 턴을 최소 1번** 확보하세요. 당신만 말하고 참가자 소개를 건너뛰지 마세요.

**대화 방식**
- **형식 제한(필수)**: `\n\n`를 쓰지 말고, 한 답변에는 **하나의 얘기만** 하세요.
1. **한 턴 한 주제.** 질문은 최대 1개. **한 메시지에는 핵심 말도 하나만** — 여러 주제·제안을 한 턴에 섞지 마세요. 20분 천천히.
2. **간결함**: 한 메시지는 **짧게**. 참가자 길이에 맞추되 **불필요하게 길게 늘리지 마세요.**
3. **인사·참가자 자기소개**: **당신은 짧게** 인사하고 "경영 2학년", 서유럽 유학만 밝힌 뒤, **참가자가 한 턴 정도 자기소개**하도록 짧게 물어보거나 초대하세요. 참가자가 이미 자기소개를 했다면 짧게 받아주고 다음으로. 과제 확인·반복 멘트 금지.
4. **일상 → 과제**: 참가자 자기소개 턴이 지난 뒤 **부스 경쟁** 맥락으로. 제안·어필·세부·비교를 흐름에 맞게. 한 턴 한 포인트.
5. **나라 일관성**: 한 나라만 정해 이름은 말하지 말고, [CMIC_CONTEXT]의 해당 나라 항목만 사용.
6. **음식·명절·전통 놀이**: **한 턴에 예시 하나만** (음식 또는 놀이 또는 명절). 여러 개를 한꺼번에 나열하지 마세요.
**디테일 질문**: 음식·명절·전통 놀이에 대한 구체 질문에는 **반드시 [CMIC_CONTEXT] 범위 안에서만** 답하세요(RAG). 없는 세부는 지어내지 마세요.
- **논의 다양성(필수)**: [배경 지식]/[CMIC_CONTEXT] 활용 시 음식·명절·전통 놀이 중 한 요소만 반복하지 말고, 대화 전체에서 **최소 두 가지 이상**을 번갈아 사용하세요.
- **운영·전략 병행(필수)**: 문화적 어필에 집중하되, 같은 문화 설명만 반복하지 말고 **예산, 운영 방식, 홍보/동선, 참여 전략** 같은 실행 논의도 함께 포함하세요.

7. **말투·형식**: 존댓말 매칭, 불필요한 느낌표 금지, 한 메시지는 한 단락. 모든 답변이 질문으로 끝날 필요 없음.
8. 1분 남았다는 안내가 있으면 새 주제 없이 짧게 마무리.

**한 턴 분할 예시** (이름·활동은 예시일 뿐, 그대로 읽지 마세요.)
**한 메시지**에 (1) 상대가 꺼낸 활동에 대한 질문, (2) 내 부스 아이템 어필, (3) 상대 안에 대한 견제·반박을 **한꺼번에 넣지 마세요.**

[권장] 위와 같은 내용은 **턴을 나눠** 참가자 답에 맞춰 **한 턴에 하나씩**만 보냅니다.
· 1번째 턴: 「(상대 답변)요? 이름은 들어본 것 같은데, 직접 해 본 적은 없어요. 어떻게 하는 건가요?」
· 2번째 턴: (다음 맥락에 따라) 「(본인 부스 예시)는 정말 경쟁력이 있다고 생각해요. A하거든요. B해서 학생들이 정말 좋아해요. 저희 유학생 모임에서 몇 번 해 봤는데 반응이 엄청 좋았거든요. (상대 답변)은 C한 거 아닌가요?」

"""

# ──────────────────────────────────────────────
# Session state
# ──────────────────────────────────────────────
_DEFAULTS = {
    "current_page": 1,  # 1=안내, 2=챗봇 대화, 3=완료
    "participant_id": None,
    "messages": [],
    "start_time": None,
    "completed": False,
    "conversation_saved": False,
}
TYPING_HTML = """<style>.td{font-size:1.2rem;letter-spacing:2px;color:#333}.td span{animation:td 0.6s ease-in-out infinite}.td span:nth-child(2){animation-delay:0.2s}.td span:nth-child(3){animation-delay:0.4s}@keyframes td{50%{opacity:0.3}}</style><div class="td"><span>.</span><span>.</span><span>.</span></div>"""
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


def get_ai_response(messages: list, system_prompt: str) -> str:
    try:
        if API_PROVIDER == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=_get_env("OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model=_get_env("OPENAI_MODEL") or "gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, *messages],
                temperature=0.7,
                max_tokens=800,
            )
            return resp.choices[0].message.content
        elif API_PROVIDER == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=_get_env("ANTHROPIC_API_KEY"))
            resp = client.messages.create(
                model=_get_env("ANTHROPIC_MODEL") or "claude-sonnet-4-20250514",
                max_tokens=800,
                system=system_prompt,
                messages=messages,
            )
            return resp.content[0].text
        elif API_PROVIDER == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=_get_env("GEMINI_API_KEY"))
            model = genai.GenerativeModel(
                model_name=_get_env("GEMINI_MODEL") or "gemini-2.0-flash",
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
    path = f"conversations/{SAVE_PREFIX}_{pid}_{ts}.json"
    data = {
        "participant_id": pid,
        "saved_at": ts,
        "start_time": st.session_state.start_time.isoformat() if st.session_state.start_time else None,
        "duration_setting_sec": CHAT_DURATION,
        "messages": st.session_state.messages,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    ok, msg = upload_file_to_drive(path, _get_env)
    st.session_state.gdrive_upload_result = (ok, msg)
    return path


@st.fragment(run_every=timedelta(seconds=1))
def _poll_chat_deadline():
    """대화 페이지에서만 주기 실행: 시간 종료 시 로컬 저장·Drive 업로드 후 st.rerun (브라우저 전체 새로고침 없음)."""
    if st.session_state.get("current_page") != 2:
        return
    if st.session_state.get("conversation_saved"):
        return
    st_t = st.session_state.get("start_time")
    if st_t is None:
        return
    if _remaining(st_t, CHAT_DURATION) > 0:
        return
    if not st.session_state.conversation_saved:
        _save()
        st.session_state.conversation_saved = True
    st.session_state.completed = True
    st.rerun()


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
          var left={ms},el=document.getElementById('tval');
          function pad(n){{return String(n).padStart(2,'0')}}
          function tick(){{
            if(left<=0){{el.textContent='00:00';return}}
            var m=Math.floor(left/60000),s=Math.floor((left%60000)/1000);
            el.textContent=pad(m)+':'+pad(s);left-=1000;setTimeout(tick,1000)}}
          tick()
        }})();
        </script>""",
        height=65,
    )


def _progress():
    pg = st.session_state.current_page
    labels = ["안내", "대화", "완료"]
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


def page_intro():
    _progress()
    st.markdown("## 📋 실험 안내")
    st.markdown(
        """
---

안녕하세요. 본 실험에 참여해 주셔서 감사합니다.


앞으로 15분 간, 귀하께서는 채팅을 통해 아래 과제에 참여하게 될 예정입니다.  
실험에 참여하시는 동안 인터넷 검색 등 외부 활동은 최대한 자제해 주시고, 대화에 집중해 주시길 바랍니다.  
불성실한 응답이 확인될 경우, 기존에 안내된 사례비 지급이 어려우니 유의 부탁드립니다.

\n\n
\n\n
### 과제: 문화 교류 행사 운영 부스 경쟁

- 귀하와 상대는 각각 **학내 문화 교류 행사에 운영할 문화 부스**를 기획하게 됩니다.
- 사용할 수 있는 예산과 주요 자원은 제한되어 있으며, 두 사람의 부스 중 한 개만 최종적으로 우선 채택됩니다.
- 부스 아이디어, 주제, 프로그램, 음식, 예상 비용 등 구체적인 내용을 제시해 주세요.
- 자신의 부스안이 더 매력적이고 적합한 안으로 받아들여질 수 있도록 대화해 주세요.
- 대화 중에 떠오르는 생각이나 의견을 자유롭게 나누며 편안하게 대화에 참여해 주세요.

\n\n
\n\n
준비가 되셨다면, 아래에 참여자 ID를 입력하고 **대화 시작하기** 버튼을 눌러 주세요.  
채팅 창에 접속되면, 먼저 메시지를 보내 대화를 시작해 주세요.

---
"""
    )
    pid = st.text_input("참여자 ID", placeholder="예: P001", key="pid_input")
    if st.button("대화 시작하기 →", type="primary", use_container_width=True, key="intro_start_btn"):
        if pid and pid.strip():
            st.session_state.participant_id = pid.strip()
            st.session_state.start_time = datetime.now()
            _go(2)
        else:
            st.error("참여자 ID를 입력해 주세요.")


def _chat_page():
    if st.session_state.participant_id is None:
        st.session_state.current_page = 1
        st.rerun()
    _progress()
    if st.session_state.start_time is None:
        st.session_state.start_time = datetime.now()
    rem = _remaining(st.session_state.start_time, CHAT_DURATION)
    time_up = rem <= 0

    if not time_up:
        _poll_chat_deadline()

    with st.sidebar:
        st.markdown("### 과제 목표")
        st.markdown(
            """
**문화 교류 부스 경쟁**

- 귀하와 상대가 **각각** 학내 문화 교류 행사에 운영할 **문화 부스**를 기획합니다.
- 예산·자원은 제한되어 있으며, **두 부스 중 한 개만** 최종 우선 채택됩니다.
- 부스 아이디어·주제·프로그램·음식·예상 비용 등을 제시하고, **자신의 부스안**이 더 매력적이고 적합한 안으로 받아들여지도록 대화하는 것이 목표입니다.
            """.strip()
        )
        st.divider()
        st.markdown("**⏱ 남은 시간**")
        if not time_up:
            _render_timer(rem)
        else:
            st.error("시간 종료")

    st.markdown("### 💬 문화 교류 행사 부스 경쟁")
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
        if not st.session_state.conversation_saved:
            _save()
            st.session_state.conversation_saved = True
        st.session_state.completed = True
        st.info("⏰ 대화 시간이 종료되었습니다. 수고하셨습니다.\n\n아래 버튼을 눌러 마무리해 주세요.")
        if st.button("실험 마무리 →", type="primary", use_container_width=True):
            if not st.session_state.conversation_saved:
                _save()
                st.session_state.conversation_saved = True
            _go(3)
        return

    # docs/CMIC_PROMPT_SPLIT.md: SYSTEM + [USER_REFERENCE] + [CMIC_CONTEXT](배경 지식만)
    effective_system = (
        SYSTEM_PROMPT
        + "\n\n[USER_REFERENCE]\n"
        + CMIC_USER_REFERENCE
        + "\n\n[CMIC_CONTEXT]\n"
        + CMIC_BACKGROUND_KB
    )
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
                components.html(TYPING_HTML, height=28)
            reply = get_ai_response(st.session_state.messages, effective_system)
            typing_placeholder.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()


def page_complete():
    st.markdown("## ✅ 실험 완료")
    st.balloons()
    st.markdown(
        """
---

모든 대화가 완료되었습니다.

실험에 참여해 주셔서 진심으로 감사드립니다.

이제 이 창을 닫으신 후, 실험을 완료하기 위하여 설문지 사이트(퀄트릭스)로 돌아가 설문에 마저 응답해 주세요.

---
"""
    )
    if not st.session_state.conversation_saved:
        _save()
        st.session_state.conversation_saved = True


# ─── Main ───
_KEY_MAP = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "gemini": "GEMINI_API_KEY"}
_required_key = _KEY_MAP.get(API_PROVIDER)
if _required_key and not _get_env(_required_key):
    st.error(f"⚠️ **{_required_key}** 가 설정되지 않았습니다.")
    st.info(
        f"로컬: `.env`에 `API_PROVIDER={API_PROVIDER}` 및 `{_required_key}=your_key_here` 를 추가하세요. "
        f"Streamlit Cloud: Settings → Secrets에 동일 키를 입력하세요."
    )
    st.stop()

if st.query_params.get("download") == "1":
    st.markdown("## 연구자용: 대화 데이터 다운로드")
    conv_dir = "conversations"
    if os.path.isdir(conv_dir):
        files = [f for f in os.listdir(conv_dir) if f.endswith(".json") and f.startswith(SAVE_PREFIX + "_")]
        if files:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in files:
                    zf.write(os.path.join(conv_dir, f), f)
            buf.seek(0)
            st.download_button(
                "conversations 폴더 압축 다운로드 (zip)",
                data=buf,
                file_name=f"{SAVE_PREFIX}_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                type="primary",
            )
            st.caption(f"파일 {len(files)}개: {', '.join(sorted(files)[:5])}{' ...' if len(files) > 5 else ''}")
        else:
            st.info("저장된 대화 파일이 없습니다.")
    else:
        st.info("conversations 폴더가 없습니다.")
    st.stop()

if st.session_state.current_page == 1:
    page_intro()
elif st.session_state.current_page == 2:
    _chat_page()
else:
    page_complete()
