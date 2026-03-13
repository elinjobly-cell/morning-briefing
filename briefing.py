import requests
import os
from datetime import datetime

# 환경 변수 가져오기
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # 연합뉴스(yna.co.kr)와 한국경제(hankyung.com)에서 경제 뉴스를 확실히 가져옵니다.
    url = f"https://newsapi.org/v2/everything?q=경제 OR 금리 OR 부동산&domains=yna.co.kr,hankyung.com&language=ko&sortBy=publishedAt&pageSize=10&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url).json()
        articles = res.get('articles', [])
        # 여기서 링크와 제목을 아예 문자열로 딱 붙여서 만듭니다.
        news_formatted = "\n".join([f"제목: {a['title']}\n링크: {a['url']}\n" for a in articles])
        return news_formatted
    except Exception as e:
        return f"뉴스 데이터 수집 실패: {e}"

def get_briefing():
    news_data = get_real_news()
    
    # 프롬프트: '창작' 금지, '제공된 데이터' 사용 강제
    prompt = (
        "아래 제공된 [뉴스 리스트]만 사용하여 경제 브리핑을 작성하세요.\n"
        "지시사항:\n"
        "1. 제공된 [링크]가 있는 기사만 언급하고, 제목과 링크를 그대로 붙여넣으세요.\n"
        "2. 절대 가짜 링크를 생성하지 마세요.\n"
        "3. 개인 신상 정보는 일절 언급하지 마세요.\n\n"
        "[뉴스 리스트]\n"
        f"{news_data}\n\n"
        "위 뉴스를 바탕으로 7개 섹션(핵심/부동산/주식/IT/글로벌/재테크/기술)별로 요약하세요."
    )
    
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    
    if res.status_code != 200:
        raise Exception(f"API 오류: {res.text}")
    
    return res.json()['choices'][0]['message']['content']

def send_telegram(text):
    message = f"☀️ <b>[경제 뉴스 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing = get_briefing()
    send_telegram(briefing)
