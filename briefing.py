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
        f"오늘은 {today}입니다. 싱글맘, 송도 풍림아이원(대출4억, 3.9%) 거주, 잠실 르엘 관심, "
        "씨티은행 IT 인프라 담당자(VMware/NAS/Wintel), GCP 자격증 준비 중인 투자자를 위한 경제 브리핑.\n\n"
        f"참고 뉴스 데이터:\n{news}\n\n"
        "위 뉴스와 키워드를 바탕으로 다음 7개 섹션을 3~4줄씩 작성해 주세요. 뉴스마다 끝에 [뉴스 보기](URL) 형식을 꼭 넣어주세요.\n"
        "1. 핵심 요약 2. 부동산 및 금리(송도/잠실) 3. 주식 및 ETF 4. GCP 및 IT 커리어 "
        "5. 글로벌 경제 6. 생활 재테크 7. 기술 트렌드(HBF 이슈)."
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
