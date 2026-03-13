import requests
import os
from datetime import datetime

# 환경 변수 가져오기
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # 검색 쿼리를 단순하게 변경하여 결과가 나올 확률을 높입니다.
    url = f"https://newsapi.org/v2/everything?q=경제&language=ko&sortBy=publishedAt&pageSize=5&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get('articles', [])
        
        # 기사가 있을 경우에만 포맷팅
        if articles:
            return "\n".join([f"제목: {a['title']}\n링크: {a['url']}\n" for a in articles])
        return None
    except:
        return None

def get_briefing():
    news_data = get_real_news()
    
    # 만약 NewsAPI에서 데이터를 못 가져오면, AI에게 '일반적인 경제 정보'를 작성하라고 시킵니다.
    if news_data:
        prompt = f"다음 뉴스 리스트를 바탕으로 경제 브리핑을 작성하세요:\n{news_data}\n\n"
    else:
        prompt = "최근 실시간 경제 뉴스 데이터가 없습니다. 현재 시장 상황과 투자자가 주의해야 할 일반적인 경제 지표(금리, 환율 등)에 대해 브리핑해 주세요.\n\n"

    prompt += (
        "규칙: \n"
        "1. 개인 정보(직장, 거주지 등) 언급 금지\n"
        "2. 7개 섹션(핵심/부동산/주식/IT/글로벌/재테크/기술)별 작성\n"
        "3. 뉴스 데이터가 있는 경우에만 링크를 표기"
    )
    
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "AI 생성 오류"

def send_telegram(text):
    message = f"☀️ <b>[경제 뉴스 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing_text = get_briefing()
    send_telegram(briefing_text)

