import requests
import os
from datetime import datetime

# 환경 변수 가져오기
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    # 최대한 넓은 범위로 검색 (뉴스 소스 필터 제거하여 데이터 수집 확률 높임)
    url = f"https://newsapi.org/v2/everything?q=경제 OR 부동산&language=ko&sortBy=publishedAt&pageSize=5&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get('articles', [])
        
        if not articles:
            return "현재 실시간 뉴스 데이터가 없습니다."
            
        news_formatted = "\n".join([f"제목: {a['title']}\n링크: {a['url']}\n" for a in articles])
        return news_formatted
    except Exception as e:
        return f"뉴스 데이터 수집 실패: {e}"

def get_briefing():
    news_data = get_real_news()
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    # AI가 개인 정보를 생성하지 못하도록 강력하게 프롬프트 제약
    prompt = (
        f"오늘 날짜: {today}\n"
        "당신은 경제/금융 전문 뉴스 브리퍼입니다.\n"
        "아래 [뉴스 데이터]만 사용하여 브리핑을 작성하세요. "
        "만약 뉴스 데이터가 없거나 부족하다면 '현재 뉴스 업데이트 중입니다'라고 답변하세요.\n"
        "필수 규칙: 절대 사용자의 개인 신상(직장, 거주지, 대출 등)을 언급하지 마세요. 오직 경제 뉴스 중심입니다.\n\n"
        "[뉴스 데이터]\n"
        f"{news_data}\n\n"
        "다음 7개 섹션으로 요약하세요.\n"
        "1. [핵심 경제 이슈] 2. [부동산/금리 시장] 3. [주식/ETF] 4. [IT/인프라/GCP] 5. [글로벌 경제] 6. [생활 재테크] 7. [기술 트렌드]"
    )
    
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    
    if res.status_code != 200:
        return f"브리핑 생성 중 오류 발생: {res.text}"
    
    return res.json()['choices'][0]['message']['content']

def send_telegram(text):
    message = f"☀️ <b>[경제 뉴스 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    res = requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})
    
    if res.status_code != 200:
        print(f"텔레그램 전송 실패: {res.text}")

if __name__ == "__main__":
    briefing_text = get_briefing()
    send_telegram(briefing_text)
