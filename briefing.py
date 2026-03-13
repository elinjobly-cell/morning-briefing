import requests
import os
from datetime import datetime

# 환경 변수 설정
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # 연합뉴스(yna.co.kr)와 한국경제(hankyung.com)로 출처를 제한
    query = "반도체 OR NVIDIA OR AMD OR SK하이닉스 OR 삼성전자 OR TSMC"
    url = f"https://newsapi.org/v2/everything?q={query}&domains=yna.co.kr,hankyung.com&language=ko&sortBy=publishedAt&pageSize=7&apiKey={NEWS_KEY}"
    
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get('articles', [])
        return "\n".join([f"- {a['title']}: {a['url']}" for a in articles]) if articles else None
    except:
        return None

def get_briefing():
    news = get_real_news()
    
    portfolio_info = """
    주요 기업: NVIDIA(AI칩), AMD(메모리), SK하이닉스(메모리), 마이크론(메모리), 
    삼성전자(NAND), 웨스턴디지털(파운드리/NAND), TSMC(패키징), ASE(패키징)
    """
    
    prompt = (
        "당신은 한국의 경제 전문 기자입니다. 반드시 완벽한 한국어(표준어)로만 작성하세요.\n"
        "지시사항:\n"
        "- 한자나 외국어(베트남어 등)를 혼용하지 마세요.\n"
        "- 반드시 자연스러운 한국어 문장으로만 구성하세요.\n"
        "- 뉴스 데이터가 있다면 제목과 [링크]를 포함하고, 데이터가 없다면 시장 상황을 분석하세요.\n"
        "- 개인 신상 정보는 절대 언급하지 마세요.\n"
        f"{portfolio_info}\n\n"
        "다음 8개 섹션으로 나누어 작성하세요:\n"
        "1. [핵심 경제 이슈] 2. [부동산/금리] 3. [반도체 및 종목 이슈] 4. [주식/ETF] "
        "5. [IT/인프라/GCP] 6. [글로벌 경제] 7. [생활 재테크] 8. [기술 트렌드]"
    )
    
    if news:
        prompt += f"\n\n참고 뉴스 데이터:\n{news}"
    else:
        prompt += "\n\n현재 실시간 뉴스 데이터가 부족하므로, 일반적인 반도체 업황 및 시장 상황을 분석해 주세요."

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [{"role": "user", "content": prompt}], 
        "max_tokens": 2000,
        "temperature": 0.2  # 답변의 정확성을 위한 낮은 온도 설정
    }
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "브리핑 생성 오류"

def send_telegram(text):
    message = f"☀️ <b>[오늘의 맞춤형 반도체/경제 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing_text = get_briefing()
    send_telegram(briefing_text)
