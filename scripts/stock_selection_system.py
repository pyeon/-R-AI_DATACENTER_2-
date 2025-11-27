"""
데이터센터 종목 자동 선정 시스템 v2.0 - GitHub Actions Compatible
✅ API → Data Collection → File Storage → Git Push → Telegram Summary Only
✅ 월 1회 실행하여 각 세부영역별 최적 종목 선정
"""

import yfinance as yf
import pandas as pd
import requests
import os
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("="*80)
print("🔍 데이터센터 종목 자동 선정 시스템 v2.0")
print("  ✅ GitHub Actions Compatible")
print("="*80 + "\n")

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 데이터 저장 디렉토리
MARKET_DATA_DIR = 'market_data'
ANALYSIS_DIR = 'analysis_reports'
OUTPUT_DIR = 'outputs'

os.makedirs(MARKET_DATA_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 각 세부영역별 후보 종목 Pool
CANDIDATE_POOLS = {
    'GPU': [
        {'name': 'NVIDIA', 'ticker': 'NVDA', 'exchange': 'US'},
        {'name': 'AMD', 'ticker': 'AMD', 'exchange': 'US'},
    ],
    'CPU': [
        {'name': 'Intel', 'ticker': 'INTC', 'exchange': 'US'},
        {'name': 'AMD', 'ticker': 'AMD', 'exchange': 'US'},
    ],
    '서버제조': [
        {'name': 'Super Micro', 'ticker': 'SMCI', 'exchange': 'US'},
        {'name': 'Dell', 'ticker': 'DELL', 'exchange': 'US'},
        {'name': 'HPE', 'ticker': 'HPE', 'exchange': 'US'},
        {'name': 'Lenovo', 'ticker': '0992.HK', 'exchange': 'HK'},
    ],
    '전력관리': [
        {'name': 'Vertiv', 'ticker': 'VRT', 'exchange': 'US'},
        {'name': 'Eaton', 'ticker': 'ETN', 'exchange': 'US'},
        {'name': 'Schneider Electric', 'ticker': 'SU.PA', 'exchange': 'EU'},
    ],
    '전력기기': [
        {'name': 'LS ELECTRIC', 'ticker': '010120.KS', 'exchange': 'KR'},
        {'name': 'LS', 'ticker': '006260.KS', 'exchange': 'KR'},
    ],
    '발전기': [
        {'name': 'Cummins', 'ticker': 'CMI', 'exchange': 'US'},
        {'name': 'Generac', 'ticker': 'GNRC', 'exchange': 'US'},
        {'name': 'Caterpillar', 'ticker': 'CAT', 'exchange': 'US'},
    ],
    'HVAC': [
        {'name': 'Johnson Controls', 'ticker': 'JCI', 'exchange': 'US'},
        {'name': 'Trane Tech', 'ticker': 'TT', 'exchange': 'US'},
        {'name': 'Carrier Global', 'ticker': 'CARR', 'exchange': 'US'},
    ],
    '스위치': [
        {'name': 'Arista Networks', 'ticker': 'ANET', 'exchange': 'US'},
        {'name': 'Cisco', 'ticker': 'CSCO', 'exchange': 'US'},
        {'name': 'Juniper', 'ticker': 'JNPR', 'exchange': 'US'},
    ],
    '네트워크칩': [
        {'name': 'Broadcom', 'ticker': 'AVGO', 'exchange': 'US'},
        {'name': 'Marvell', 'ticker': 'MRVL', 'exchange': 'US'},
        {'name': 'Microchip', 'ticker': 'MCHP', 'exchange': 'US'},
    ],
    '광트랜시버': [
        {'name': 'HFR', 'ticker': '230240.KQ', 'exchange': 'KR'},
        {'name': '옵트론텍', 'ticker': '082210.KQ', 'exchange': 'KR'},
    ],
    '광섬유케이블': [
        {'name': 'Corning', 'ticker': 'GLW', 'exchange': 'US'},
        {'name': 'Prysmian', 'ticker': 'PRY.MI', 'exchange': 'EU'},
    ],
    '광학부품': [
        {'name': 'Lumentum', 'ticker': 'LITE', 'exchange': 'US'},
        {'name': 'II-VI', 'ticker': 'COHR', 'exchange': 'US'},
    ],
    'HBM메모리': [
        {'name': 'SK hynix', 'ticker': '000660.KS', 'exchange': 'KR'},
        {'name': 'Samsung', 'ticker': '005930.KS', 'exchange': 'KR'},
        {'name': 'Micron', 'ticker': 'MU', 'exchange': 'US'},
    ],
    '반도체패키징': [
        {'name': '한미반도체', 'ticker': '042700.KQ', 'exchange': 'KR'},
        {'name': 'Amkor', 'ticker': 'AMKR', 'exchange': 'US'},
        {'name': 'ASE Technology', 'ticker': '3711.TW', 'exchange': 'TW'},
    ],
    '스토리지': [
        {'name': 'Western Digital', 'ticker': 'WDC', 'exchange': 'US'},
        {'name': 'Seagate', 'ticker': 'STX', 'exchange': 'US'},
        {'name': 'NetApp', 'ticker': 'NTAP', 'exchange': 'US'},
    ],
    '데이터센터REIT': [
        {'name': 'Digital Realty', 'ticker': 'DLR', 'exchange': 'US'},
        {'name': 'Equinix', 'ticker': 'EQIX', 'exchange': 'US'},
        {'name': 'CyrusOne', 'ticker': 'CONE', 'exchange': 'US'},
    ],
}

# 세부영역과 대분류/중분류 매핑
SECTOR_MAPPING = {
    'GPU': {'category': 'AI 인프라', 'sector': 'AI칩'},
    'CPU': {'category': 'AI 인프라', 'sector': 'AI칩'},
    '서버제조': {'category': 'AI 인프라', 'sector': 'AI서버'},
    '전력관리': {'category': '전력/쿨링', 'sector': '전력'},
    '전력기기': {'category': '전력/쿨링', 'sector': '전력'},
    '발전기': {'category': '전력/쿨링', 'sector': '발전'},
    'HVAC': {'category': '전력/쿨링', 'sector': '쿨링'},
    '스위치': {'category': '네트워크', 'sector': '네트워크'},
    '네트워크칩': {'category': '네트워크', 'sector': '네트워크'},
    '광트랜시버': {'category': '네트워크', 'sector': '광통신'},
    '광섬유케이블': {'category': '네트워크', 'sector': '광섬유'},
    '광학부품': {'category': '네트워크', 'sector': '광통신'},
    'HBM메모리': {'category': '메모리/스토리지', 'sector': 'HBM'},
    '반도체패키징': {'category': '메모리/스토리지', 'sector': '패키징'},
    '스토리지': {'category': '메모리/스토리지', 'sector': 'SSD'},
    '데이터센터REIT': {'category': 'DC 부동산', 'sector': 'DC REIT'},
}


def calculate_selection_score(ticker, name, exchange):
    """종목 선정 점수 계산 (100점 만점)"""
    try:
        stock = yf.Ticker(ticker)
        
        # 기본 정보
        info = stock.info
        market_cap = info.get('marketCap', 0)
        
        # 가격 데이터
        hist = stock.history(period="1y")
        if hist.empty or len(hist) < 126:
            print(f"  ⚠️ {name}: 데이터 부족")
            return None
        
        current = hist['Close'].iloc[-1]
        
        # 수익률
        return_3m = ((current / hist['Close'].iloc[-63]) - 1) * 100 if len(hist) >= 63 else 0
        return_6m = ((current / hist['Close'].iloc[-126]) - 1) * 100 if len(hist) >= 126 else 0
        
        # 거래량
        avg_volume_20 = hist['Volume'].rolling(20).mean().iloc[-1]
        avg_volume_60 = hist['Volume'].rolling(60).mean().iloc[-1]
        volume_trend = (avg_volume_20 / avg_volume_60) if avg_volume_60 > 0 else 1
        
        # 이동평균
        ma_20 = hist['Close'].rolling(20).mean().iloc[-1]
        ma_60 = hist['Close'].rolling(60).mean().iloc[-1]
        golden_cross = ma_20 > ma_60
        
        # RSI
        delta = hist['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        rsi_value = rsi.iloc[-1]
        
        # 점수 계산
        score = 0
        
        # 1. 시가총액 점수 (30점)
        if market_cap >= 100_000_000_000:
            score += 30
        elif market_cap >= 50_000_000_000:
            score += 25
        elif market_cap >= 10_000_000_000:
            score += 20
        elif market_cap >= 5_000_000_000:
            score += 15
        elif market_cap >= 1_000_000_000:
            score += 10
        else:
            score += 5
        
        # 2. 거래량 점수 (20점)
        if volume_trend >= 1.5:
            score += 20
        elif volume_trend >= 1.2:
            score += 15
        elif volume_trend >= 1.0:
            score += 10
        else:
            score += 5
        
        # 3. 3개월 수익률 점수 (20점)
        if return_3m >= 30:
            score += 20
        elif return_3m >= 20:
            score += 17
        elif return_3m >= 10:
            score += 14
        elif return_3m >= 0:
            score += 10
        elif return_3m >= -10:
            score += 5
        
        # 4. 6개월 수익률 점수 (15점)
        if return_6m >= 40:
            score += 15
        elif return_6m >= 25:
            score += 12
        elif return_6m >= 10:
            score += 9
        elif return_6m >= 0:
            score += 6
        elif return_6m >= -15:
            score += 3
        
        # 5. 기술적 지표 점수 (15점)
        tech_score = 0
        if golden_cross:
            tech_score += 6
        if 40 <= rsi_value <= 60:
            tech_score += 6
        elif 30 <= rsi_value <= 70:
            tech_score += 3
        
        price_vs_ma20 = (current / ma_20 - 1) * 100
        if price_vs_ma20 > 0:
            tech_score += 3
        
        score += tech_score
        
        return {
            'name': name,
            'ticker': ticker,
            'exchange': exchange,
            'market_cap': float(market_cap),
            'price': float(current),
            'return_3m': float(return_3m),
            'return_6m': float(return_6m),
            'volume_trend': float(volume_trend),
            'ma_20': float(ma_20),
            'ma_60': float(ma_60),
            'golden_cross': bool(golden_cross),
            'rsi': float(rsi_value),
            'score': float(score)
        }
        
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:100]}")
        return None


def select_best_stocks_per_sector():
    """각 세부영역별로 최고 점수 종목 선정"""
    
    selected_stocks = []
    all_candidates_data = []
    
    for sub_sector, candidates in CANDIDATE_POOLS.items():
        print(f"\n{'='*60}")
        print(f"📂 세부영역: {sub_sector}")
        print(f"   후보: {len(candidates)}개")
        print(f"{'='*60}")
        
        sector_results = []
        
        for candidate in candidates:
            print(f"  분석 중: {candidate['name']:20s} ... ", end='')
            result = calculate_selection_score(
                candidate['ticker'],
                candidate['name'],
                candidate['exchange']
            )
            
            if result:
                result['sub_sector'] = sub_sector
                result['category'] = SECTOR_MAPPING[sub_sector]['category']
                result['sector'] = SECTOR_MAPPING[sub_sector]['sector']
                
                sector_results.append(result)
                all_candidates_data.append(result)
                print(f"✅ {result['score']:.1f}점")
            else:
                print("❌")
        
        # 점수 순으로 정렬
        sector_results.sort(key=lambda x: x['score'], reverse=True)
        
        if sector_results:
            best = sector_results[0]
            selected_stocks.append(best)
            
            print(f"\n  ⭐ 선정: {best['name']} ({best['score']:.1f}점)")
            print(f"     시가총액: ${best['market_cap']/1e9:.1f}B")
            print(f"     3개월 수익률: {best['return_3m']:+.2f}%")
            print(f"     골든크로스: {'✅' if best['golden_cross'] else '❌'}")
            
            if len(sector_results) > 1:
                second = sector_results[1]
                print(f"  2위: {second['name']} ({second['score']:.1f}점)")
        else:
            print(f"  ⚠️ 해당 세부영역에서 선정 가능한 종목 없음")
    
    return selected_stocks, all_candidates_data


# ============================================================================
# MAIN EXECUTION
# ============================================================================

print("\n🚀 종목 선정 프로세스 시작...\n")

selected, all_candidates = select_best_stocks_per_sector()

print(f"\n{'='*80}")
print(f"✅ 총 {len(selected)}개 종목 선정 완료!")
print(f"{'='*80}\n")

# ============================================================================
# DATA STORAGE (JSON, Excel, Markdown)
# ============================================================================

now = datetime.now()
date_str = now.strftime('%Y%m%d')
timestamp = now.strftime('%Y-%m-%d %H:%M')

print("="*80)
print("💾 DATA STORAGE")
print("="*80)

# 1. JSON 저장 (market_data/)
json_file = f'{MARKET_DATA_DIR}/stock_selection_{date_str}.json'
json_data = {
    'timestamp': timestamp,
    'total_selected': len(selected),
    'selected_stocks': selected,
    'all_candidates': all_candidates
}
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)
print(f"✅ JSON: {json_file}")

# 2. Excel 저장 (analysis_reports/)
df_selected = pd.DataFrame(selected)
df_all = pd.DataFrame(all_candidates)

excel_file = f'{ANALYSIS_DIR}/stock_selection_{date_str}.xlsx'

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    # Sheet 1: 선정 결과
    df_export = df_selected[[
        'name', 'ticker', 'category', 'sector', 'sub_sector',
        'score', 'market_cap', 'return_3m', 'return_6m',
        'golden_cross', 'rsi'
    ]].copy()
    
    df_export['market_cap'] = df_export['market_cap'] / 1e9
    df_export.columns = [
        '종목명', '티커', '대분류', '중분류', '세부분류',
        '종합점수', '시가총액(B$)', '3개월수익률(%)', '6개월수익률(%)',
        '골든크로스', 'RSI'
    ]
    
    df_export = df_export.round(2)
    df_export.to_excel(writer, sheet_name='선정결과', index=False)
    
    # Sheet 2: 전체 후보 종목
    df_all_export = df_all[[
        'name', 'ticker', 'category', 'sector', 'sub_sector',
        'score', 'market_cap', 'return_3m', 'return_6m'
    ]].copy()
    df_all_export['market_cap'] = df_all_export['market_cap'] / 1e9
    df_all_export.to_excel(writer, sheet_name='전체후보종목', index=False)
    
    # Sheet 3: 대분류별 통계
    category_stats = df_selected.groupby('category').agg({
        'score': 'mean',
        'return_3m': 'mean',
        'name': 'count'
    }).round(2)
    category_stats.columns = ['평균점수', '평균3개월수익률', '종목수']
    category_stats.to_excel(writer, sheet_name='대분류별통계')
    
    # Sheet 4: 점수 상위 종목
    top_scores = df_selected.nlargest(10, 'score')[[
        'name', 'category', 'sub_sector', 'score', 'return_3m'
    ]].copy()
    top_scores.columns = ['종목명', '대분류', '세부분류', '점수', '3개월수익률']
    top_scores.to_excel(writer, sheet_name='점수TOP10', index=False)
    
    # Sheet 5: 선정 기준
    criteria_df = pd.DataFrame({
        '평가항목': ['시가총액', '거래량', '3개월수익률', '6개월수익률', '기술적지표'],
        '배점': [30, 20, 20, 15, 15],
        '평가기준': [
            '1000억$↑: 30점, 500억$↑: 25점, 100억$↑: 20점...',
            '거래량 급증 여부 (최근20일 vs 60일)',
            '30%↑: 20점, 20%↑: 17점, 10%↑: 14점...',
            '40%↑: 15점, 25%↑: 12점, 10%↑: 9점...',
            '골든크로스, RSI 중립구간, 20일선 상향'
        ]
    })
    criteria_df.to_excel(writer, sheet_name='선정기준', index=False)

print(f"✅ Excel: {excel_file}")

# 3. Markdown 리포트 (analysis_reports/)
md_file = f'{ANALYSIS_DIR}/stock_selection_report_{date_str}.md'

with open(md_file, 'w', encoding='utf-8') as f:
    f.write(f"# 🔍 데이터센터 종목 선정 리포트\n\n")
    f.write(f"**Generated:** {timestamp}\n\n")
    f.write(f"---\n\n")
    
    f.write(f"## 📊 선정 결과\n\n")
    f.write(f"총 **{len(selected)}개** 종목 선정\n\n")
    
    # 대분류별 선정 종목
    for category in df_selected['category'].unique():
        category_stocks = df_selected[df_selected['category'] == category]
        f.write(f"### {category} ({len(category_stocks)}개)\n\n")
        
        for _, row in category_stocks.iterrows():
            f.write(f"- **[{row['sub_sector']}] {row['name']}**\n")
            f.write(f"  - 점수: {row['score']:.1f}/100\n")
            f.write(f"  - 시가총액: ${row['market_cap']/1e9:.1f}B\n")
            f.write(f"  - 3개월 수익률: {row['return_3m']:+.2f}%\n")
            f.write(f"  - RSI: {row['rsi']:.1f}\n")
            f.write(f"  - 골든크로스: {'✅' if row['golden_cross'] else '❌'}\n\n")
    
    f.write(f"---\n\n")
    
    # 점수 상위 종목
    top_10 = df_selected.nlargest(10, 'score')
    f.write(f"## 🏆 점수 상위 10개 종목\n\n")
    for idx, (_, row) in enumerate(top_10.iterrows(), 1):
        f.write(f"{idx}. **{row['name']}** ({row['category']})\n")
        f.write(f"   - 점수: {row['score']:.1f}, 3개월: {row['return_3m']:+.2f}%\n\n")
    
    f.write(f"---\n\n")
    
    # Python 코드 (main 스크립트용)
    f.write(f"## 📝 Python 코드 (복사용)\n\n")
    f.write(f"```python\n")
    f.write(f"STOCKS = [\n")
    for _, row in df_selected.iterrows():
        f.write(f"    {{'name': '{row['name']}', 'ticker': '{row['ticker']}', ")
        f.write(f"'sector': '{row['sector']}'}},\n")
    f.write(f"]\n")
    f.write(f"```\n")

print(f"✅ Markdown: {md_file}")

# ============================================================================
# TELEGRAM SUMMARY (요약만!)
# ============================================================================

print("\n" + "="*80)
print("📱 TELEGRAM SUMMARY")
print("="*80)

# 대분류별 카운트
category_counts = df_selected['category'].value_counts().to_dict()

summary = f"🔍 데이터센터 종목 선정 완료\n\n"
summary += f"📊 총 {len(selected)}개 종목 선정\n\n"

summary += f"📁 대분류별:\n"
for category, count in category_counts.items():
    summary += f"  • {category}: {count}개\n"

summary += f"\n🏆 점수 상위 5개:\n"
for idx, (_, row) in enumerate(df_selected.nlargest(5, 'score').iterrows(), 1):
    summary += f"{idx}. {row['name']} ({row['score']:.1f}점)\n"

summary += f"\n💾 저장:\n"
summary += f"- JSON: {os.path.basename(json_file)}\n"
summary += f"- Excel: {os.path.basename(excel_file)}\n"
summary += f"- Markdown: {os.path.basename(md_file)}\n\n"
summary += f"✅ GitHub에 push 완료\n"
summary += f"📄 상세 내용은 repo 파일 참조"

url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {"chat_id": TELEGRAM_CHAT_ID, "text": summary}

try:
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ 텔레그램 전송 성공!")
    else:
        print(f"❌ 전송 실패: {response.status_code}")
except Exception as e:
    print(f"❌ 오류: {e}")

print("\n" + "="*80)
print("✅ 작업 완료 - Data saved to repo, summary sent to Telegram")
print("💡 Tip: 매월 1일에 이 스크립트를 실행하여 종목을 업데이트하세요.")
print("="*80)
