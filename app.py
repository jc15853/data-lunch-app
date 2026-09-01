import io
import os
import re
import requests
import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# -----------------------------------------------------------------------------
# 0. 페이지 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(page_title="스마트 급식 데이터 식단 연구소", page_icon="🍱", layout="wide")

if 'my_menu' not in st.session_state:
    st.session_state.my_menu = []
if 'chef_note' not in st.session_state:
    st.session_state.chef_note = ""

# -----------------------------------------------------------------------------
# 1. 데이터 로드 및 폰트/유틸리티 함수
# -----------------------------------------------------------------------------
@st.cache_data
def load_menu():
    try:
        return pd.read_csv('menu.csv')
    except Exception:
        # 파일이 없을 때 대비용 확장 기본 데이터
        return pd.DataFrame({
            '메뉴명': ['통밀밥', '콩나물국', '제육볶음', '배추김치', '샤인머스캣', '마라탕', '치킨마요덮밥'],
            '카테고리': ['밥', '국', '메인반찬', '김치', '후식', '메인반찬', '밥'],
            '칼로리(kcal)': [250, 45, 380, 25, 60, 520, 480],
            '단백질(g)': [5.0, 4.0, 25.0, 1.0, 1.0, 18.0, 20.0],
            '나트륨(mg)': [10, 450, 620, 320, 5, 1100, 750],
            '이미지url': ['https://via.placeholder.com/150'] * 7
        })

# 세션 상태에 데이터프레임 저장 (학생들이 새로 등록한 데이터 유지를 위함)
if 'menu_df' not in st.session_state:
    st.session_state.menu_df = load_menu()

df_menu = st.session_state.menu_df

@st.cache_resource
def get_korean_font(size):
    font_filename = "NanumGothic.ttf"
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    if not os.path.exists(font_filename):
        try:
            res = requests.get(font_url, timeout=5)
            with open(font_filename, "wb") as f:
                f.write(res.content)
        except Exception:
            pass
    try:
        return ImageFont.truetype(font_filename, size)
    except Exception:
        return ImageFont.load_default()

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U00010000-\U0010FFFF"
        "\u2600-\u27BF"
        "\u2300-\u23FF"
        "\u2B00-\u2BFF"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text).strip()

# PNG 이미지 카드 생성 함수
def generate_menu_card(menu_list, total_cal, total_protein, total_sodium, note):
    width, height = 650, 800
    img = Image.new('RGB', (width, height), color='#FFFFFF')
    draw = ImageDraw.Draw(img)

    font_title = get_korean_font(22)
    font_sub = get_korean_font(13)
    font_body = get_korean_font(14)
    font_bold = get_korean_font(15)

    clean_note = remove_emojis(note)

    # 테두리 및 헤더
    draw.rectangle([(10, 10), (width-10, height-10)], outline='#047857', width=3)
    draw.rectangle([(20, 20), (width-20, 85)], fill='#ECFDF5')
    draw.text((width//2, 40), "[내가 만든 오늘의 급식 식단표]", fill='#047857', font=font_title, anchor="mm")
    draw.text((width//2, 68), "중1 정보 데이터 분석 & 영양 진단 결과", fill='#4B5563', font=font_sub, anchor="mm")

    # 메뉴 목록
    draw.text((30, 105), "[선택한 급식 메뉴 데이터]", fill='#1F2937', font=font_bold)
    draw.line([(30, 128), (width-30, 128)], fill='#E5E7EB', width=1)

    y_offset = 140
    for item in menu_list:
        clean_name = remove_emojis(item['메뉴명'])
        text_line = f"• [{item['카테고리']}] {clean_name}"
        info_line = f"{item['칼로리(kcal)']} kcal | 단백질 {item['단백질(g)']}g | 나트륨 {item['나트륨(mg)']}mg"
        
        draw.text((40, y_offset), text_line, fill='#1F2937', font=font_bold)
        draw.text((width-40, y_offset), info_line, fill='#4B5563', font=font_body, anchor="ra")
        y_offset += 32

    # 영양 성분 정산 영역
    draw.rectangle([(30, 450), (width-30, 580)], fill='#F9FAFB', outline='#E5E7EB')
    draw.text((50, 470), "총 칼로리 (정수):", fill='#374151', font=font_body)
    draw.text((width-50, 470), f"{total_cal} kcal (권장: 600~800)", fill='#047857', font=font_bold, anchor="ra")

    draw.text((50, 505), "총 단백질 (실수):", fill='#374151', font=font_body)
    draw.text((width-50, 505), f"{total_protein:.1f} g (권장: 20g 이상)", fill='#16A34A', font=font_bold, anchor="ra")

    draw.text((50, 540), "총 나트륨 (정수):", fill='#374151', font=font_body)
    draw.text((width-50, 540), f"{total_sodium} mg (권장: 1000mg 이하)", fill='#DC2626', font=font_bold, anchor="ra")

    # 학생 영양사 피드백 영역
    draw.rectangle([(30, 600), (width-30, 760)], fill='#FEF3C7', outline='#F59E0B')
    draw.text((45, 615), "[학생 데이터 분석가의 한마디]", fill='#B45309', font=font_bold)

    lines = []
    words = clean_note.split(' ')
    curr_line = ""
    for w in words:
        if len(curr_line + w) > 32:
            lines.append(curr_line)
            curr_line = w + " "
        else:
            curr_line += w + " "
    lines.append(curr_line)

    ry = 645
    for line in lines[:4]:
        draw.text((45, ry), line.strip(), fill='#4B5563', font=font_body)
        ry += 22

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# -----------------------------------------------------------------------------
# 2. 메인 UI 화면 구성
# -----------------------------------------------------------------------------
st.title("🍱 중1 정보 [2.데이터] 스마트 급식 데이터 연구소")
st.caption("수집된 메뉴 데이터를 조합하고 가공하여 영양 균형을 분석하는 프로그래밍 프로젝트입니다.")

# 데이터 단원 개념 학습 서브 탭
tabs = st.tabs(["🍽️ 급식 식단 짜기 및 분석", "📥 새로운 메뉴 데이터 수집/등록", "🔍 데이터 유형(Type) 개념 확인"])

# -----------------------------------------------------------------------------
# TAB 1: 급식 식단 짜기 및 분석 (기존 메인 기능 발전)
# -----------------------------------------------------------------------------
with tabs[0]:
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("📋 메뉴 데이터베이스 (검색 & 선택)")
        
        # 카테고리 필터링
        categories = ["전체"] + list(df_menu['카테고리'].unique())
        selected_cat = st.selectbox("카테고리 필터링:", categories)
        
        if selected_cat != "전체":
            filtered_df = df_menu[df_menu['카테고리'] == selected_cat]
        else:
            filtered_df = df_menu

        # 메뉴 카드 출력
        grid_cols = st.columns(2)
        for idx, row in filtered_df.iterrows():
            with grid_cols[idx % 2]:
                st.markdown(
                    f'<div style="border: 1px solid #E5E7EB; border-radius: 10px; padding: 10px; margin-bottom: 10px; background-color: #FFFFFF;">'
                    f'<img src="{row["이미지url"]}" style="width: 100%; height: 90px; object-fit: cover; border-radius: 6px;" />'
                    f'<h4 style="margin: 8px 0 4px 0; color:#047857;">[{row["카테고리"]}] {row["메뉴명"]}</h4>'
                    f'<p style="font-size: 13px; color: #4B5563; margin: 0;">🔥 {row["칼로리(kcal)"]}kcal | 💪 {row["단백질(g)"]}g | 🧂 {row["나트륨(mg)"]}mg</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                
                # 버튼 로직
                is_selected = any(m['메뉴명'] == row['메뉴명'] for m in st.session_state.my_menu)
                if is_selected:
                    if st.button(f"❌ {row['메뉴명']} 빼기", key=f"del_{idx}", use_container_width=True):
                        st.session_state.my_menu = [m for m in st.session_state.my_menu if m['메뉴명'] != row['메뉴명']]
                        st.rerun()
                else:
                    if st.button(f"➕ {row['메뉴명']} 담기", key=f"add_{idx}", use_container_width=True):
                        st.session_state.my_menu.append(row.to_dict())
                        st.rerun()

    with col_right:
        st.subheader("🍽️ 내 식판 데이터 연산")
        
        if not st.session_state.my_menu:
            st.info("왼쪽에서 식판에 담을 메뉴를 선택해 주세요!")
        else:
            # 1. 수집 데이터 정산 (연산 가공)
            total_cal = sum(int(m['칼로리(kcal)']) for m in st.session_state.my_menu)
            total_protein = sum(float(m['단백질(g)']) for m in st.session_state.my_menu)
            total_sodium = sum(int(m['나트륨(mg)']) for m in st.session_state.my_menu)

            # 담긴 메뉴 리스트
            for item in st.session_state.my_menu:
                st.text(f"• [{item['카테고리']}] {item['메뉴명']} ({item['칼로리(kcal)']}kcal)")

            st.divider()
            st.subheader("📊 영양 데이터 가공 및 시각화")

            c1, c2, c3 = st.columns(3)
            c1.metric("총 칼로리", f"{total_cal} kcal")
            c2.metric("총 단백질", f"{total_protein:.1f} g")
            c3.metric("총 나트륨", f"{total_sodium} mg")

            # 🔥 [발전 기능] 데이터 시각화 차트 추가 (권장량 대비 비율)
            st.markdown("#### 📈 권장량 대비 영양성분 비율 (%)")
            chart_data = pd.DataFrame({
                "영양소": ["칼로리(800kcal기준)", "단백질(20g기준)", "나트륨(1000mg기준)"],
                "달성률(%)": [
                    min(150, int((total_cal / 800) * 100)),
                    min(150, int((total_protein / 20) * 100)),
                    min(150, int((total_sodium / 1000) * 100))
                ]
            }).set_index("영양소")
            st.bar_chart(chart_data)

            # -------------------------------------------------------------
            # 💡 [핵심 알고리즘] 중1 수준 조건문(if-elif-else) 진단
            # -------------------------------------------------------------
            st.markdown("#### 🔍 조건문(Logic) 기반 영양 진단")
            
            # 칼로리 진단
            if total_cal < 600:
                st.warning("⚠️ [칼로리 부족] 활기찬 학업을 위해 더 섭취가 필요합니다.")
            elif total_cal > 850:
                st.error("🚨 [칼로리 과다] 열량이 높습니다. 메뉴 배정을 조정해보세요.")
            else:
                st.success("✅ [칼로리 적절] 한 끼 권장 범위(600~800kcal)를 충족합니다.")

            # 나트륨 진단
            if total_sodium > 1000:
                st.warning("🧂 [나트륨 주의] 국물 섭취를 줄이거나 적절한 조리가 요구됩니다.")
            else:
                st.info("👍 [나트륨 적절] 염도가 적절하게 맞춰진 식단입니다.")

            st.divider()
            
            # 소감 및 메모 입력
            st.subheader("📝 데이터 분석 리포트 작성")
            note_input = st.text_area(
                "이 식단을 추천하는 이유와 데이터 분석 소감을 적어보세요:",
                value=st.session_state.chef_note,
                placeholder="예: 단백질 함량이 20g 이상으로 매우 훌륭하지만 나트륨 수치가 높아 국물을 줄이도록 제안합니다.",
                height=80
            )
            st.session_state.chef_note = note_input

            # PNG 결과 카드 다운로드
            if st.button("📸 급식 식단표 카드(PNG) 생성", type="primary", use_container_width=True):
                if not note_input.strip():
                    st.warning("분석 소감을 먼저 입력해 주세요!")
                else:
                    card_bytes = generate_menu_card(
                        st.session_state.my_menu,
                        total_cal,
                        total_protein,
                        total_sodium,
                        note_input
                    )
                    
                    st.download_button(
                        label="💾 PNG 식단표 다운로드",
                        data=card_bytes,
                        file_name="오늘의_급식_식단표.png",
                        mime="image/png",
                        use_container_width=True
                    )

# -----------------------------------------------------------------------------
# TAB 2: 새로운 메뉴 데이터 수집/등록 (학생 실습용)
# -----------------------------------------------------------------------------
with tabs[1]:
    st.subheader("📥 데이터 수집기: 신규 급식 메뉴 데이터 추가")
    st.write("학생들이 직접 메뉴와 영양 정보를 수집하여 데이터베이스에 추가해보는 실습 칸입니다.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        in_name = st.text_input("메뉴명 (문자/String)", value="마라탕")
        in_cat = st.selectbox("카테고리 (문자/String)", ["밥", "국", "메인반찬", "김치", "후식"])
        in_cal = st.number_input("칼로리 (정수/Integer)", min_value=0, value=450)
    with col_b:
        in_protein = st.number_input("단백질(g) (실수/Float)", min_value=0.0, value=15.5, step=0.1)
        in_sodium = st.number_input("나트륨(mg) (정수/Integer)", min_value=0, value=950)
        in_img = st.text_input("이미지 URL (문자/String)", value="https://via.placeholder.com/150")

    if st.button("➕ 메뉴 데이터베이스에 저장하기", use_container_width=True):
        new_row = pd.DataFrame([{
            '메뉴명': in_name,
            '카테고리': in_cat,
            '칼로리(kcal)': in_cal,
            '단백질(g)': in_protein,
            '나트륨(mg)': in_sodium,
            '이미지url': in_img
        }])
        st.session_state.menu_df = pd.concat([st.session_state.menu_df, new_row], ignore_index=True)
        st.success(f"✅ '{in_name}' 메뉴 데이터가 성공적으로 추가되었습니다! [급식 식단 짜기] 탭에서 확인하세요.")

# -----------------------------------------------------------------------------
# TAB 3: 데이터 유형(Type) 개념 학습 퀴즈
# -----------------------------------------------------------------------------
with tabs[2]:
    st.subheader("🔍 [2단원 개념] 컴퓨터에서의 데이터 표현과 유형")
    st.markdown("""
    우리가 사용한 급식 데이터는 컴퓨터 내부에서 다음과 같은 **데이터 유형(Data Type)**으로 분류되어 저장 및 연산됩니다.
    
    * **메뉴명, 카테고리:** `문자열(String)` ➔ 예: `"통밀밥"`, `"국"`
    * **칼로리, 나트륨:** `정수(Integer)` ➔ 소수점이 없는 숫자 데이터 예: `250`, `620`
    * **단백질:** `실수(Float)` ➔ 소수점이 포함된 정밀한 숫자 데이터 예: `25.0`, `4.5`
    * **식판 선택 여부:** `불리언(Boolean)` ➔ 참/거짓 데이터 예: `True`, `False`
    """)
    
    st.divider()
    st.dataframe(st.session_state.menu_df, use_container_width=True)
