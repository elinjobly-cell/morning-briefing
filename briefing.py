import requests
import os
from datetime import datetime

GEMINI_KEY = os.environ['GEMINI_API_KEY']
TG_TOKEN   = os.environ['TELEGRAM_TOKEN']
TG_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']

def get_briefing():
    today = datetime.now().strftime("%Y년 %m월 %d일")
    prompt = f"""오늘은 {today}입니다.
한국 부동산 담보대출(4억, 3.9%) 보유한 은행 IT 인프라 담당자를 위한
오전 7시 투자 브리핑을 작성해주세요.

다음 5개 섹션으로 작성:

📊 오늘의 핵심 요약
└ 오늘 꼭 알아야 할 투자 이슈 3가지

🏠 부동산·금리
└ 주담대 금리, 부동산 시장 동향, 4억 대출자 관점 시사점

📈 주식·ETF
└ 국내외 주요 지수, 주목 섹터, 투자 액션

🤖 GCP·AI 테크
└ Google Cloud, AI 산업, 씨티 기술 트렌드, 커리어 시사점

🌏 글로벌 경제
└ 미국 연준, 달러/원 환율, 한국 자산 영향

각 섹션 3~4줄로 간결하게. 투자 관점 인사이트 포함."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    res = requests.post(url, json={
        "contents": [{"parts": [{"text": prompt}]}]
    })
    return res.json()['candidates'][0]['content']['parts'][0]['text']

def send_telegram(text):
    today = datetime.now().strftime("%Y.%m.%d (%a)")
    message = f"🌅 *모닝 투자 브리핑*\n_{today}_\n\n{text}\n\n━━━━━━━━━━━━━━\n_AI 자동 생성 | 투자 참고용_"
    requests.post(
        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
        json={
            "chat_id": TG_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
    )

if __name__ == "__main__":
    print("브리핑 생성 중...")
    briefing = get_briefing()
    send_telegram(briefing)
    print("전송 완료!")
