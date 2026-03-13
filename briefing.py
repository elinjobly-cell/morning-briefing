import requests
import os
from datetime import datetime

GROQ_KEY = os.environ.get('GROQ_API_KEY', '')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

def get_briefing():
    today = datetime.now().strftime("%Y %m %d")
    prompt = ("오늘은 " + today + "입니다. "
        "싱글맘 남아 2016년생 초등학생 자녀 1명. "
        "인천 송도 풍림아이원 1단지 거주 유일자산. "
        "담보대출 4억 금리 3.9%. "
        "잠실 르엘 관심 등기시점 및 관련뉴스 주목. "
        "씨티은행 IT 인프라 담당자 VMware NAS Wintel 운영. "
        "GCP 클라우드 자격증 준비중. "
        "위 투자자를 위한 오전 7시 투자 브리핑 작성. "
        "6개 섹션: 1.오늘의핵심요약 2.부동산및금리(송도풍림아이원1단지시세 잠실르엘등기시점) "
        "3.주식및ETF 4.GCP및AI테크 5.글로벌경제 6.오늘의생활팁(싱글맘재테크조언). "
        "각섹션 3~4줄. 따뜻하고 실용적인 톤.")
    headers = {
        "Authorization": "Bearer " + GROQ_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000
    }
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    data = res.json()
    print("Groq 응답 확인:", list(data.keys()))
    if 'choices' not in data:
        error_msg = data.get('error', {}).get('message', '알수없는오류')
        raise Exception("Groq API 오류: " + error_msg)
    return data['choices'][0]['message']['content']

def send_telegram(text):
    today = datetime.now().strftime("%Y.%m.%d")
    message = ("모닝 투자 브리핑\n" + today + "\n"
        "송도 풍림아이원 1단지 | 잠실 르엘 | 씨티 IT\n"
        "====================\n\n" + text
        + "\n\n====================\nAI 자동 생성 | 투자 참고용")
    res = requests.post(
        "https://api.telegram.org/bot" + TG_TOKEN + "/sendMessage",
        json={"chat_id": TG_CHAT_ID, "text": message}
    )
    print("텔레그램 응답:", res.json())

if __name__ == "__main__":
    print("브리핑 생성 중...")
    print("GROQ_KEY 길이:", len(GROQ_KEY))
    print("TG_TOKEN 길이:", len(TG_TOKEN))
    print("TG_CHAT_ID:", TG_CHAT_ID)
    briefing = get_briefing()
    send_telegram(briefing)
    print("전송 완료!")
