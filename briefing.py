import requests
import os
from datetime import datetime

# 환경 변수 가져오기
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # NewsAPI로 경제 관련 핵심 뉴스 검색
    url = f"https://newsapi.org/v2/everything?q=경제 OR 부동산 OR 증시&domains=yna.co.kr,hankyung.com&language=ko&sortBy=publishedAt&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url).json()
        articles = res.get('articles', [])[:5]
        news_list = "\n".join([f"- {a['title']}: {a['url']}" for a in articles])
        return news_list
    except Exception as e:
        return f"뉴스 데이터 없음: {e}"

def get_briefing():
    news_data = get_real_news()
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 프롬프트: 개인 상황 언급을 강력하게 금지하고 뉴스 중심으로 설정
    prompt = (
        f"오늘은 {today}입니다. 당신은 경제/금융 전문 기자입니다.\n"
        "다음 7개 섹션을 오직 제공된 뉴스 데이터와 경제 시장 정보를 중심으로 작성하세요.\n"
        "지시사항: 사용자의 개인적인 거주지, 직장, 대출 상태 등 개인 신상 관련 내용은 절대 언급하지 마세요.\n"
        "각 항목 끝에는 반드시 해당 뉴스의 [뉴스 보기](URL) 링크를 포함하세요.\n\n"
        "1. [핵심 경제 이슈] 2. [부동산/금리 시장] 3. [주식/ETF] 4. [GCP/인프라/IT] 5. [글로벌] 6. [생활 재테크] 7. [기술 트렌드]\n\n"
        f"참고 뉴스 데이터:\n{news_data}"
    )
    
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    
    if res.status_code != 200:
        raise Exception(f"Groq API 오류: {res.text}")
    
    return res.json()['choices'][0]['message']['content']

def send_telegram(text):
    message = f"☀️ <b>[경제 뉴스 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    res = requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})
    
    if res.status_code != 200:
        raise Exception(f"텔레그램 전송 실패: {res.text}")

if __name__ == "__main__":
    briefing = get_briefing()
    send_telegram(briefing)
