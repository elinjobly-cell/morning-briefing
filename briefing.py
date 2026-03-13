import requests
import os
from datetime import datetime

# 환경 변수 가져오기
GROQ_KEY = os.environ.get('GROQ_API_KEY', '').strip() # .strip() 추가로 앞뒤 공백 제거
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '').strip()
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '').strip()

def get_briefing():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    prompt = (
        f"오늘은 {today}입니다. 싱글맘, 2016년생 자녀, 송도 풍림아이원 거주(대출4억, 3.9%), "
        "잠실 르엘 관심, 씨티은행 IT 인프라 담당자, GCP 자격증 준비 중인 투자자를 위한 브리핑.\n\n"
        "다음 7개 섹션으로 구성해 주세요:\n"
        "1. [핵심] 오늘의 시장 한 줄 평\n"
        "2. [부동산] 송도/잠실 이슈 및 등기 관련\n"
        "3. [주식/ETF] 시장 주요 테마 및 유의 종목\n"
        "4. [IT커리어] GCP/인프라 기술 동향\n"
        "5. [글로벌] 주요 경제 지표 및 이슈\n"
        "6. [생활] 실용적인 싱글맘 재테크 조언\n"
        "7. [기술] 차세대 메모리/반도체 트렌드 분석\n\n"
        "각 섹션은 3~4줄로, 따뜻하고 전문적인 톤으로 작성해 주세요."
    )
    
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
