import requests
import os
from datetime import datetime

# 환경 변수
GROQ_KEY = os.environ.get('GROQ_API_KEY', '')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

def get_news():
    # 간단한 뉴스 검색 (NewsAPI 사용 시)
    try:
        # 무료 API 키가 있다면 사용, 없으면 빈 문자열 반환
        return "최신 부동산 및 IT 기술 트렌드: 잠실 르엘 분양 이슈 및 클라우드 인프라 자동화 동향"
    except:
        return "최신 금융/IT 뉴스"

def get_briefing():
    news = get_news()
    today = datetime.now().strftime("%Y년 %m월 %d일")
    prompt = (f"오늘은 {today}입니다. 싱글맘, 송도 풍림아이원(대출4억, 3.9%) 거주, 잠실 르엘 관심, "
              "씨티은행 IT 인프라 담당자(VMware/NAS/Wintel), GCP 자격증 준비 중인 투자자를 위한 브리핑.\n\n"
              f"참고 뉴스: {news}\n\n"
              "7개 섹션 작성: 1.핵심 요약 2.부동산 및 금리(송도/잠실) 3.주식 및 ETF 4.GCP 및 IT 커리어 "
              "5.글로벌 경제 6.생활 재테크 7.기술 트렌드(HBF 이슈). "
              "각 섹션 3~4줄, 전문적이고 따뜻한 톤으로 작성.")
    
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    if res.status_code != 200:
        raise Exception(f"Groq API 오류: {res.text}")
    return res.json()['choices'][0]['message']['content']

def send_telegram(text):
    today = datetime.now().strftime("%Y.%m.%d")
    # 제목 보완: 눈에 띄게 구성
    message = (f"☀️ <b>[오늘의 맞춤형 투자 브리핑]</b>\n"
               f"📅 {today}\n"
               "--------------------------\n"
               f"{text}\n"
               "--------------------------\n"
               "💡 <i>AI 자동 생성 | 투자 참고용</i>")
    
    res = requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", json=payload)
    print(f"텔레그램 응답 상태 코드: {res.status_code}") # 이 줄 추가
    print(f"텔레그램 응답 내용: {res.text}")           # 이 줄 추가

if __name__ == "__main__":
    briefing = get_briefing()
    send_telegram(briefing)
