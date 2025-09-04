# 스마트공장 수준 진단 설문 애플리케이션 (SFMA Survey)

## 1. 프로젝트 개요

본 애플리케이션은 웹 기반 설문을 통해 스마트공장의 현재 수준을 진단하고, 그 결과를 차트와 표 형태로 시각화하여 제공하는 도구입니다. 사용자는 설문 답변을 통해 각 영역별 점수와 종합 수준(Level)을 확인할 수 있으며, 모든 결과는 파일로 저장하여 관리할 수 있습니다.

## 2. 주요 기능

- **동적 설문 생성**: `data/스마트팩토리수준진단_input.csv` 파일을 기반으로 설문 항목을 동적으로 생성합니다.
- **결과 분석 및 시각화**: 2가지 기준(수준, 점수)으로 결과를 분석하고, 요약 표와 막대 차트로 시각화하여 제공합니다.
- **상세 리포트**: 사용자가 선택한 모든 항목에 대한 상세 결과와 전문가의 종합 분석 요약을 함께 제공합니다.
- **데이터 저장**: 설문자 정보는 `설문자리스트.xlsx` 파일에, 개별 진단 결과는 `SFactory-XXXX.json` 형식의 파일로 자동 저장됩니다.
- **순차적 답변**: 사용자가 이전 문항에 답변해야만 다음 문항이 활성화되는 순차적 응답 방식을 적용했습니다.
- **실행 파일 지원**: PyInstaller를 통해 모든 기능이 포함된 단일 실행 파일(`SFMA_Survey.exe`) 생성을 지원합니다.

## 3. 사용 방법 (SFMA_Survey.exe 실행)

1. `dist` 폴더 안에 있는 `SFMA_Survey.exe` 파일을 더블 클릭하여 실행합니다.
2. 프로그램이 실행되면 자동으로 기본 웹 브라우저에 설문 페이지(`http://127.0.0.1:5000`)가 열립니다.
3. 성명, 회사명, 이메일을 입력하고 '설문 시작' 버튼을 누릅니다.
4. 순서에 따라 모든 문항에 답변합니다.
5. '결과보기' 버튼을 클릭하여 진단 결과를 확인합니다.

## 4. 개발 환경 설정 (개발자용)

- **요구사항**: Python 3.11 이상

1. **저장소 복제(Clone)**
   ```bash
   git clone <repository_url>
   cd SFMA_2
   ```

2. **가상 환경 생성 및 활성화**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **필요 라이브러리 설치**
   ```bash
   pip install -r requirements.txt
   ```

4. **개발 서버 실행**
   ```bash
   python app.py
   ```
   이후 웹 브라우저에서 `http://127.0.0.1:5000` 주소로 접속합니다.

## 5. 실행 파일 빌드 방법 (개발자용)

소스코드를 수정한 후 실행 파일을 다시 빌드하려면 아래 절차를 따릅니다.

1. **PyInstaller 설치**
   ```bash
   pip install pyinstaller
   ```

2. **빌드 명령어 실행**
   - **주의**: 빌드 전, 실행 중인 `SFMA_Survey.exe`가 있다면 반드시 종료해야 합니다.
   ```bash
   pyinstaller --onefile --name SFMA_Survey --add-data "data;data" --add-data "templates;templates" app.py
   ```

3. **결과 확인**: `dist` 폴더에 새로운 `SFMA_Survey.exe` 파일이 생성됩니다.

## 6. 프로젝트 구조

```
C:/Project/SFMA_2/
├── app.py                  # Flask 애플리케이션 메인 스크립트
├── data/                   # 입력 데이터 폴더
│   └── 스마트팩토리수준진단_input.csv
├── docs/                   # 프로젝트 문서 폴더
│   ├── PRD.md
│   └── 스마트공장수준진단결과.jpg
├── templates/              # HTML 템플릿 폴더
│   └── index.html
├── .gitignore              # Git 버전 관리 제외 목록
├── requirements.txt        # 필요 라이브러리 목록
├── README.md               # 프로젝트 소개 및 안내 문서
├── build/                  # PyInstaller 빌드 과정 파일
├── dist/                   # 최종 실행 파일(.exe) 폴더
└── ... (실행 시 생성되는 결과 파일들)
```
