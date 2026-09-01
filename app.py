import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 라이트 모드 디자인
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="급식 데이터 분석기",
    page_icon="🍱",
    layout="centered"
)

# 글자가 또렷하게 보이는 라이트 스타일
custom_css = """
<style>
    .stApp {
        background-color: #ffffff !important;
        color: #1f2937 !important;
        font-family: 'Pretendard', -apple-system, sans-serif;
    }
    h1, h2, h3, h4 {
        color: #047857 !important;
        font-weight: bold !important;
    }
    p, span, label, div {
        color: #1f2937 !important;
    }
    .data-card {
        background-color: #f0fdf4;
        border: 2px solid #16a34a;
        border-radius: 12px;
        padding: 20px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .badge {
        background-color: #dcfce7;
        color: #15803d !important;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.title("🍱 [개발자 모드] 우리 학교 급식 데이터 분석기")
st.caption("중1 정보 [2. 데이터] - 데이터 수집, 데이터 유형 구분, 시각화 및 정보 가공")

st.info("""
💡 **학습 목표:**
급식 메뉴와 관련된 수집 데이터(문자, 정수, 실수, 참/거짓)를 분류하고, 
데이터를 시각화하여 **"잔반을 줄이기 위한 유용한 정보"**로 가공해봅시다.
""")

st.divider()

# -----------------------------------------------------------------------------
# Step 1. 데이터 수집 및 데이터 유형(Data Type) 구조 정의
# -----------------------------------------------------------------------------
st.markdown("### 1️⃣ 수집된 급식 데이터와 데이터 유형(Data Type)")

# 세션 상태에 기본 급식 데이터 저장
if "meal_data" not in st.session_state:
    st.session_state.meal_data = pd.DataFrame([
        {"날짜": "10/01", "메뉴명": "치킨마요덮밥", "잔반량(kg)": 12.5, "만족도(5점)": 5, "선호메뉴여부": True},
        {"날짜": "10/02", "메뉴명": "시래기국밥", "잔반량(kg)": 45.0, "만족도(5점)": 2, "선호메뉴여부": False},
        {"날짜": "10/03", "메뉴명": "돈까스", "잔반량(kg)": 15.0, "만족도(5점)": 5, "선호메뉴여부": True},
        {"날짜": "10/04", "메뉴명": "해물순두부찌개", "잔반량(kg)": 38.2, "만족도(5점)": 3, "선호메뉴여부": False},
        {"날짜": "10/05", "메뉴명": "스파게티", "잔반량(kg)": 18.4, "만족도(5점)": 4, "선호메뉴여부": True},
    ])

df = st.session_state.meal_data

# 표 형태로 수집된 데이터 출력
st.dataframe(df, use_container_width=True)

# 데이터 유형 개념 확인
with st.expander("🔍 [개념 정리] 이 데이터들의 컴퓨터 내부 표현 방식(유형)은?"):
    st.markdown("""
    * **메뉴명 (`"치킨마요덮밥"`)** ➔ <span class="badge">문자(String) 데이터</span>
    * **잔반량 (`12.5`)** ➔ <span class="badge">실수(Float) 데이터</span> (소수점이 포함된 숫자)
    * **만족도 (`5`)** ➔ <span class="badge">정수(Integer) 데이터</span> (소수점이 없는 숫자)
    * **선호메뉴여부 (`True / False`)** ➔ <span class="badge">불리언(Boolean) 참/거짓 데이터</span>
    """, unsafe_allow_html=True)

st.divider()

# -----------------------------------------------------------------------------
# Step 2. 새로운 급식 데이터 수집(입력) 및 데이터 추가
# -----------------------------------------------------------------------------
st.markdown("### 2️⃣ 새로운 급식 데이터 수집하기 (학생 입력)")

col1, col2, col3, col4 = st.columns(4)

with col1:
    new_date = st.text_input("날짜 (문자)", value="10/06")
with col2:
    new_menu = st.text_input("메뉴명 (문자)", value="제육볶음")
with col3:
    new_leftover = st.number_input("잔반량(kg) (실수)", min_value=0.0, max_value=100.0, value=16.0, step=0.1)
with col4:
    new_score = st.slider("만족도 (정수)", min_value=1, max_value=5, value=4)

new_is_favorite = st.checkbox("학생들이 선호하는 메뉴인가요? (참/거짓)", value=True)

if st.button("➕ 수집 데이터 표에 추가하기", use_container_width=True):
    new_row = pd.DataFrame([{
        "날짜": new_date,
        "메뉴명": new_menu,
        "잔반량(kg)": new_leftover,
        "만족도(5점)": new_score,
        "선호메뉴여부": new_is_favorite
    }])
    st.session_state.meal_data = pd.concat([st.session_state.meal_data, new_row], ignore_index=True)
    st.rerun()

st.divider()

# -----------------------------------------------------------------------------
# Step 3. 데이터 가공 및 정보(Information) 창출 (시각화)
# -----------------------------------------------------------------------------
st.markdown("### 3️⃣ 데이터 시각화 ➔ 정보 가공")

m_col1, m_col2 = st.columns(2)

with m_col1:
    avg_leftover = df["잔반량(kg)"].mean()
    st.metric(label="📊 평균 잔반량", value=f"{avg_leftover:.1f} kg")

with m_col2:
    avg_score = df["만족도(5점)"].mean()
    st.metric(label="⭐ 평균 학생 만족도", value=f"{avg_score:.1f} 점")

st.markdown("#### 📈 메뉴별 잔반량 비교 (막대그래프)")
st.bar_chart(df.set_index("메뉴명")["잔반량(kg)"])

# -----------------------------------------------------------------------------
# Step 4. 데이터 분석 기반 급식 개선 로직
# -----------------------------------------------------------------------------
st.divider()
st.markdown("### 4️⃣ 데이터 분석 결과 및 개선안 리포트")

if st.button("🚀 데이터 분석 리포트 생성", type="primary", use_container_width=True):
    
    worst_row = df.sort_values(by="잔반량(kg)", ascending=False).iloc[0]
    best_row = df.sort_values(by="만족도(5점)", ascending=False).iloc[0]
    
    report_html = f"""
    <div class="data-card">
        <h3 style="margin-top:0; color: #047857;">[ 급식 데이터 분석 리포트 ]</h3>
        <p><strong>1. 잔반이 가장 많은 메뉴:</strong> <span style="color:#dc2626; font-weight:bold;">{worst_row['메뉴명']} ({worst_row['잔반량(kg)']}kg)</span></p>
        <p><strong>2. 만족도가 가장 높은 메뉴:</strong> <span style="color:#2563eb; font-weight:bold;">{best_row['메뉴명']} ({best_row['만족도(5점)']}점)</span></p>
        <hr style="border-color: #bbf7d0;">
        <p><strong>💡 데이터 기반 개선 솔루션:</strong></p>
        <ul>
            <li>잔반량이 높은 <b>[{worst_row['메뉴명']}]</b> 메뉴는 조리 방식을 변경하거나 배식량을 조정할 필요가 있습니다.</li>
            <li>선호도가 높은 메뉴의 공통 데이터 유형적 특징을 분석하여 식단 구성 비율을 높여야 합니다.</li>
        </ul>
    </div>
    """
    st.markdown(report_html, unsafe_allow_html=True)
