import requests
import os
from datetime import datetime

GEMINI_KEY = os.environ.get('GEMINI_API_KEY', '')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

def get_briefing():
    today = datetime.now().strftime("%Y %m %d")
    prompt = ("오늘은 " + today + "입니다. "
        "아래 조건의 투자자를 위한 오전 7시 투자 브리핑을 작성해주세요. "
        "투자자 프로필: "
        "싱글맘 남아 2016년생 초등학생 자녀 1명. "
        "인천 송도 풍림아이원 1단지 거주 유일자산. "
        "담보대출 4억 금리 3.9%. "
        "잠실 르엘 관심 등기시점 및 관련뉴스 주목. "
        "씨티은행 IT 인프라 담당자 VMware NAS Wintel 운영. "
        "GCP 클라우드 자격증 준비중. "
        "다음 6개 섹션으로 작성: "
        "1.오늘의 핵심요약 오늘 꼭 알아야 할 투자이슈 3가지. "
        "2.부동산및금리 주담대금리동향 4억대출자시사점 송도풍림아이원1단지시세뉴스 잠실르엘최신뉴스 등기시점분양가입주일정 싱글맘1주택자절세및대출관리팁. "
        "3.주식및ETF 국내외주요지수동향 직장인소액투자가능ETF추천 싱글맘관점안정적투자전략. "
        "4.GCP및AI테크 GoogleCloud및AI산업동향 씨티은행기술트렌드 GCP자격증팁 인프라담당자커리어시사점. "
        "5.글로벌경제 미국연준금리정책 달러원환율동향 한국자산영향. "
        "6.오늘의생활팁 2016년생초등학생교육비절약투자팁 싱글맘재테크한줄조언. "
        "각섹션 3~4줄 간결하게. 따뜻하고 실용적인 톤으로 작성.")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + GEMINI_KEY
    res = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]})
    data = res.json()
    print("Gemini 응답 확인:", list(data.keys()))
    if 'candidates' not in data:
        error_msg = data.get('error', {}).get('message', '알수없는오류')
        raise Exception("Gemini API 오류: " + error_msg)
    return data['candidates'][0]['content']['parts'][0]['text']

def send_telegram(text):
    today = datetime.now().strftime("%Y.%m.%d")
    message = (
        "모닝 투자 브리핑\n"
        + today + "\n"
        + "송도 풍림아이원 1단지 | 잠실 르엘 | 씨티 IT\n"
        + "====================\n\n"
        + text
        + "\n\n===================="
        + "\nAI 자동 생성 | 투자 참고용"
    )
    res = requests.post(
        "https://api.telegram.org/bot" + TG_TOKEN + "/sendMessage",
        json={"chat_id": TG_CHAT_ID, "text": message}
    )
    print("텔레그램 응답:", res.json())

if __name__ == "__main__":
    print("브리핑 생성 중...")
    print("GEMINI_KEY 길이:", len(GEMINI_KEY))
    print("TG_TOKEN 길이:", len(TG_TOKEN))
    print("TG_CHAT_ID:", TG_CHAT_ID)
    briefing = get_briefing()
    send_telegram(briefing)
    print("전송 완료!")
