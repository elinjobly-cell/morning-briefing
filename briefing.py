import requests
import os
from datetime import datetime

# 환경 변수 가져오기
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # NewsAPI로 관련 뉴스 검색 (삼성전자, 부동산, 금리 등)
    url = f"https://newsapi.org/v2/everything?q=삼성전자 OR 부동산 OR 금리&domains=yna.co.kr,hankyung.com&language=ko&sortBy=publishedAt&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url).json()
        articles = res.get('articles', [])[:5]  # 최신 뉴스 5개만 가져오기
        news_text = "\n".join([f"- {a['title']}: {a['url']}" for a in articles])
        return news_text
    except Exception as e:
        return f"뉴스 검색 실패: {e}"

def get_briefing():
    news = get_real_news()
    today = datetime.now().strftime("%Y년 %m월 %d일")
        prompt = (
        f"오늘은 {datetime.now().strftime('%Y년 %m월 %d일')}입니다. "
        "사용자는 투자자로서 실시간 경제/기술 뉴스 브리핑을 원합니다.\n\n"
        "아래 제공된 뉴스 데이터를 참고하여, 다음 7개 섹션을 간결하고 전문적인 톤으로 요약하세요.\n"
        "각 항목 끝에는 반드시 해당 뉴스의 [뉴스 보기](URL) 링크를 포함해 주세요.\n\n"
        "1. [핵심 경제 뉴스] 오늘 시장을 움직일 가장 중요한 이슈\n"
        "2. [부동산 및 금리] 잠실 르엘, 송도 지역 등 부동산 주요 뉴스\n"
        "3. [주식 및 ETF] 주요 테마 및 투자 유의 종목\n"
        "4. [GCP 및 IT 커리어] 클라우드, VMware, 인프라 자동화 동향\n"
        "5. [글로벌 경제] 국제 지표 및 환율 이슈\n"
        "6. [생활 재테크] 실용적인 자산 관리 팁\n"
        "7. [기술 트렌드] 반도체/HBF 등 최신 기술 이슈\n\n"
        "참고 뉴스:\n{news}" # 위에서 NewsAPI로 가져온 news 데이터가 여기에 들어갑니다.
    )

    
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    if res.status_code != 200:
        raise Exception(f"Groq API 오류: {res.text}")
    return res.json()['choices'][0]['message']['content']

def send_telegram(text):
    message = f"☀️ <b>[오늘의 맞춤형 투자 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing = get_briefing()
    send_telegram(briefing)
