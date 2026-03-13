import requests
import os
from datetime import datetime

# 환경 변수 설정 (시스템 환경 변수에서 로드)
GROQ_KEY = os.environ.get('GROQ_API_KEY', '')
TG_TOKEN = os.environ.get('TELEGRAM_TOKEN', '')
TG_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')

def get_briefing():
    """Groq API를 사용하여 맞춤형 투자 브리핑 내용을 생성합니다."""
    today = datetime.now().strftime("%Y년 %m월 %d일")
    prompt = (
        f"오늘은 {today}입니다. "
        "싱글맘, 2016년생 초등학생 자녀 1명, 인천 송도 풍림아이원 1단지 거주(담보대출 4억, 금리 3.9%), "
        "잠실 르엘 관심 및 등기시점 주목, 씨티은행 IT 인프라 담당자(VMware, NAS, Wintel 운영), "
        "GCP 클라우드 자격증 준비 중인 투자자를 위한 오전 7시 맞춤형 투자 브리핑을 작성해줘. "
        "반드시 다음 7개 섹션을 포함하세요: "
        "1. 오늘의 핵심 요약, 2. 부동산 및 금리(송도 풍림아이원 시세/잠실 르엘 등기), "
        "3. 주식 및 ETF, 4. GCP 및 AI 테크(IT 커리어), 5. 글로벌 경제, "
        "6. 오늘의 생활 팁(재테크), 7. 기술 트렌드(HBF 표준화 이슈/SK하이닉스-샌디스크 협력 및 산업 전망). "
        "각 섹션은 3~4줄 내외로, 따뜻하고 실용적인 톤으로 작성하세요."
    )
    
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2000
    }
    
    try:
        res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=body)
        res.raise_for_status()  # 요청 에러 시 예외 발생
        data = res.json()
        return data['choices'][0]['message']['content']
    except Exception as e:
        return f"브리핑 생성 중 오류가 발생했습니다: {str(e)}"

def send_telegram(text):
    """생성된 브리핑을 텔레그램으로 전송합니다."""
    today = datetime.now().strftime("%Y.%m.%d")
    message = (
        f"📢 모닝 투자 브리핑\n{today}\n"
        "송도 풍림아이원 | 잠실 르엘 | HBF 메모리 | 씨티 IT\n"
        "====================\n\n"
        f"{text}\n\n"
        "====================\nAI 자동 생성 | 투자 참고용"
    )
    
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": message}
    
    try:
        res = requests.post(url, json=payload)
        res.raise_for_status()
        print("전송 완료!")
    except Exception as e:
        print(f"텔레그램 전송 실패: {str(e)}")

if __name__ == "__main__":
    print("브리핑 생성 및 전송 시작...")
    briefing_content = get_briefing()
    send_telegram(briefing_content)

