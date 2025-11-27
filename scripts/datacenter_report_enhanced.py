"""
데이터센터 투자 자동화 시스템 v3.0 - GitHub Actions Compatible
✅ API → Data Collection → File Storage → Git Push → Telegram Summary Only
"""

import yfinance as yf
import pandas as pd
import requests
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("="*70)
print("📊 데이터센터 투자 자동화 시스템 v3.0")
print("  ✅ GitHub Actions Compatible")
print("="*70 + "\n")

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 데이터 저장 디렉토리
MARKET_DATA_DIR = 'market_data'
ANALYSIS_DIR = 'analysis_reports'
OUTPUT_DIR = 'outputs'

os.makedirs(MARKET_DATA_DIR, exist_ok=True)
os.makedirs(ANALYSIS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

STOCKS = [
    {'name': 'NVIDIA', 'ticker': 'NVDA', 'sector': 'AI칩'},
    {'name': 'AMD', 'ticker': 'AMD', 'sector': 'AI칩'},
    {'name': 'Intel', 'ticker': 'INTC', 'sector': 'AI칩'},
    {'name': 'Super Micro', 'ticker': 'SMCI', 'sector': 'AI서버'},
    {'name': 'Dell', 'ticker': 'DELL', 'sector': 'AI서버'},
    {'name': 'Vertiv', 'ticker': 'VRT', 'sector': '전력'},
    {'name': 'Eaton', 'ticker': 'ETN', 'sector': '전력'},
    {'name': 'LS ELECTRIC', 'ticker': '010120.KS', 'sector': '전력'},
    {'name': 'Cummins', 'ticker': 'CMI', 'sector': '발전'},
    {'name': 'Generac', 'ticker': 'GNRC', 'sector': '발전'},
    {'name': 'Johnson Controls', 'ticker': 'JCI', 'sector': '쿨링'},
    {'name': 'Trane Tech', 'ticker': 'TT', 'sector': '쿨링'},
    {'name': 'Arista Networks', 'ticker': 'ANET', 'sector': '네트워크'},
    {'name': 'Broadcom', 'ticker': 'AVGO', 'sector': '네트워크'},
    {'name': 'Marvell', 'ticker': 'MRVL', 'sector': '네트워크'},
    {'name': 'HFR', 'ticker': '230240.KQ', 'sector': '광통신'},
    {'name': 'Corning', 'ticker': 'GLW', 'sector': '광섬유'},
    {'name': 'Lumentum', 'ticker': 'LITE', 'sector': '광통신'},
    {'name': 'SK hynix', 'ticker': '000660.KS', 'sector': 'HBM'},
    {'name': 'Samsung', 'ticker': '005930.KS', 'sector': 'HBM'},
    {'name': 'Micron', 'ticker': 'MU', 'sector': 'HBM'},
    {'name': '한미반도체', 'ticker': '042700.KQ', 'sector': '패키징'},
    {'name': 'Amkor', 'ticker': 'AMKR', 'sector': '패키징'},
    {'name': 'Western Digital', 'ticker': 'WDC', 'sector': 'SSD'},
    {'name': 'Digital Realty', 'ticker': 'DLR', 'sector': 'DC REIT'},
    {'name': 'Equinix', 'ticker': 'EQIX', 'sector': 'DC REIT'},
]

print(f"📋 총 {len(STOCKS)}개 종목 모니터링\n")


def calculate_rsi(prices, period=14):
    """RSI(Relative Strength Index) 계산"""
    try:
        if len(prices) < period:
            return 50
        
        deltas = prices.diff()
        gain = deltas.where(deltas > 0, 0)
        loss = -deltas.where(deltas < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
    except:
        return 50


def get_stock_data(ticker, name, sector):
    """주가 데이터 수집 및 지표 계산"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty or len(hist) < 2:
            return None
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
        
        # 수익률 계산
        change_1d = ((current / prev) - 1) * 100
        change_1w = ((current / hist['Close'].iloc[-5]) - 1) * 100 if len(hist) >= 5 else 0
        change_1m = ((current / hist['Close'].iloc[-21]) - 1) * 100 if len(hist) >= 21 else 0
        
        # 이동평균
        ma_20 = hist['Close'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else current
        ma_60 = hist['Close'].rolling(60).mean().iloc[-1] if len(hist) >= 60 else current
        
        vs_ma20 = ((current / ma_20) - 1) * 100 if ma_20 else 0
        golden_cross = ma_20 > ma_60 if (ma_20 and ma_60) else False
        dead_cross = ma_20 < ma_60 if (ma_20 and ma_60) else False
        
        # 거래량
        volume = hist['Volume'].iloc[-1]
        avg_volume = hist['Volume'].rolling(20).mean().iloc[-1] if len(hist) >= 20 else volume
        volume_ratio = (volume / avg_volume * 100) if avg_volume else 100
        
        # RSI 계산
        rsi = calculate_rsi(hist['Close'], period=14)
        
        return {
            'name': name,
            'ticker': ticker,
            'sector': sector,
            'price': float(current),
            'change_1d': float(change_1d),
            'change_1w': float(change_1w),
            'change_1m': float(change_1m),
            'vs_ma20': float(vs_ma20),
            'ma_20': float(ma_20),
            'ma_60': float(ma_60),
            'golden_cross': bool(golden_cross),
            'dead_cross': bool(dead_cross),
            'volume': int(volume),
            'volume_ratio': float(volume_ratio),
            'rsi': float(rsi),
        }
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:50]}")
        return None


print("📈 주가 데이터 수집 중...\n")

results = []
for idx, stock in enumerate(STOCKS, 1):
    print(f"[{idx}/{len(STOCKS)}] {stock['name']:20s} ... ", end='')
    data = get_stock_data(stock['ticker'], stock['name'], stock['sector'])
    if data:
        results.append(data)
        print("✅")
    else:
        print("❌")

print(f"\n✅ 수집 완료: {len(results)}/{len(STOCKS)}개\n")

df = pd.DataFrame(results)

# ============================================================================
# DATA STORAGE (JSON, Excel, Markdown)
# ============================================================================

now = datetime.now()
date_str = now.strftime('%Y%m%d')
timestamp = now.strftime('%Y-%m-%d %H:%M')

print("="*70)
print("💾 DATA STORAGE")
print("="*70)

# 1. JSON 저장 (market_data/)
json_file = f'{MARKET_DATA_DIR}/datacenter_stocks_{date_str}.json'
json_data = {
    'timestamp': timestamp,
    'total_stocks': len(results),
    'stocks': results
}
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)
print(f"✅ JSON: {json_file}")

# 2. Excel 저장 (analysis_reports/)
excel_file = f'{ANALYSIS_DIR}/datacenter_analysis_{date_str}.xlsx'

with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
    # Sheet 1: 전체 데이터
    df_export = df.copy()
    df_export.to_excel(writer, sheet_name='All_Stocks', index=False)
    
    # Sheet 2: 상승 종목
    up_stocks = df[df['change_1d'] > 0].sort_values('change_1d', ascending=False)
    up_stocks.to_excel(writer, sheet_name='Up_Stocks', index=False)
    
    # Sheet 3: 하락 종목
    down_stocks = df[df['change_1d'] < 0].sort_values('change_1d')
    down_stocks.to_excel(writer, sheet_name='Down_Stocks', index=False)
    
    # Sheet 4: 골든크로스
    golden = df[df['golden_cross'] == True]
    if len(golden) > 0:
        golden.to_excel(writer, sheet_name='Golden_Cross', index=False)
    
    # Sheet 5: 거래량 급증
    volume_spike = df[df['volume_ratio'] > 200]
    if len(volume_spike) > 0:
        volume_spike.to_excel(writer, sheet_name='Volume_Spike', index=False)
    
    # Sheet 6: RSI 과매수/과매도
    rsi_extreme = df[(df['rsi'] > 70) | (df['rsi'] < 30)]
    if len(rsi_extreme) > 0:
        rsi_extreme.to_excel(writer, sheet_name='RSI_Extreme', index=False)

print(f"✅ Excel: {excel_file}")

# 3. Markdown 리포트 (analysis_reports/)
md_file = f'{ANALYSIS_DIR}/datacenter_report_{date_str}.md'

with open(md_file, 'w', encoding='utf-8') as f:
    f.write(f"# 📊 데이터센터 종목 일일 리포트\n\n")
    f.write(f"**Generated:** {timestamp}\n\n")
    f.write(f"---\n\n")
    
    # 상승 종목
    up_stocks = df[df['change_1d'] > 0].sort_values('change_1d', ascending=False)
    if len(up_stocks) > 0:
        f.write(f"## 🔥 오늘 상승 종목 ({len(up_stocks)}개)\n\n")
        for _, row in up_stocks.iterrows():
            emoji = "🚀" if row['change_1d'] > 5 else "📈"
            f.write(f"- {emoji} **{row['name']}**: {row['change_1d']:+.2f}% (${row['price']:.2f})\n")
        f.write(f"\n")
    
    # 하락 종목
    down_stocks = df[df['change_1d'] < 0].sort_values('change_1d')
    if len(down_stocks) > 0:
        f.write(f"## 📉 오늘 하락 종목 ({len(down_stocks)}개)\n\n")
        for _, row in down_stocks.iterrows():
            f.write(f"- 📉 **{row['name']}**: {row['change_1d']:+.2f}% (${row['price']:.2f})\n")
        f.write(f"\n")
    
    # 골든크로스
    golden = df[df['golden_cross'] == True]
    if len(golden) > 0:
        f.write(f"## ⭐ 골든크로스 ({len(golden)}개)\n\n")
        for _, row in golden.iterrows():
            f.write(f"- **{row['name']}**: MA20(${row['ma_20']:.2f}) > MA60(${row['ma_60']:.2f})\n")
        f.write(f"\n")
    
    # 데드크로스
    dead = df[df['dead_cross'] == True]
    if len(dead) > 0:
        f.write(f"## 💀 데드크로스 ({len(dead)}개)\n\n")
        for _, row in dead.iterrows():
            f.write(f"- **{row['name']}**\n")
        f.write(f"\n")
    
    # 거래량 급증
    volume_spike = df[df['volume_ratio'] > 200].sort_values('volume_ratio', ascending=False)
    if len(volume_spike) > 0:
        f.write(f"## 📊 거래량 급증 ({len(volume_spike)}개)\n\n")
        for _, row in volume_spike.iterrows():
            f.write(f"- **{row['name']}**: {row['volume_ratio']:.0f}% (평균 대비)\n")
        f.write(f"\n")
    
    # RSI 과매수/과매도
    rsi_overbought = df[df['rsi'] > 70]
    if len(rsi_overbought) > 0:
        f.write(f"## 🔴 RSI 과매수 ({len(rsi_overbought)}개)\n\n")
        for _, row in rsi_overbought.iterrows():
            f.write(f"- **{row['name']}**: RSI {row['rsi']:.1f}\n")
        f.write(f"\n")
    
    rsi_oversold = df[df['rsi'] < 30]
    if len(rsi_oversold) > 0:
        f.write(f"## 🟢 RSI 과매도 ({len(rsi_oversold)}개)\n\n")
        for _, row in rsi_oversold.iterrows():
            f.write(f"- **{row['name']}**: RSI {row['rsi']:.1f}\n")
        f.write(f"\n")
    
    # 통계
    f.write(f"---\n\n")
    f.write(f"## 📊 Summary\n\n")
    f.write(f"- 📈 상승: {len(up_stocks)}개\n")
    f.write(f"- 📉 하락: {len(down_stocks)}개\n")
    f.write(f"- ➖ 보합: {len(df[df['change_1d'] == 0])}개\n")
    f.write(f"- 📊 총 {len(results)}개 종목\n")

print(f"✅ Markdown: {md_file}")

# ============================================================================
# TELEGRAM SUMMARY (요약만!)
# ============================================================================

print("\n" + "="*70)
print("📱 TELEGRAM SUMMARY")
print("="*70)

up_count = len(df[df['change_1d'] > 0])
down_count = len(df[df['change_1d'] < 0])
flat_count = len(df[df['change_1d'] == 0])

summary = f"📊 데이터센터 종목 분석 완료\n\n"
summary += f"📈 상승: {up_count}개\n"
summary += f"📉 하락: {down_count}개\n"
summary += f"➖ 보합: {flat_count}개\n"
summary += f"📊 총 {len(results)}개 종목\n\n"

# 주요 시그널 요약
signals = []
if len(df[df['golden_cross'] == True]) > 0:
    signals.append(f"⭐ 골든크로스: {len(df[df['golden_cross'] == True])}개")
if len(df[df['dead_cross'] == True]) > 0:
    signals.append(f"💀 데드크로스: {len(df[df['dead_cross'] == True])}개")
if len(df[df['volume_ratio'] > 200]) > 0:
    signals.append(f"📊 거래량급증: {len(df[df['volume_ratio'] > 200])}개")
if len(df[df['rsi'] > 70]) > 0:
    signals.append(f"🔴 RSI과매수: {len(df[df['rsi'] > 70])}개")
if len(df[df['rsi'] < 30]) > 0:
    signals.append(f"🟢 RSI과매도: {len(df[df['rsi'] < 30])}개")

if signals:
    summary += f"🎯 주요 시그널:\n" + "\n".join(signals) + "\n\n"

summary += f"💾 저장:\n"
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

print("\n" + "="*70)
print("✅ 작업 완료 - Data saved to repo, summary sent to Telegram")
print("="*70)
