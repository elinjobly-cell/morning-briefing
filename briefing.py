import requests
import os
from datetime import datetime

# 디버깅: 환경 변수 키 확인
print(f"DEBUG: 키의 첫 4자리: {os.environ.get('GROQ_API_KEY', '')[:4]}") 

# 환경 변수 가져오기
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip() 
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()

def get_briefing():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    # 프롬프트 수정: 개인적인 상황 언급을 최소화하고 경제/금융 뉴스 중심으로 변경
    prompt = (
        f"오늘은 {today}입니다. 투자자를 위한 '실시간 경제 및 금융 뉴스 브리핑'입니다.\n\n"
        "다음 5개 섹션으로 구성해 주세요:\n"
        "1. [핵심 뉴스] 오늘 가장 중요한 경제 이슈 3가지 (뉴스 제목 포함)\n"
        "2. [시장 지표] 주요 지수(국내/해외) 요약 및 투자 포인트\n"
        "3. [산업 동향] IT/반도체/부동산 관련 주요 정책 및 산업 뉴스\n"
        "4. [글로벌] 놓치지 말아야 할 국제 경제 뉴스\n"
        "5. [재테크 팁] 투자자가 주목해야 할 데이터나 관련 분석 정보\n\n"
        "각 섹션은 간결하고 전문적인 톤으로 작성해 주세요. 모든 내용은 사실 기반의 경제 뉴스를 중심으로 하세요."
    )
    # ... 이하 기존 헤더 및 API 호출 코드 동일 ...

    
    headers = {"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    body = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "max_tokens": 2000}
    
    res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
    
    if res.status_code != 200:
        raise Exception(f"Groq API 연결 실패 (상태코드 {res.status_code}): {res.text}")
    
    return res.json()['choices'][0]['message']['content']

def send_telegram(text):
    message = f"☀️ <b>[오늘의 맞춤형 투자 브리핑]</b>\n📅 {datetime.now().strftime('%Y.%m.%d')}\n\n{text}\n\n💡 <i>AI 자동 생성 | 투자 참고용</i>"
    
    res = requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
        json={"chat_id": TG_CHAT_ID, "text": message, "parse_mode": "HTML"}
    )
    
    if res.status_code != 200:
        raise Exception(f"텔레그램 전송 실패: {res.text}")

if __name__ == "__main__":
    briefing = get_briefing()
    send_telegram(briefing)
