# 📊 Datacenter Investment Automation System

GitHub Actions 기반 데이터센터 관련 주식 자동 분석 및 뉴스 수집 시스템

## 🎯 주요 기능

### 1. 📰 데이터센터 뉴스 모니터 (`datacenter_news_monitor.py`)
- Google News & Naver API를 통한 자동 뉴스 수집
- 네이버 파파고 자동 번역 (영문 → 한글)
- 관련도 기반 스코어링 및 필터링
- 주요 데이터센터/AI 기업 뉴스 추적

### 2. 📈 종목 일일 리포트 (`datacenter_report_enhanced.py`)
- 26개 데이터센터 관련 종목 자동 분석
- RSI, 이동평균, 거래량 등 기술적 지표 계산
- 골든크로스/데드크로스 감지
- 섹터별 성과 분석

### 3. 🔍 종목 자동 선정 시스템 (`stock_selection_system.py`)
- 월 1회 실행 권장
- 16개 세부 영역별 최적 종목 선정
- 시가총액, 수익률, 모멘텀 등 종합 평가 (100점 만점)
- 투자 포트폴리오 자동 구성

## 📁 디렉토리 구조

```
repo/
├── scripts/                      # Python 스크립트
│   ├── datacenter_news_monitor.py
│   ├── datacenter_report_enhanced.py
│   └── stock_selection_system.py
├── market_data/                  # 원본 데이터 (JSON)
│   ├── news_data_YYYYMMDD.json
│   ├── datacenter_stocks_YYYYMMDD.json
│   ├── stock_selection_YYYYMMDD.json
│   └── news_history.json
├── analysis_reports/             # 분석 리포트 (Excel, Markdown)
│   ├── news_analysis_YYYYMMDD.xlsx
│   ├── news_report_YYYYMMDD.md
│   ├── datacenter_analysis_YYYYMMDD.xlsx
│   ├── datacenter_report_YYYYMMDD.md
│   ├── stock_selection_YYYYMMDD.xlsx
│   └── stock_selection_report_YYYYMMDD.md
├── outputs/                      # Telegram 전송용 임시 파일
│   └── *.docx
├── .github/workflows/            # GitHub Actions workflows
└── requirements.txt
```

## 🔧 환경 설정

### 필수 Secrets (GitHub Repository Settings)

```
TELEGRAM_BOT_TOKEN       # Telegram 봇 토큰
TELEGRAM_CHAT_ID         # Telegram 채팅 ID
NAVER_CLIENT_ID          # 네이버 API Client ID (뉴스 검색 & 번역용)
NAVER_CLIENT_SECRET      # 네이버 API Client Secret
```

### GitHub Actions Workflow 설정

각 workflow 파일에 반드시 포함:

```yaml
permissions:
  contents: write  # Git push 권한 필수!
```

## 📊 데이터 흐름

```
API 호출 (yfinance, Google News, Naver)
    ↓
데이터 수집 & 분석
    ↓
파일 저장 (JSON, Excel, Markdown)
    ↓
Git Commit & Push (repo에 영구 보관)
    ↓
Telegram 요약 알림 (상세 내용은 repo 참조)
```

## 🚀 실행 방법

### GitHub Actions (자동)
- 각 스크립트별 스케줄에 따라 자동 실행
- 뉴스 모니터: 매일 실행 권장
- 종목 리포트: 매일 실행 권장
- 종목 선정: 월 1회 실행 권장

### 로컬 실행
```bash
# 가상환경 생성 (선택)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
export TELEGRAM_BOT_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export NAVER_CLIENT_ID="your_client_id"
export NAVER_CLIENT_SECRET="your_client_secret"

# 스크립트 실행
python scripts/datacenter_news_monitor.py
python scripts/datacenter_report_enhanced.py
python scripts/stock_selection_system.py
```

## 📋 주요 종목 커버리지

### AI 인프라
- GPU: NVIDIA, AMD
- CPU: Intel, AMD
- 서버: Super Micro, Dell, HPE

### 전력/쿨링
- 전력관리: Vertiv, Eaton
- 발전기: Cummins, Generac
- HVAC: Johnson Controls, Trane Tech

### 네트워크
- 스위치: Arista Networks, Cisco
- 네트워크칩: Broadcom, Marvell
- 광통신: HFR, Lumentum, Corning

### 메모리/스토리지
- HBM: SK Hynix, Samsung, Micron
- 패키징: 한미반도체, Amkor
- 스토리지: Western Digital, Seagate

### DC 부동산
- REIT: Digital Realty, Equinix

## 📱 Telegram 알림

### 뉴스 모니터
```
📰 데이터센터 뉴스 수집 완료

📊 수집: 20개 기사
Google: 12 | Naver: 8

💾 저장:
- JSON: news_data_20241127.json
- Excel: news_analysis_20241127.xlsx
- Markdown: news_report_20241127.md

✅ GitHub에 push 완료
📄 상세 내용은 repo 파일 참조
```

### 종목 리포트
```
📊 데이터센터 종목 분석 완료

📈 상승: 15개
📉 하락: 10개
➖ 보합: 1개
📊 총 26개 종목

🎯 주요 시그널:
⭐ 골든크로스: 8개
📊 거래량급증: 3개

💾 저장 완료
✅ GitHub에 push 완료
```

## ⚠️ GitHub Actions Usage 제한 대응

이 시스템은 **GitHub Actions usage 제한을 피하기 위해** 다음과 같이 설계되었습니다:

1. ✅ **데이터를 repo에 저장** (JSON, Excel, Markdown)
2. ✅ **Git commit & push로 repo 활용**
3. ✅ **Telegram은 요약만 전송** (상세 내용 ❌)
4. ✅ **모든 분석 결과는 repo 파일로 영구 보관**

### ❌ 하지 말아야 할 것
- Telegram에 전체 리포트 전송 (usage 급증)
- API만 호출하고 파일 저장 안 함
- Git push 없이 실행

### ✅ 올바른 사용법
- **API → 데이터 수집 → 파일 저장 → Git push → Telegram 요약**
- 상세 내용은 repo의 `analysis_reports/` 디렉토리에서 확인

## 🔄 업데이트 히스토리

### v3.0 (2024-11-27) - GitHub Actions Compatible
- ✅ 데이터 저장 로직 추가 (JSON, Excel, Markdown)
- ✅ Telegram 알림을 요약만으로 변경
- ✅ Git push 기반 repo 활용
- ✅ GitHub Actions usage 최적화

### v2.0 (이전)
- RSI 지표 추가
- 네이버 파파고 번역 기능
- 종목 자동 선정 시스템

## 📞 문의 및 기여

이슈나 개선 사항은 GitHub Issues에 등록해주세요.

## 📄 라이선스

MIT License
