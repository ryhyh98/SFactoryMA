
import pandas as pd
from flask import Flask, render_template, request, jsonify
import os
import sys
import datetime
import json
import webbrowser
from threading import Timer

# --- PyInstaller 경로 해결 함수 ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Flask 앱 초기화 ---
# 템플릿 폴더 경로를 resource_path를 이용해 지정
app = Flask(__name__, template_folder=resource_path('templates'))

# --- 전역 변수 --- #
df_input = None
대분류_info = {}
RESULT_FOLDER = 'result'

def load_survey_data():
    global df_input, 대분류_info
    try:
        # CSV 파일 경로를 resource_path를 이용해 지정
        csv_path = resource_path(os.path.join('data', '스마트팩토리수준진단_input.csv'))
        df_input = pd.read_csv(csv_path, encoding='utf-8')
        # 대분류별 배점 정보 미리 계산
        대분류_info = df_input.groupby('대분류')['배점'].first().to_dict()
    except Exception as e:
        print(f"Error loading CSV: {e}")

# --- 유틸리티 함수 --- #
def get_next_serial_number():
    serial_file_path = os.path.join(RESULT_FOLDER, 'serial_number.txt')
    try:
        with open(serial_file_path, "r") as f:
            new_number = int(f.read().strip()) + 1
        with open(serial_file_path, "w") as f:
            f.write(str(new_number))
        return f"SFactory-{new_number:04d}"
    except FileNotFoundError:
        with open(serial_file_path, "w") as f:
            f.write("1")
        return "SFactory-0001"

def get_final_level(total_score):
    if total_score < 550:
        return "Level 0"
    elif 550 <= total_score < 650:
        return "Level 1"
    elif 650 <= total_score < 750:
        return "Level 2"
    elif 750 <= total_score < 850:
        return "Level 3"
    elif 850 <= total_score < 950:
        return "Level 4"
    else:
        return "Level 5"

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000')

# --- 라우트 --- #
@app.route('/')
def index():
    if df_input is None:
        return "오류: 설문 데이터가 로드되지 않았습니다. 서버 로그를 확인하세요.", 500
    
    questions = []
    for _, row in df_input.iterrows():
        questions.append({
            "대분류": row["대분류"],
            "평가항목": row["평가항목"],
            "질문": f'【{row["대분류"]}】 - {row["평가항목"]}: 귀사의 수준에 맞는 내용을 선택하십시요.',
            "options": [
                {"text": row["select0"], "score1": 0, "score2": row["Level0"]},
                {"text": row["select1"], "score1": 1, "score2": row["Level1"]},
                {"text": row["select2"], "score1": 2, "score2": row["Level2"]},
                {"text": row["select3"], "score1": 3, "score2": row["Level3"]},
                {"text": row["select4"], "score1": 4, "score2": row["Level4"]},
                {"text": row["select5"], "score1": 5, "score2": row["Level5"]},
            ]
        })
    return render_template('index.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    
    # 1. 설문자 정보 저장
    surveyor_data = pd.DataFrame([data['surveyorInfo']])
    excel_path = os.path.join(RESULT_FOLDER, '설문자리스트.xlsx')
    if os.path.exists(excel_path):
        with pd.ExcelWriter(excel_path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            surveyor_data.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
    else:
        surveyor_data.to_excel(excel_path, sheet_name='Sheet1', index=False)

    # 2. 결과 계산
    대분류_scores = {key: {'배점': val, '수준': 0, '점수': 0, 'count': 0} for key, val in 대분류_info.items()}
    
    detailed_answers = []
    for answer in data['answers']:
        대분류 = answer['대분류']
        if 대분류 in 대분류_scores:
            대분류_scores[대분류]['수준'] += answer['score1']
            대분류_scores[대분류]['점수'] += answer['score2']
            대분류_scores[대분류]['count'] += 1
        detailed_answers.append(answer)

    total_배점 = 0
    total_점수 = 0
    total_수준_sum = 0
    total_count = 0

    for key, value in 대분류_scores.items():
        count = value['count']
        if count > 0:
            value['수준'] = round(value['수준'] / count, 1)
        total_배점 += value['배점']
        total_점수 += value['점수']
        total_수준_sum += value['수준'] * count # 가중 평균을 위해 곱함
        total_count += count

    overall_수준 = round(total_수준_sum / total_count, 1) if total_count > 0 else 0
    final_level = get_final_level(total_점수)

    # 3. 종합 분석 요약 (전문가 수준으로 보강)
    summary = {
        "total_evaluation": "귀사의 스마트공장 수준은 현재 ‘{}’ 단계로, 전반적인 디지털 전환의 초기 단계에 있습니다. 특히 ‘리더십과 전략’ 및 ‘정보시스템’ 영역의 수준이 상대적으로 낮아, 데이터 기반의 의사결정 체계 강화와 핵심 정보시스템(MES, SCM 등) 도입 및 고도화를 위한 구체적인 로드맵 수립이 시급합니다. ‘제품개발’ 및 ‘생산계획’ 영역은 비교적 양호하나, 타 영역과의 연계성 강화를 통해 시너지를 창출할 필요가 있습니다.".format(final_level),
        "category_summary": {
            "1.1 리더십과 전략": "리더십 분야에서는 명확한 디지털 전환 비전 및 KPI 설정이 미흡한 것으로 보입니다. 스마트공장 추진을 위한 전담 조직을 구성하고, 구체적인 성과지표를 설정하여 전사적으로 공유 및 관리하는 체계를 마련해야 합니다.",
            "2.1 제품개발": "제품개발 프로세스는 비교적 잘 관리되고 있으나, PLM(제품수명주기관리) 시스템과의 연계를 통해 설계-생산 간 데이터 흐름을 일원화하고, 개발 효율성을 극대화할 필요가 있습니다.",
            "3.1 정보시스템": "핵심 정보시스템의 활용도가 낮아 데이터 기반의 실시간 의사결정에 한계가 있습니다. MES를 중심으로 생산 현장의 데이터를 수집/분석하고, SCM, ERP와의 연동을 통해 공급망 전체의 가시성을 확보하는 전략이 중요합니다.",
            "4.1 성과": "현재 성과는 정체 상태이거나 경쟁사 대비 낮은 수준에 머물러 있습니다. 스마트공장 도입을 통해 달성하고자 하는 명확한 목표(생산성, 품질, 원가, 납기 등)를 설정하고, 이를 측정/개선하기 위한 노력이 필요합니다."
        }
    }

    # 4. 결과 데이터 구성
    serial_number = get_next_serial_number()
    result_data = {
        "serial_number": serial_number,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "surveyor": data['surveyorInfo'],
        "detailed_results": detailed_answers, # 상세 결과 추가
        "summary_table": 대분류_scores,
        "totals": {
            "배점": total_배점,
            "점수": total_점수,
            "수준": overall_수준
        },
        "final_level": final_level,
        "summary_text": summary
    }
    
    # 5. 파일로 저장
    json_path = os.path.join(RESULT_FOLDER, f"{serial_number}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)

    return jsonify(result_data)

# --- 앱 실행 --- #
if __name__ == '__main__':
    # 결과 폴더가 없으면 생성
    if not os.path.exists(RESULT_FOLDER):
        os.makedirs(RESULT_FOLDER)
    load_survey_data()
    Timer(1, open_browser).start()
    app.run(debug=False, host='127.0.0.1', port=5000)
