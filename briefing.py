import requests
import os
from datetime import datetime

# 환경 변수 설정
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip()
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()
NEWS_KEY = os.environ.get('NEWSAPI_KEY', '').strip()

def get_real_news():
    url = f"https://newsapi.org/v2/everything?q=경제 OR 부동산 OR 증시&language=ko&sortBy=publishedAt&pageSize=5&apiKey={NEWS_KEY}"
    try:
        res = requests.get(url, timeout=10).json()
        articles = res.get('articles', [])
        return "\n".join([f"- {a['title']}: {a['url']}" for a in articles]) if articles else None
    except:
        return None

def get_briefing():
    news = get_real_news()
    
    # AI에게 전달할 상황별 프롬프트
    base_prompt = (
        "당신은 투자자에게 매일 아침 경제 브리핑을 제공하는 전문 경제 기자입니다.\n"
        "반드시 다음 7개 섹션(핵심, 부동산/금리, 주식/ETF, IT/인프라/GCP, 글로벌, 재테크, 기술)으로 나누어 작성하세요.\n"
        "개인 정보(거주지, 대출 등) 언급은 금지하며, 전문적이고 간결한 톤을 유지하세요.\n"
    )
    
    if news:
        prompt = base_prompt + f"\n다음 뉴스 데이터를 기반으로 섹션별 요약과 링크를 포함하세요:\n{news}"
    else:
        prompt = base_prompt + "\n실시간 뉴스 데이터가 없으므로, 현재 시장 지표(금리, 환율, 주요 산업 트렌드)를 분석하여 작성하세요."

    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    return res.json()['choices'][0]['message']['content'] if res.status_code == 200 else "브리핑 생성 오류"

def send_telegram(text):
    # 가독성을 위해 HTML 포맷으로 전송
    message = f"☀️ <b>[오늘의 맞춤형 투자 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}"
    requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                  json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"})

if __name__ == "__main__":
    briefing_text = get_briefing()
    send_telegram(briefing_text)
