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
        # 뉴스 제목과 URL을 문자열로 결합
        news_list = "\n".join([f"- {a['title']}: {a['url']}" for a in articles])
        return news_list
    except Exception as e:
        return f"뉴스 데이터 없음: {e}"

def get_briefing():
    news_data = get_real_news()
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    # 강력한 지시사항을 포함한 프롬프트 (들여쓰기 주의!)
    prompt = (
        f"오늘은 {today}입니다. 당신은 경제 뉴스 전문 분석가입니다.\n\n"
        "아래 제공된 뉴스 데이터를 기반으로 7개 섹션을 간결하게 요약하세요.\n"
        "지시사항: 개인적인 상황(직장, 거주지 등) 언급을 절대 하지 말고, 오직 경제와 시장 정보 중심으로 작성하세요.\n"
        "각 항목 끝에는 반드시 [뉴스 보기](URL) 링크를 포함하세요.\n\n"
        "1. [핵심 경제 이슈] 2. [부동산/금리] 3. [주식/ETF] 4. [IT/인프라/GCP] 5. [글로벌] 6. [생활 재테크] 7. [기술 트렌드]\n\n"
        f"참고 뉴스:\n{news_data}"
    )
    
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body
