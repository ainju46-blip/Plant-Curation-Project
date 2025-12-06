import streamlit as st
import json

# ====================================================
# 1. 매핑 딕셔너리 정의 (코드 <-> 문장 변환용)
# ====================================================

DIFFICULTY_MAP = {
    '매우 귀찮음 (물 주기를 자주 잊어요) 😴': '하',
    '보통 (주 1~2회 정도는 봐줄 수 있어요) 🪴': '중',
    '열정적 (매일 상태를 확인하고 싶어요) ✨': '상'
}

LIGHT_MAP = {
    '빛이 하루 종일 잘 드는 창가 ☀️': '밝음',
    '간접광이 들어오는 실내 중간 🌥️': '중간',
    '어둡거나 빛이 거의 없는 곳 🌑': '낮음'
}

SIZE_MAP = {
    '15cm 이하 (책상 위, 작은 선반용) 🤏': '소',
    '15cm 초과 ~ 30cm 이하 (중형 스탠드) 📏': '중',
    '30cm 초과 (바닥 배치, 코너 공간) 🌳': '대'
}

AIR_MAP = {
    '공기 정화 능력이 높음': '높음', 
    '일반적인 공기 정화 수준': '보통', 
    '기능보다 관상 목적': '낮음'
}

PET_MAP = {
    '반려동물/아이에게 안전함 ✅': '안전', 
    '섭취 시 주의 필요 ⚠️': '주의'
}

GROWTH_MAP = {
    '성장이 매우 느려 분갈이가 거의 필요 없음 🐌': '느림',
    '보통 속도로 관리하기 적당함 🌳': '보통',
    '성장이 빨라 자주 가지치기/분갈이가 필요함 🌱': '빠름'
}

# 총 6개의 조건 딕셔너리와 JSON 키 정의
ALL_MAPS = [DIFFICULTY_MAP, LIGHT_MAP, SIZE_MAP, AIR_MAP, PET_MAP, GROWTH_MAP]
JSON_KEYS = ['difficulty', 'light_level', 'size', 'air_purifying', 'pet_safe', 'growth_speed'] 
NUM_CONDITIONS = len(JSON_KEYS)

# ====================================================
# 2. 데이터 로드 및 UI 설정
# ====================================================

@st.cache_data
def load_data(file_path):
    """JSON 파일을 로드하고 파일 없을 시 에러 메시지를 출력합니다."""
    try:
        # 파일 이름을 소문자로 강제하여 대소문자 오류를 방지합니다.
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        # FileNotFoundError 처리 시, 파일 경로를 변수로 받아 출력합니다.
        st.error("오류: {0} 파일을 찾을 수 없습니다. JSON 파일 이름(plants_data.json)을 확인해주세요.".format(file_path))
        return []

PLANT_DATA = load_data('plants_data.json') # 파일 이름은 소문자로 지정합니다.

st.title("🌿 성향 맞춤 실내 식물 큐레이션")
st.markdown("당신의 관리 성향, 환경, 목적에 가장 적합한 식물을 찾아드립니다.")
st.markdown("---") # UI 디자인 구분선

default_options = ['-- 선택 --']
all_inputs = []

# 컬럼 3개로 나누어 질문 배치
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("✅ 관리 성향/환경")
    all_inputs.append(st.selectbox("Q1. 관리 난이도", default_options + list(DIFFICULTY_MAP.keys())))
    all_inputs.append(st.selectbox("Q2. 햇빛 량", default_options + list(LIGHT_MAP.keys())))

with col2:
    st.subheader("💡 추가 조건")
    all_inputs.append(st.selectbox("Q3. 식물 크기", default_options + list(SIZE_MAP.keys())))
    all_inputs.append(st.selectbox("Q4. 공기정화 능력", default_options + list(AIR_MAP.keys())))

with col3:
    st.subheader("⚠️ 생활 환경")
    all_inputs.append(st.selectbox("Q5. 반려동물/아이 안전", default_options + list(PET_MAP.keys()))) 
    all_inputs.append(st.selectbox("Q6. 생장 속도", default_options + list(GROWTH_MAP.keys())))   


# ====================================================
# 3. 6가지 조건 필터링 로직 및 결과 출력
# ====================================================

# 모든 질문이 선택되었는지 확인
all_selected = all(val != '-- 선택 --' for val in all_inputs)

if PLANT_DATA and all_selected:
    
    # 3-1. 긴 문장 선택지를 짧은 코드로 변환 (매핑)
    filtered_values = []
    for i, selected_text in enumerate(all_inputs):
        # ALL_MAPS[i].get(selected_text)를 사용하여 짧은 코드를 추출합니다.
        filtered_values.append(ALL_MAPS[i].get(selected_text))

    recommended_plants = []

    # 3-2. 6가지 조건 필터링 실행
    for plant in PLANT_DATA:
        match_count = 0
        
        # 6개의 JSON_KEYS와 필터링 값 6개를 비교
        for i, key in enumerate(JSON_KEYS):
            if plant.get(key) == filtered_values[i]:
                match_count += 1
        
        # 6개의 조건이 모두 일치해야만 추천
        if match_count == NUM_CONDITIONS:
            recommended_plants.append(plant)

    # ⭐ 추천 식물을 최대 3개로 제한합니다.
    final_recommendations = recommended_plants[:3] 
    
    # 3-3. 결과 출력
    st.header("✅ 추천 결과")
    
    if len(final_recommendations) > 0:
        # .format() 사용
        st.success("🎊 조건에 맞는 식물 중 상위 {0}개를 추천합니다! (최대 3개)".format(len(final_recommendations)))
        
        for i, plant in enumerate(final_recommendations):
            # .format() 사용
            st.subheader("{0}. {1}".format(i + 1, plant['korean_name']))
            st.info("🌿 난이도: {0} | ☀️ 빛: {1} | 📏 크기: {2}".format(
                plant['difficulty'], plant['light_level'], plant['size']))
            st.info("💨 공기정화: {0} | 🐶 안전성: {1} | 📈 생장 속도: {2}".format(
                plant['air_purifying'], plant['pet_safe'], plant['growth_speed']))
            
            # 일반 팁과 변색 시 대처 팁을 구분하여 출력합니다.
            st.warning("💡 일반 관리 팁: {0}".format(plant.get('management_tip', '팁 정보 없음')))
            # .format() 사용
            st.error("⚠️ 잎 변색 시 대처법: {0}".format(plant.get('discoloration_tip', '대처 팁 정보 없음'))) 
            st.markdown("---")
            
    else:
        st.error("😭 {0}가지 조건에 모두 맞는 식물은 찾지 못했어요. 조건을 완화해보세요!".format(NUM_CONDITIONS))
        
elif not all_selected:
    st.info("모든 질문에 답변을 선택해주세요.")
