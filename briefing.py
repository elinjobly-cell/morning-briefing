import requests
import os
from datetime import datetime

# 환경 변수 설정
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # ZDNet, 아이뉴스24 등 IT/경제 뉴스 도메인 포함
    query = "경제 OR 반도체 OR IT OR 증시"
    url = f"https://newsapi.org/v2/everything?q={query}&domains=yna.co.kr,hankyung.com,zdnet.co.kr,inews24.com&language=ko&sortBy=publishedAt&pageSize=8&apiKey={NEWS_KEY}"
    
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get('articles', [])
        # 제목과 링크를 하나의 줄로 묶어 AI가 링크를 인식하기 쉽게 전달
        return "\n".join([f"- {a['title']}: {a['url']}" for a in articles]) if articles else None
    except:
        return None

def get_briefing():
    news = get_real_news()
    
    portfolio_info = "주요 기업: NVIDIA, AMD, SK하이닉스, 마이크론, 삼성전자, 웨스턴디지털, TSMC, ASE"
    
    # 링크를 반드시 포함하도록 강력한 제약사항 추가
    prompt = (
        "당신은 경제 전문 기자입니다. 아래 [뉴스 리스트]의 기사 링크(URL)를 절대 누락하지 마세요.\n"
        "지시사항:\n"
        "1. 경제 전반의 흐름을 요약하되, [뉴스 리스트]에 있는 링크를 반드시 해당 섹션 끝에 포함하세요.\n"
        "2. 한자나 외국어를 혼용하지 말고 표준 한국어로만 작성하세요.\n"
        "3. 올리버 님의 주요 관심 기업(NVIDIA, SK하이닉스 등) 뉴스가 있다면 섹션 3에 포함하세요.\n"
        "4. 링크가 없다면 뉴스 검색 내용을 바탕으로 가장 적절한 기사 링크를 붙이세요.\n\n"
        f"주요 관심 기업: {portfolio_info}\n\n"
        f"[뉴스 리스트]\n{news if news else '최신 경제 뉴스 데이터가 없습니다.'}\n\n"
        "다음 8개 섹션으로 요약하세요(각 섹션 끝에 반드시 [원본 보기](URL) 형식으로 링크 첨부):\n"
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
    message = f"☀️ <b>[오늘의 경제/산업 종합 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing_text = get_briefing()
    send_telegram(briefing_text)
