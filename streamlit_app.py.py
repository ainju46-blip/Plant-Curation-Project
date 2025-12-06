import streamlit as st
import json
import os # <-- os 모듈 추가

# ====================================================
# 1. 매핑 딕셔너리 정의 (문장 <-> 코드 변환용)
# ... (이 부분은 이전과 동일)
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

ALL_MAPS = [DIFFICULTY_MAP, LIGHT_MAP, SIZE_MAP, AIR_MAP, PET_MAP, GROWTH_MAP]
JSON_KEYS = ['difficulty', 'light_level', 'size', 'air_purifying', 'pet_safe', 'growth_speed'] 
NUM_CONDITIONS = len(JSON_KEYS)

# ====================================================
# 2. 데이터 로드 (경로 수정 포함)
# ====================================================

@st.cache_data
def load_data(file_name):
    """JSON 파일을 로드하고 파일 경로 문제를 해결합니다."""
    try:
        # os.path.dirname(__file__)는 현재 스크립트 파일의 디렉토리를 반환합니다.
        # os.path.join은 해당 디렉토리와 파일 이름을 합쳐 정확한 경로를 만듭니다.
        base_dir = os.path.dirname(__file__)
        file_path = os.path.join(base_dir, file_name) 
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("오류: 데이터 파일을 찾을 수 없습니다. 경로: {0}".format(file_path))
        return []

PLANT_DATA = load_data('plants_data.json') # 파일 이름은 소문자로 유지

# ... (나머지 UI 및 로직 코드는 이전과 동일)

# --------------------------------------------------------------------------------------
# (3. UI 설정, 4. 필터링 로직 및 결과 출력 코드는 이전 최종 버전과 동일합니다.)
# --------------------------------------------------------------------------------------

st.title("🌿 성향 맞춤 실내 식물 큐레이션")
st.markdown("당신의 관리 성향, 환경, 목적에 가장 적합한 식물을 찾아드립니다.")
st.markdown("---")

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

st.markdown("---")

# 4. 필터링 로직 및 결과 출력
all_selected = all(val != '-- 선택 --' for val in all_inputs)

if PLANT_DATA and all_selected:
    
    # 4-1. 긴 문장 선택지를 짧은 코드로 변환 (매핑)
    filtered_values = []
    for i, selected_text in enumerate(all_inputs):
        filtered_values.append(ALL_MAPS[i].get(selected_text))

    recommended_plants = []

    # 4-2. 6가지 조건 필터링 실행
    for plant in PLANT_DATA:
        match_count = 0
        
        for i, key in enumerate(JSON_KEYS):
            if plant.get(key) == filtered_values[i]:
                match_count += 1
        
        if match_count == NUM_CONDITIONS:
            recommended_plants.append(plant)

    # 추천 식물을 최대 3개로 제한합니다.
    final_recommendations = recommended_plants[:3] 
    
    # 4-3. 결과 출력
    st.header("✅ 추천 결과")
    
    if len(final_recommendations) > 0:
        st.success("🎊 조건에 맞는 식물 중 상위 {0}개를 추천합니다! (최대 3개)".format(len(final_recommendations)))
        
        for i, plant in enumerate(final_recommendations):
            st.subheader("{0}. {1}".format(i + 1, plant['korean_name']))
            st.info("🌿 난이도: {0} | ☀️ 빛: {1} | 📏 크기: {2}".format(
                plant['difficulty'], plant['light_level'], plant['size']))
            st.info("💨 공기정화: {0} | 🐶 안전성: {1} | 📈 생장 속도: {2}".format(
                plant['air_purifying'], plant['pet_safe'], plant['growth_speed']))
            
            st.warning("💡 일반 관리 팁: {0}".format(plant.get('management_tip', '팁 정보 없음')))
            st.error("⚠️ 잎 변색 시 대처법: {0}".format(plant.get('discoloration_tip', '대처 팁 정보 없음'))) 
            st.markdown("---")
            
    else:
        st.error("😭 {0}가지 조건에 모두 맞는 식물은 찾지 못했어요. 조건을 완화해보세요!".format(NUM_CONDITIONS))
        
elif not all_selected:
    st.info("모든 질문에 답변을 선택해주세요.")

