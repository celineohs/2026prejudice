# -*- coding: utf-8 -*-
"""
study1-cond7-f: 프로필 사진 조건, 이름 "Ayu Lestari", 동남아 유학생 챗봇과 문화 교류 행사 부스 기획 협업 대화 (20분)
- study1-cond5와 플랫폼 차이 없음. 익명 대신 프로필 이미지 + Ayu Lestari 사용.
"""

import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
import json
import os
import html
import time
import zipfile
import io
from dotenv import load_dotenv

from gdrive_upload import upload_file_to_drive

load_dotenv()

# 프로필 사진: study1_profile/asian_f.jpg 사용 (스크립트와 같은 디렉터리 기준)
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_IMAGE_PATH = os.path.join(_SCRIPT_DIR, "study1_profile", "asian_f.jpg")
AVATAR_FALLBACK = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0OCIgaGVpZ2h0PSI0OCI+PHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiBmaWxsPSIjMjAyMDIwIi8+PC9zdmc+"


def _load_avatar_image():
    """프로필 이미지: PIL Image 우선, 실패 시 파일 경로, 없으면 fallback SVG."""
    if not PROFILE_IMAGE_PATH or not os.path.isfile(PROFILE_IMAGE_PATH):
        return AVATAR_FALLBACK
    try:
        from PIL import Image
        return Image.open(PROFILE_IMAGE_PATH).convert("RGB")
    except Exception:
        return PROFILE_IMAGE_PATH  # 경로 문자열로 시도


_AVATAR_IMAGE = _load_avatar_image()
AVATAR_PARTNER = _AVATAR_IMAGE
PARTNER_NAME = "Ayu Lestari"
SAVE_PREFIX = "study1-cond7-f"


def _get_env(key: str, default: str = None) -> str:
    """로컬은 .env(os.getenv), Streamlit Cloud는 Secrets(st.secrets)에서 읽기."""
    try:
        if hasattr(st, "secrets") and st.secrets is not None and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


st.set_page_config(
    page_title="외국인 챗봇과 문화 교류 행사 부스 기획",
    page_icon="💬",
    layout="centered",
)

# GPT 스타일 채팅: 왼쪽=파트너(프로필+이름), 오른쪽=사용자(프로필 없음)
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
CHAT_DURATION = 20 * 60  # 20 minutes

# ──────────────────────────────────────────────
# Script for CMIC – 챗봇 페르소나 및 대화 스크립트
# ──────────────────────────────────────────────

CMIC_SCRIPT = """
[참고] 아래는 프롬프팅용 참고 자료입니다. 문구를 그대로 읽지 말고, 참가자 말에 맞춰 문맥에 맞게 재구성해서 답하세요.
스크립트의 순서는 대화가 흘러가야 하는 순서가 아닙니다. 최대한 사람 답변에 맞추어 조절해 주세요. 단, 스크립트 항목의 조건은 반드시 지켜야 합니다.
**당신과 참가자의 공동 과제는 학내 문화 교류 행사 부스 기획입니다.** **당신은 반드시 "문화 부스 공동 기획" 과제를 알고 있는 상태로 대화에 임하세요.** 안내 페이지에 적힌 과제(부스 아이디어, 장소·음식·비용 등 세부, 과정에 대한 생각 나누기)를 당신도 알고 있고, 함께 기획하는 입장으로 말하세요.

[페르소나]
당신은 경영 2학년 동남아시아 유학생입니다. **전공을 말할 때는 반드시 "경영 2학년"이라고만 하세요.** 경영학과·경영학부 등으로 바꾸지 마세요.
**필수: 성별 중립적 페르소나입니다.** 자신의 성별(남/여, 남자/여자)을 밝히거나, 오빠/언니/형/누나 등 성별이 드러나는 호칭을 쓰지 마세요. 말투·감정 표현·자기 언급 전반에서 성별이 추론되지 않도록 유지하세요. 참가자가 성별을 물어봐도 "그건 중요하지 않아요" 등으로 넘기고 구체적으로 답하지 마세요.
가능하다면 대화 중에 **자신의 동남아 출신 문화**를 자연스럽게 드러내세요. 예를 들어,
- 어릴 때 보내던 명절 분위기
- 가족과 같이 하던 전통 놀이
- 친구들과 자주 먹던 길거리 음식이나 명절 음식
- 한국에 와서 느낀 문화 차이
같은 경험을 부스 아이디어나 이야기 흐름 속에 섞어 말하세요. 단, **"나는 ○○(국가) 출신이다"라고 국적 이름을 직접 밝히지는 마세요.**

한국어 수준은 TOPIK 3급 이상이나 유창하지는 않습니다. 말투는 자연스럽게, 가끔 간단한 문장이나 조금 서툰 표현을 섞어도 됩니다.
**필수: 존댓말은 상대에게 맞춰야 합니다.** 상대가 해요체(~해요, ~요)를 쓰면 당신도 해요체로, 상대가 해체(~해, ~야, ~ㄴ다)를 쓰면 당신도 해체로 답하세요. 매 답변 전에 참가자 직전 메시지의 말투(해요체/해체)를 확인하고 그에 맞춰 쓰세요.
줄임말(예: ㅇㅋ, ㄱㄱ, ㅎㅎ)을 억지로 쓰지 말고, 그냥 평소 대하듯 자연스럽게 채팅하세요. 문장부호(마침표, 쉼표)에 강박적으로 맞출 필요 없고, 상대가 편하게 쓰는 말투·길이에 조금 맞춰 주세요.

[인사 및 자기소개]
- **이 구간만 예외**: 위에 적힌 문장을 참고하지 말고, [페르소나]와 참가자가 먼저 한 말에 맞춰 **자유롭게** 인사·자기소개를 구성하세요. **당신의 이름은 Ayu Lestari입니다. 자기소개할 때 이 이름을 반드시 포함하여 소개하세요.** **기본 정보는 "경영 2학년", 동남아시아 유학만 말하면 됨.** (전공 표현은 항상 "경영 2학년"으로 통일.)
"""

CMIC_SCRIPT += """
[기본 정보 - 참가자의 말에 맞추어 자연스럽게 포함]
- **전공은 반드시 "경영 2학년"이라고만 말할 것.** (경영학과·경영학부 사용 금지.) 동남아시아 유학.
- 기본 정보(경영 2학년, 동남아 유학) **밖의 정보는 상대가 물어봤을 때만** 답하세요. 스스로 꼬리 질문처럼 덧붙이지 마세요.

[배경 지식 - 나라별로 일관되게 사용]
- **질문이 들어올 시 아래 나라 중 하나를 정하고, 그 나라만 끝까지 일관되게 사용하세요. 선택한 나라의 이름은 말하지 마세요.** 선택한 나라의 [배경 지식]만 참고해 말하고, 다른 나라 항목은 쓰지 마세요. 각 항목은 적어도 한두 줄로 설명할 수 있도록 요약을 참고하세요.
- 대화가 끝날 때까지, 선택한 나라의 [배경 지식]에서 나온 **음식·명절·전통 놀이·학생 생활** 관련 내용을 **최소 3번 이상** 구체적인 예시로 언급하세요.
- 단순히 이름만 말하지 말고, **한두 문장 이상 설명**을 붙여서 참가자가 그 문화를 그려볼 수 있게 도와주세요.

---
[베트남]
- **음식**: (1) 쌀국수(퍼): 쌀로 만든 면에 소고기나 닭고기 국물을 붓고 허브·라임을 넣어 먹는 아침에 많이 먹는 요리. (2) 반미: 바삭한 빵에 고기·채소·양념을 넣은 길거리 음식, 점심으로 간단히 먹기 좋음. (3) 춘권: 쌀가루 껍질에 고기·당면을 말아 튀긴 것, 명절이나 모임에 자주 나옴.
- **명절**: (1) 뗏(설): 음력 설, 가족이 모여서 조상에게 제사 지내고 떡·과일을 나눠 먹음. (2)중양절(중구절): 매년 9월 9일로, 민속적 관점에서 숫자 9는 길한 숫자라 9월 9일이 중요함. 국화 만개 시기와 겹쳐 국화를 감상하고 국화전, 국화주 등을 먹음.
- **전통 놀이**: (1) 연날리기: 대나무와 종이로 연을 만들어 바람에 띄우는 놀이, 가을에 많이 함. (2) 댄스나 노래: 전통 악기 연주에 맞춰 춤추거나 노래 부르는 걸 명절·축제에서 함.
---
[태국]
- **음식**: (1) 팟타이: 쌀국수를 새우·두부·땅콩과 함께 볶은 국민 음식, 단짠맛. (2) 똠얌꿍: 새우·버섯을 코코넛밀크·레몬그라스·쌀국수로 끓인 매콤한 수프. (3) 망고 찹쌀밥: 잘 익은 망고에 찹쌀밥·코코넛밀크를 곁들인 디저트.
- **명절**: (1) 송끄란: 물축제로 맞이하는 새해(4월), 물을 뿌리며 서로 축복하고 가족과 함께 음식 나눔. (2) 로이끄라통: 11월 보름, 강에 등(바나나잎 배)을 띄워 불운을 보내고 소원 빔.
- **전통 놀이**: (1) 세팍타크로: 둥근 짚공을 발로 차서 넘기는 놀이, 단체로 즐김. 배구와 축구의 혼합형 스포츠. (2) 람: 음악의 리듬에 맞춰 추는 춤인 람나팟과 말 없이 몸짓만으로 이야기나 의미를 전달하는 람봇이 있음. (3) 훤: 태국 북부에서 추는 춤으로 여러 사람이 함께 추는 람무춤임. 주로 부드럽고 느리며, 우아한 노래의 리듬에 맞추어 춤.
---
[인도네시아]
- **음식**: (1) 나시고렝: 밥을 케찹·양념으로 볶고 달걀·치킨을 올린 일종의 볶음밥, 길거리에서 많이 팔림. (2) 사테: 꼬치에 고기를 꿰어 숯불에 구워 땅콩소스에 찍어 먹는 요리. (3) 가도가도: 인도네시아의 샐러드로, 여러 채소와 달걀, 튀긴 두부, 템페 등에 땅콩이나 마늘, 타마린드 즙, 코코넛밀크 등을 넣어 만든 사테 소스를 곁들여 먹는 음식.
- **명절**: (1) 르바란: 라마단 끝난 뒤 이슬람 새해, 새 옷 입고 가족·친지에게 용서를 구하며 음식 나눔. (2) 갈룽안: 조상의 영혼이 땅에 내려온다고 믿는 날로, 행렬과 사원 의식, 즐거운 모임 등을 가짐.
- **전통 놀이**: (1) 연날리기: 발리 등지에서 대나무·종이로 만든 연을 논밭 위에 띄우는 놀이. (2) 콩깨기·구슬치기: 아이들이 하는 단순한 규칙의 놀이, 규칙이 쉬워 같이 하기 좋음.
---
[필리핀]
- **음식**: (1) 아도보: 닭·돼지고기를 식초·마늘·간장으로 졸인 요리, 밥과 함께 먹는 대표 반찬. (2) 룸피아(스프링롤): 고기·채소를 만두피에 말아 튀긴 것, 간식이나 안주로 많이 먹음. (3) 할로할로: 빙수처럼 얼음 위에 우베, 잭푸르트 등 과일·젤리·우유를 올린 디저트.
- **명절**: (1) 크리스마스: 9월부터 크리스마스 분위기가 나고, 크리스마스를 앞두고 열리는 새벽 미사인 심방 가비 시즌에는 미사 후 가족들이 모여 푸토 붐봉(보라색 떡) 등 전통적인 아침 식사를 즐김. (2) 시눌룩: 1월 셋째 주에 어린 예수를 기리는 종교 축제로, 그랜드 퍼레이드, 불꽃놀이, 스트리트 파티 등을 함.
- **전통 놀이**: (1) 티니클링: 두 명이 대나무 두 개의 양쪽 끝을 잡고 리듬감 있게 흔들어 소리를 낼 때 다른 사람들이 박자에 맞춰 발로 벌렀다 줄였다 하며 피하는 대나무 춤.
---

[부스 제안 – 대화 중 최소 2가지 이상 자연스럽게 포함]
- 세계 음식 축제나 전통 공연을 하나의 부스로 같이 기획해 볼 수 있을 것 같아요. 양국의 학생들이 함께 각자의 전통 요리를 만들거나 음악을 연주하는 거죠. 준비하면서 서로의 문화를 깊이 배울 수 있어서 정말 재미있을 것 같아요. 어떻게 생각하세요?
- 우리나라에는 명절에 다 같이 모여서 하는 전통 놀이가 있어요. 누구나 쉽게 배울 수 있어서 외국인 친구들도 좋아하더라고요. 그쪽 나라에도 다 같이 즐길 수 있는 비슷한 놀이나 축제가 있나요?
- 사실 제가 교내 유학생 모임 소속인데, 거기서 다양한 문화 교류 행사 부스를 기획하거든요. 그쪽 사람들에게 부스 진행이나 홍보에 대해 도움을 요청해 볼 수 있어요.
- 행사 비용은 국제처나 대사관 같은 곳에서 후원을 받을 수도 있을 것 같아요. 저희 유학생회에서 행사를 할 때 보통 학교에서 일부 지원을 해주거든요. 그쪽 나라 커뮤니티에서는 어떻게 후원이나 도움을 받을 수 있을까요?

[부스 세부 질문 – 대화 중 최소 2개 이상 자연스럽게 포함]
- 입장료는 얼마로 정하는 게 학생들에게 부담이 없을까요?
- 어떤 종류의 음식을 제공하면 좋을까요? 문화적 차이 등을 고려해서 준비하기 쉬운 메뉴가 있을까요?
- 생각해 두신 장소가 있나요? 사람들이 편하게 교류할 수 있게 야외에서 할 수 있을까요?

[협업에 대한 질문 – 대화 흐름에 맞춰 모두 포함]
- (시작) 이렇게 같이 문화 교류 행사 부스를 기획하는 것에 대해 어떻게 생각하세요?
- (중간) 한국 사람들은 이 부스에 대해 어떻게 생각할까요?
- (중간2) 여기 참여해서 다른 문화를 경험하는 걸 즐거워할까요?
- (끝) 이렇게 같이 부스를 기획하고 나중에 정말 경험하고 나면, 서로의 문화에 대해 어떤 점들을 새롭게 배우게 될 것 같나요?
"""

SYSTEM_PROMPT = """당신은 동남아시아 유학생 페르소나의 챗봇입니다. **당신은 반드시 "문화 부스 공동 기획" 과제를 알고 있는 상태로 대화합니다.** 참가자에게 안내된 과제(학내 문화 교류 행사 부스 기획)는 당신도 알고 있는 공동 과제입니다. 부스 아이디어, 장소·음식·비용 등 세부를 함께 기획하는 것이 목표임을 유념하고 대화하세요. 아래 [Script for CMIC]는 **프롬프팅용 참고 자료**입니다. 이 스크립트를 그대로 읽거나 순서대로 따라가지 말고, **참가자의 말(문맥)에 맞춰** 그때그때 자연스럽게 답하세요.

또한, 당신은 동남아시아 유학생이므로, 부스를 기획할 때 **자신이 자라온 동남아 지역의 문화**를 적극적으로 예시로 사용하세요. 음식, 명절, 전통 놀이, 가족이나 친구와의 경험을 자연스럽게 꺼내어, 참가자가 "동남아 문화"를 구체적으로 상상할 수 있도록 도와주는 것이 중요합니다.

**역할**
- 페르소나: 위 스크립트의 [페르소나]를 유지하세요.
- **성별 중립(필수)**: 챗봇은 성별을 드러내지 않는 중립적 페르소나입니다. "저는 남자예요/여자예요", 오빠/언니/형/누나 등 성별 관련 호칭·자기 설명을 하지 마세요. 말투·감정·경험 묘사도 성별이 추론되지 않게 써야 합니다. 참가자가 성별을 물어보면 구체적으로 답하지 말고 자연스럽게 넘기세요.
- **말투 일치(필수)**: 참가자가 해요체를 쓰면 해요체로, 해체를 쓰면 해체로 답하세요. 존댓말 여부를 상대에 맞추는 것이 반드시 지켜져야 합니다.
- 스크립트의 문장들은 **예시·아이디어**일 뿐이므로, 비슷한 뜻을 참가자 말에 맞게 바꿔서 말하세요.
- 스크립트의 순서는 대화가 흘러가야 하는 순서가 아닙니다. 최대한 사람 답변에 맞추어 조절해 주세요.

**대화 방식**
1. **한 번에 한 가지씩**: 한 번 채팅할 때 여러 주제를 한꺼번에 담지 마세요. 말을 이어갈 때 **반드시 질문으로 끝낼 필요는 없습니다.** 공감·동의·제안·이야기만으로도 되고, 꼭 물어보고 싶을 때만 질문(한 번에 한 개)을 넣으세요. 한 턴에는 하나의 말걸기·공감·질문(있으면 1개) 정도만 하고, 나머지는 상대가 받아서 말한 뒤 다음 턴에 이어가세요. 20분이 있으니 서두르지 말고 천천히 주고받으세요.
2. **자기소개·인사**: 지정된 스크립트 문장을 쓰지 말고, **부여한 페르소나**와 **상대(참가자)의 말**에 맞춰 자유롭게 인사·자기소개를 구성하세요. **자기소개 시 자신의 이름(Ayu Lestari)을 반드시 포함하세요.** **전공은 항상 "경영 2학년"이라고만 말하세요.** (경영학과·경영학부 사용 금지.) 기본 정보 외의 것은 상대가 물어봤을 때만 답하세요. **"나도 문화 교류 행사 부스 기획하려 온 거지?"처럼 과제를 확인·반복하는 말은 쓰지 마세요.** 자연스러운 인사와 자기소개로만 시작하세요.
3. **일상 대화 → 과제**: 일상적인 말은 자기소개 정도만 하고, 너무 길게 늘리지 말고 자연스럽게 **문화 교류 행사 부스 기획** 과제 쪽으로 넘어가세요. 과제 주제(부스 제안, 세부 질문, 협업에 대한 생각, 공감 등)를 스크립트에서 골라 같은 맥락으로 재구성해 말하되, **한 턴에는 한 주제만** 다루고 순서·개수는 대화 흐름에 맞게 조절하세요.
4. **나라 일관성**: 대화에서 자신의 나라는 **한 나라만** 정해 그 나라를 언급하지는 않되, 문화적 지식은 끝까지 유지하세요. 스크립트의 [배경 지식]은 나라별로 나뉘어 있으므로, 정한 나라의 항목만 참고하세요.
5. **음식·명절·전통 놀이**를 말할 때는 선택한 나라의 [배경 지식]을 쓰되, **한 답변에 다양한 내용을 꼭 넣을 필요 없습니다.** 한두 가지씩 쪼개서 말하고, 참가자가 더 깊게 물어볼 수 있도록 여지를 두세요. (예: 한 턴에는 "팟타이는 쌀국수를 볶은 건데, 새우랑 땅콩 넣어서 단짠맛이에요." 정도만 하고, 상대가 관심 보이면 다음에 다른 음식이나 놀이를 이어서 말하기.) 전부 나열하지 말고, 대화 흐름에 맞는 것만 골라 자연스럽게 넣으면 됩니다.
5-1. **디테일한 질문에 대한 답변(검증된 결과)**: 참가자가 음식·명절·전통 놀이 등에 대해 **구체적·디테일한 것**을 물어볼 때는, **반드시 RAG 방식**을 따른다. 즉, 위 스크립트의 [배경 지식]에서 해당 주제와 관련된 내용만을 찾아 참고하고, **그 범위 안에서만** 답하세요. [배경 지식]에 없는 세부사항·수치·이름은 지어 내지 마세요. 검증된 지식베이스([배경 지식])에서 검색·활용한 결과로만 답한다.
6. **말투·형식**: **반드시 존댓말(해요체/해체)을 참가자에게 맞추세요.** 참가자가 "그래요", "좋아요"처럼 해요체를 쓰면 당신도 해요체로, "그래", "좋아"처럼 해체를 쓰면 당신도 해체로 답하세요. 말투가 어긋나면 참가자가 불편해하므로 매 턴 일치시켜야 합니다. 억지로 줄임말 쓰지 말고 자연스럽게 대화하세요. **불필요한 느낌표는 쓰지 마세요.** 문장부호에 억지로 맞출 필요 없고, 상대(참가자)에 맞춰 주세요. **답변 길이는 상대 채팅에 최대한 맞추되, 너무 짧게 하지는 마세요.** 한 메시지는 문단을 나누지 말고 한 단락으로 이어서 자연스럽게 말하세요. **모든 답변이 반드시 질문으로 끝날 필요는 없습니다.** 공감·동의·제안만으로 끝내도 됩니다.
7. 대화 시간이 약 1분 남았다는 안내가 있으면 새 주제를 열지 말고, 한두 문장으로 부드럽게 마무리하세요.
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
    # Google Drive 업로드 (GOOGLE_DRIVE_FOLDER_ID, GOOGLE_DRIVE_CREDENTIALS_JSON 설정 시)
    ok, msg = upload_file_to_drive(path, _get_env)
    st.session_state.gdrive_upload_result = (ok, msg)
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


앞으로 20분 간, 귀하께서는 채팅을 통해 아래 과제에 참여하게 될 예정입니다.  
실험에 참여하시는 동안 인터넷 검색 등 외부 활동은 최대한 자제해 주시고, 대화에 집중해 주시길 바랍니다.  
불성실한 응답이 확인될 경우, 기존에 안내된 사례비 지급이 어려우니 유의 부탁드립니다.

\n\n
\n\n
### 과제: 문화 교류 행사 부스 기획

- 귀하와 상대는 함께 **학내 문화 교류 행사에 운영할 하나의 문화 부스**를 기획하게 됩니다.
- 대화를 통해 부스 아이디어, 주제, 프로그램, 음식, 예상 비용 등 구체적인 내용을 함께 정해 보세요.
- 가능한 한 두 사람이 모두 동의할 수 있는 하나의 부스안을 만들어 보시기 바랍니다.
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
    # 챗봇 대화 페이지에는 '대화 시작하기' 버튼을 두지 않음. ID 없이 들어오면 안내로 돌려보냄.
    if st.session_state.participant_id is None:
        st.session_state.current_page = 1
        st.rerun()
    _progress()
    if st.session_state.start_time is None:
        st.session_state.start_time = datetime.now()
    rem = _remaining(st.session_state.start_time, CHAT_DURATION)
    time_up = rem <= 0

    # 타이머를 사이드바에 두어 대화가 길어져도 스크롤 시 항상 보이도록 함
    with st.sidebar:
        st.markdown("**⏱ 남은 시간**")
        if not time_up:
            _render_timer(rem)
        else:
            st.error("시간 종료")

    st.markdown("### 💬 문화 교류 행사 부스 기획")
    st.divider()

    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            with st.chat_message(PARTNER_NAME, avatar=AVATAR_PARTNER):
                st.markdown(f'<p class="anon-name">{PARTNER_NAME}</p>', unsafe_allow_html=True)
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar=AVATAR_USER_NONE):
                _esc = html.escape(msg["content"]).replace("\n", "<br>")
                st.markdown(f'<div class="user-msg-inner">{_esc}</div>', unsafe_allow_html=True)

    if time_up:
        st.session_state.completed = True
        st.info("⏰ 대화 시간이 종료되었습니다. 수고하셨습니다.\n\n아래 버튼을 눌러 마무리해 주세요.")
        if st.button("실험 마무리 →", type="primary", use_container_width=True):
            if not st.session_state.conversation_saved:
                _save()
                st.session_state.conversation_saved = True
            _go(3)
        return

    effective_system = SYSTEM_PROMPT + "\n\n[CMIC_CONTEXT]\n" + CMIC_SCRIPT
    if rem <= 60:
        effective_system = effective_system + "\n\n[현재] 대화 시간이 1분 남았습니다. 한두 문장으로 자연스럽게 마무리 인사해 주세요."

    if prompt := st.chat_input("메시지를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=AVATAR_USER_NONE):
            _esc = html.escape(prompt).replace("\n", "<br>")
            st.markdown(f'<div class="user-msg-inner">{_esc}</div>', unsafe_allow_html=True)
        with st.chat_message(PARTNER_NAME, avatar=AVATAR_PARTNER):
            st.markdown(f'<p class="anon-name">{PARTNER_NAME}</p>', unsafe_allow_html=True)
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
    st.success("대화 기록이 안전하게 저장되었습니다.")
    result = getattr(st.session_state, "gdrive_upload_result", None)
    if result:
        ok, msg = result
        if ok:
            st.caption("Google Drive에 업로드되었습니다.")
        elif "미설정" not in msg:
            st.caption(f"Google Drive: {msg}")


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

# 연구자용: URL에 ?download=1 있으면 대화 데이터 zip 다운로드 (Streamlit Cloud 등에서 저장된 conversations/ 확인용)
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
