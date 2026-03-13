import requests
import os
from datetime import datetime

# 환경 변수 설정
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # 검색어에 반도체 주요 기업과 키워드를 추가하여 타겟 뉴스 수집
    query = "반도체 OR NVIDIA OR AMD OR SK하이닉스 OR 삼성전자 OR TSMC"
    url = f"https://newsapi.org/v2/everything?q={query}&language=ko&sortBy=publishedAt&pageSize=8&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get('articles', [])
        return "\n".join([f"- {a['title']}: {a['url']}" for a in articles]) if articles else None
    except:
        return None

def get_briefing():
    news = get_real_news()
    
    # 올리버 님이 요청하신 포트폴리오 정보를 프롬프트에 포함하여 분석
    portfolio_info = """
    포트폴리오 주요 기업: NVIDIA(AI칩), AMD(메모리), SK하이닉스(메모리), 마이크론(메모리), 
    삼성전자(NAND), 웨스턴디지털(파운드리/NAND), TSMC(패키징), ASE(패키징)
    """
    
    prompt = (
        "당신은 전문 경제 기자입니다. 아래 뉴스 데이터와 투자자 포트폴리오를 참고하여 브리핑을 작성하세요.\n"
        f"{portfolio_info}\n\n"
        "반드시 다음 8개 섹션으로 나누어 작성하세요:\n"
        "1. [핵심 경제 이슈] 2. [부동산/금리] 3. [반도체 산업 및 종목 이슈] 4. [주식/ETF] "
        "5. [IT/인프라/GCP] 6. [글로벌 경제] 7. [생활 재테크] 8. [기술 트렌드]\n\n"
        "지시사항:\n"
        "- 뉴스 데이터가 있다면 반드시 제목과 [링크]를 포함하여 작성하세요.\n"
        "- 특정 반도체 기업 뉴스(NVIDIA, SK하이닉스 등)가 있다면 3번 섹션에서 상세히 다루세요.\n"
        "- 개인 정보(직장 등)는 절대 언급하지 마세요."
    )
    
    if news:
        prompt += f"\n\n참고할 최신 뉴스:\n{news}"
    else:
        prompt += "\n\n현재 실시간 뉴스 데이터가 부족하므로, 일반적인 반도체 업황 및 시장 상황을 분석해 주세요."

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2500}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "브리핑 생성 오류"

def send_telegram(text):
    message = f"☀️ <b>[오늘의 맞춤형 반도체/경제 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing_text = get_briefing()
    send_telegram(briefing_text)
