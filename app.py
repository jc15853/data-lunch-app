import os
import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 CSV 데이터 로드
# -----------------------------------------------------------------------------
st.set_page_config(page_title="우리 학교 급식 데이터 분석기", page_icon="🍱", layout="wide")

st.title("🍱 우리 학교 급식 데이터 연구소")
st.caption("중1 정보 [2. 데이터] - 외부 식단표 CSV 데이터 연동 및 가공/시각화 실습")

@st.cache_data
def load_menu_csv():
    file_path = 'menu.csv'
    
    # CSV 파일 존재 여부 확인 및 불러오기
    if os.path.exists(file_path):
        # 한글 깨짐 방지 인코딩 적용 (utf-8-sig, cp949 순차 시도)
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp949')
            
        # CSV의 '비고' 컬럼 결측치(NaN) 처리
        if '비고' in df.columns:
            df['비고'] = df['비고'].fillna('')
        else:
            df['비고'] = ''
        
        # CSV의 알레르기 문자열("1,2,5")을 정수 리스트([1, 2, 5])로 가공
        def parse_allergy(x):
            if pd.isna(x) or str(x).strip() == '':
                return []
            return [int(i.strip()) for i in str(x).replace('.', ',').split(',') if i.strip().isdigit()]
            
        if '알레르기' in df.columns:
            df['알레르기_리스트'] = df['알레르기'].apply(parse_allergy)
        else:
            df['알레르기_리스트'] = [[] for _ in range(len(df))]
            
        return df
    else:
        st.error("⚠️ 'menu.csv' 파일이 같은 폴더에 존재하지 않습니다! 파일을 확인해 주세요.")
        st.stop()

df = load_menu_csv()

# -----------------------------------------------------------------------------
# 탭 구성: 데이터 가공 및 시각화
# -----------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["⚠️ 내 알레르기 식단 필터링", "📊 영양 데이터 시각화", "🔍 조건별 급식일 추출"])

# -----------------------------------------------------------------------------
# TAB 1: 알레르기 데이터 자동 매칭
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("1️⃣ 내 알레르기 번호를 입력하여 위험 메뉴 탐색하기")
    
    # 교육부 나이스(NEIS) 학교급식 알레르기 유발식품 19종 기준
    allergy_dict = {
        1: "난류", 2: "우유", 3: "메밀", 4: "땅콩", 5: "대두", 6: "밀", 7: "고등어", 8: "게", 9: "새우",
        10: "돼지고기", 11: "복숭아", 12: "토마토", 13: "아황산류", 14: "호두", 15: "닭고기", 16: "쇠고기",
        17: "오징어", 18: "조개류", 19: "잣"
    }
    
    selected_allergies = st.multiselect(
        "본인이 가진 알레르기를 선택하세요:",
        options=list(allergy_dict.keys()),
        format_func=lambda x: f"{x}번: {allergy_dict[x]}"
    )

    if selected_allergies:
        selected_names = [allergy_dict[code] for code in selected_allergies]
        st.warning(f"선택한 알레르기: {', '.join(selected_names)} ({selected_allergies})")
        
        def check_allergy(row_allergies):
            return any(code in row_allergies for code in selected_allergies)

        danger_df = df[df['알레르기_리스트'].apply(check_allergy)]
        
        st.write(f"⚠️ 주의해야 할 급식일은 총 **{len(danger_df)}일**입니다.")
        
        # CSV 컬럼 구성에 맞춰 안전하게 데이터프레임 출력
        show_cols = [col for col in ['날짜', '메뉴', '비고'] if col in danger_df.columns]
        st.dataframe(danger_df[show_cols], use_container_width=True)
    else:
        st.info("위에서 알레르기 항목을 선택하면 CSV 데이터에서 해당되는 날을 자동으로 검색해 줍니다.")

# -----------------------------------------------------------------------------
# TAB 2: 데이터 시각화
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("2️⃣ 급식 영양 데이터 시각화")
    
    # 데이터 내 존재하는 영양소 컬럼만 선택 옵션으로 제공
    all_metrics = ["에너지", "단백질", "칼슘", "철"]
    available_metrics = [m for m in all_metrics if m in df.columns]
    
    if available_metrics:
        metric_type = st.selectbox("시각화할 영양소 데이터를 선택하세요:", available_metrics)
        
        if "날짜" in df.columns:
            st.bar_chart(df.set_index("날짜")[metric_type])
        else:
            st.bar_chart(df[metric_type])
        
        # 데이터 가공을 통한 최고값 자동 탐색
        max_row = df.sort_values(by=metric_type, ascending=False).iloc[0]
        date_str = max_row['날짜'] if '날짜' in max_row else "해당일"
        menu_str = max_row['메뉴'] if '메뉴' in max_row else "메뉴 정보 없음"
        
        st.success(f"💡 **{metric_type}** 수치가 가장 높은 날은 **{date_str}**이며, 수치는 **{max_row[metric_type]}**입니다. (메뉴: {menu_str})")
    else:
        st.error("영양소 컬럼(에너지, 단백질, 칼슘, 철)을 CSV 파일에서 찾을 수 없습니다.")

# -----------------------------------------------------------------------------
# TAB 3: 조건문 필터링
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("3️⃣ 조건문(Logic)을 활용한 특정 조건 급식일 추출")
    
    if '비고' in df.columns:
        event_filter = st.checkbox("특별 행사일/특식일만 보기", value=False)
        
        if event_filter:
            # 비고란에 내용이 있는 항목만 필터링
            filtered_menu = df[df['비고'].str.strip() != ""]
            st.write("📋 **특이사항/행사 표기가 있는 급식일 목록**")
        else:
            filtered_menu = df
            st.write("📋 **전체 급식 제공 데이터 목록**")
    else:
        filtered_menu = df
        st.write("📋 **전체 급식 제공 데이터 목록**")

    show_cols_tab3 = [col for col in ['날짜', '메뉴', '에너지', '비고'] if col in filtered_menu.columns]
    st.dataframe(filtered_menu[show_cols_tab3], use_container_width=True)
    st.metric("총 급식 일수", f"{len(filtered_menu)} 일")
