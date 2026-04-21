import streamlit as st
import requests
import urllib.parse
import time

# 웹 앱 페이지 설정
st.set_page_config(page_title="이치방쿠지 통털이 계산기", page_icon="🐉", layout="centered")

# CSS로 입력창 간격 및 디자인 미세 조정
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #FF4B4B; color: white; font-weight: bold; margin-top: 20px; }
    div[data-testid="stHorizontalBlock"] { align-items: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🐉 이치방쿠지 통털이 계산기")
st.caption("번개장터 최신 실거래 '최저가' 기준 분석")

# --- 시세 추출 함수 (보수적 최저가) ---
def get_bunjang_safe_price(keyword):
    search_term = keyword.lower()
    encoded_keyword = urllib.parse.quote(search_term)
    recent_prices = []
    bad_keywords = ["일괄", "세트", "set", "전부", "다해서", "포함", "처분", "정리", "예약", "결제창"]

    try:
        bj_url = f"https://api.bunjang.co.kr/api/1/find_v2.json?q={encoded_keyword}&n=15&order=date&status=3"
        bj_res = requests.get(bj_url, timeout=5).json()
        for item in bj_res.get('list', []):
            if len(recent_prices) >= 3: break
            title = item.get('name', '').lower()
            price = int(item.get('price', 0))
            if any(bad in title for bad in bad_keywords): continue
            if 10000 < price < 2000000:
                recent_prices.append(price)
    except: pass
    return min(recent_prices) if recent_prices else 0

# --- 기본 정보 입력 섹션 ---
with st.expander("📌 기본 정보 입력", expanded=True):
    series_name = st.text_input("시리즈명", placeholder="예: 헌터헌터")
    c1, c2 = st.columns(2)
    with c1:
        unit_price = st.text_input("회당 가격", placeholder="숫자만 입력")
    with c2:
        remains = st.text_input("남은 장수", placeholder="숫자만 입력")

# --- 상위상 설정 섹션 (개선된 GUI) ---
st.divider()
st.subheader("💎 남은 상위상 설정")
has_prizes = st.radio("상위상 유무", ["없음", "있음"], horizontal=True, label_visibility="collapsed")

prize_data = []
if has_prizes == "있음":
    # 4개의 슬롯을 한 줄씩 배치
    for i in range(4):
        # 종류(Column 1)와 개수(Column 2)를 한 줄에 배치
        col1, col2 = st.columns([2, 1]) 
        with col1:
            p_type = st.selectbox(f"상위상 {i+1} 종류", ["-", "A", "B", "C", "D", "E", "F"], key=f"type_{i}", label_visibility="visible")
        with col2:
            p_count = st.number_input(f"개수", min_value=1, value=1, key=f"count_{i}")
        
        if p_type != "-":
            prize_data.append((p_type, p_count))

# --- 분석 실행 ---
if st.button("💰 수익성 분석 시작"):
    if not series_name or not unit_price or not remains:
        st.error("필수 정보를 입력해주세요!")
    else:
        with st.spinner('최신 시세를 분석 중입니다...'):
            try:
                total_investment = int(unit_price) * int(remains)
                total_market_value = 0
                
                st.subheader("📊 상세 시세 현황")
                
                # 라스트원 시세
                lo_price = get_bunjang_safe_price(f"{series_name} 라스트원")
                total_market_value += lo_price
                st.info(f"📦 **라스트원**: {lo_price:,}원")
                
                # 상위상 시세
                for pt, pc in prize_data:
                    p_val = get_bunjang_safe_price(f"{series_name} {pt}상")
                    if p_val == 0: p_val = get_bunjang_safe_price(f"{series_name} {pt}")
                    total_market_value += (p_val * pc)
                    st.write(f"💎 **{pt}상**(x{pc}): {p_val:,}원")
                    time.sleep(0.3)

                # 최종 결과
                profit = total_market_value - total_investment
                st.divider()
                
                c_res1, c_res2 = st.columns(2)
                c_res1.metric("총 투자금", f"{total_investment:,}원")
                c_res2.metric("예상 회수액", f"{int(total_market_value):,}원")
                
                st.metric("최종 예상 수익", f"{profit:,}원", delta=f"{profit:,}원")
                
                if profit > 0:
                    st.balloons()
                    st.success("✅ 결론: 통털이 추천!")
                else:
                    st.warning("❌ 결론: 비추천 (손해 예상)")
            except ValueError:
                st.error("가격과 장수에는 숫자만 입력 가능합니다.")