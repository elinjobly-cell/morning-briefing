import requests
import os
from datetime import datetime

# 설정 정보
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # IT/경제 전문 도메인 4곳에서 실시간 뉴스 10개 수집
    query = "경제 OR 반도체 OR 증시 OR IT"
    url = f"https://newsapi.org/v2/everything?q={query}&domains=yna.co.kr,hankyung.com,zdnet.co.kr,inews24.com&language=ko&sortBy=publishedAt&pageSize=10&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get('articles', [])
        # 제목과 링크를 한 줄로 결합하여 AI에게 전달
        return "\n".join([f"기사: {a['title']}\n링크: {a['url']}\n" for a in articles]) if articles else None
    except:
        return None

def get_briefing():
    news = get_real_news()
    
    prompt = (
        "당신은 경제 전문 기자입니다. 제공된 [뉴스 데이터]를 분석하여 브리핑을 작성하세요.\n"
        "지시사항:\n"
        "1. 경제 전반의 흐름을 먼저 요약하고, 올리버 님의 관심 기업(NVIDIA, SK하이닉스, 삼성전자 등) 이슈를 [반도체 및 기업 소식]에 포함하세요.\n"
        "2. 뉴스 내용이 없는 섹션이라도, [뉴스 데이터]에서 가장 관련 있는 기사의 [원본 보기](URL)를 반드시 붙이세요.\n"
        "3. 표준 한국어만 사용하고, 한자나 외국어는 절대 사용하지 마세요.\n"
        "4. 브리핑은 8개 섹션으로 구성하세요.\n\n"
        f"[뉴스 데이터]\n{news if news else '데이터 없음'}\n\n"
        "섹션 구성:\n"
        "1. [핵심 경제 이슈] 2. [부동산/금리] 3. [반도체 및 기업 소식] 4. [주식/ETF] "
        "5. [IT/인프라/GCP] 6. [글로벌 경제] 7. [생활 재테크] 8. [기술 트렌드]"
    )

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [{"role": "user", "content": prompt}], 
        "max_tokens": 2000,
        "temperature": 0.2
    }
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "오류 발생"

def send_telegram(text):
    message = f"☀️ <b>[경제/산업 핵심 요약 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing_text = get_briefing()
    send_telegram(briefing_text)
