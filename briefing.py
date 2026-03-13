import requests
import os
from datetime import datetime

# 환경 변수 설정
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # 경제 전반의 뉴스를 고루 가져오기 위한 통합 쿼리
    query = "경제 OR 부동산 OR 증시 OR IT OR 반도체"
    url = f"https://newsapi.org/v2/everything?q={query}&domains=yna.co.kr,hankyung.com&language=ko&sortBy=publishedAt&pageSize=10&apiKey={NEWS_KEY}"
    
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get('articles', [])
        # 제목과 링크를 확실하게 분리하여 AI에 전달
        return "\n".join([f"- 제목: {a['title']}\n  링크: {a['url']}\n" for a in articles]) if articles else None
    except:
        return None

def get_briefing():
    news = get_real_news()
    
    # 올리버 님이 지정하신 주제
    portfolio_info = """
    주요 관심 기업: NVIDIA(AI칩), AMD, SK하이닉스, 마이크론, 삼성전자, 웨스턴디지털, TSMC, ASE
    """
    
    prompt = (
        "당신은 한국의 경제 전문 기자입니다. 아래 [뉴스 데이터]를 사용하여 경제 브리핑을 작성하세요.\n"
        "지시사항:\n"
        "1. 경제 전반의 객관적인 흐름을 먼저 작성하고, 올리버 님의 주요 관심 기업 소식을 섹션 3에 집중하세요.\n"
        "2. 각 요약 내용마다 반드시 제공된 [링크]를 하단에 첨부하세요.\n"
        "3. 절대 한자나 외국어를 혼용하지 말고, 표준 한국어로만 작성하세요.\n"
        "4. 뉴스 데이터가 없더라도 시장 상황을 분석하여 작성하세요.\n\n"
        f"{portfolio_info}\n\n"
        "[뉴스 데이터]\n{news if news else '뉴스 데이터 없음'}\n\n"
        "다음 8개 섹션으로 나누어 요약하세요:\n"
        "1. [핵심 경제 이슈] 2. [부동산/금리] 3. [반도체 및 기업 소식] 4. [주식/ETF] "
        "5. [IT/인프라/GCP] 6. [글로벌 경제] 7. [생활 재테크] 8. [기술 트렌드]"
    )

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [{"role": "user", "content": prompt}], 
        "max_tokens": 2500,
        "temperature": 0.2
    }
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "브리핑 생성 오류"

def send_telegram(text):
    message = f"☀️ <b>[경제/산업 종합 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing_text = get_briefing()
    send_telegram(briefing_text)
