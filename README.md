# Kiosk DeepFace

카페형 키오스크 UI에 **DeepFace/dlib 얼굴 분석, 시선 이동 추적, 음성 입출력 기능을 결합해 실험한 복합 프로토타입**입니다.

이 저장소는 하나의 완성 제품이라기보다, 키오스크 UI와 얼굴·시선 분석을 여러 단계에서 결합했던 **연구/프로젝트 당시 코드와 자산을 보존하면서 실행 경로를 정리한 저장소**입니다.

## 현재 권장 진입점

루트의 `run_project.py`에서 실행할 실험판을 선택할 수 있습니다.

```bash
python run_project.py ui
python run_project.py integrated
python run_project.py face-demo
python run_project.py prototype
```

| 모드 | 실행 파일 | 성격 |
|---|---|---|
| `ui` | `ksitscma-sef/kiosk.py` | 기본 PyQt 페이지 전환 UI |
| `integrated` | `ksitscma-sef/ksnv.py` | 주문/결제/관리 + 얼굴/시선/음성 기능이 누적된 통합 실험판 |
| `face-demo` | `ksitscma-sef/deeptwocam.py` | 카메라 기반 얼굴 분석과 시선 이동 실험 |
| `prototype` | `ksitscma-sef/ks.py` | 초기 키오스크 + DeepFace/음성 프로토타입 |

`ui` 모드는 과거의 PC 절대경로를 제거해 저장소 내부 `QT_design.ui`를 직접 찾도록 정리했습니다.

## 프로젝트 구조

```text
kiosk_deepface/
├── README.md
├── THIRD_PARTY_NOTICES.md
├── requirements.txt
├── run_project.py
└── ksitscma-sef/
    ├── kiosk.py
    ├── ksnv.py
    ├── deeptwocam.py
    ├── ks.py
    ├── contect.py
    ├── shopping_cart.py
    ├── sub_kiosk.py
    ├── sub_kiosk_1.py
    ├── QT_design.ui
    ├── shape_predictor_68_face_landmarks.dat
    ├── dlib-19.22.99-cp38-cp38-win_amd64.whl
    ├── ui/
    ├── data/
    ├── img/
    ├── menu/
    └── background/
```

## 주요 기능

- 카페 메뉴 선택, 옵션, 장바구니
- 매장/포장 및 결제 화면 흐름
- SQLite 기반 주문 데이터 처리
- OpenCV + dlib 얼굴 검출
- DeepFace 기반 나이/감정 추정 실험
- 68-point facial landmark 기반 눈 위치 추적
- 일정 시간 동안 시선 이동 경로를 기록해 F/Z 형태를 판정하는 실험
- SpeechRecognition 기반 음성 입력
- pyttsx3 기반 음성 출력

## 설치

이 프로젝트는 Windows + Python 3.8 계열에서 개발된 흔적이 강합니다. 새 환경에서는 가상환경 사용을 권장합니다.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`dlib`은 플랫폼과 Python 버전에 따라 설치 방식이 크게 달라지므로 `requirements.txt`에서 자동 설치하지 않습니다.

저장소에는 과거 Windows CPython 3.8용으로 사용했던 다음 wheel이 보존되어 있습니다.

```text
ksitscma-sef/dlib-19.22.99-cp38-cp38-win_amd64.whl
```

이 바이너리의 출처/재배포와 dlib 모델의 이용 조건은 [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md)를 먼저 확인하세요.

## 데이터와 UI

`data/`에는 메뉴·가격·품절·결제 관련 CSV 및 SQLite 데이터가 있고, `ui/`에는 Qt Designer UI 파일이 있습니다.

`img/`, `menu/`, `background/`에는 키오스크 화면에서 사용한 메뉴·광고·결제·브랜드 관련 이미지가 포함되어 있습니다.

이러한 자산은 모두 AIN108이 원저작권을 가진다고 볼 수 없으므로 소스 코드와 동일한 라이선스로 취급하지 않습니다.

## Legacy 코드에 대한 주의

`ksnv.py`, `contect.py`, `sub_kiosk.py`, `sub_kiosk_1.py` 등은 프로젝트 진행 과정에서 기능을 누적하며 만든 대형 실험 코드입니다.

일부 파일에는 다음과 같은 과거 환경 의존성이 남아 있을 수 있습니다.

- `UI/`와 `ui/`, `DATA/`와 `data/`처럼 Windows에서는 동작하지만 Linux에서는 문제가 될 수 있는 대소문자 차이
- 특정 카메라 번호를 전제로 한 코드
- 당시 파일 배치에 맞춘 상대경로
- 여러 세대의 UI와 데이터 포맷

따라서 이 저장소는 과거 실험을 삭제해 새 프로젝트처럼 꾸미기보다, **대표 실행 경로를 명확히 하고 legacy 코드의 맥락을 보존하는 방향**으로 관리합니다.

## 얼굴 분석 결과 해석 주의

DeepFace의 나이·감정 추정이나 시선 이동 휴리스틱은 실제 사람의 나이, 감정, 디지털 활용 능력을 확정적으로 측정하는 기능이 아닙니다.

프로젝트 당시의 실험적 분류 로직을 실제 사용자 평가나 중요한 의사결정에 그대로 사용해서는 안 됩니다.

## 카메라와 개인정보

이 프로젝트는 얼굴 영상과 음성 입력을 처리할 수 있습니다. 실제 환경에서 사용할 경우 촬영·녹음 사실 고지, 저장 여부, 분석 결과의 보관 및 전송 범위를 별도로 검토해야 합니다.

## 제3자 구성요소와 라이선스

저장소 전체에 하나의 오픈소스 라이선스를 일괄 적용하지 않습니다.

특히 다음 항목은 별도 권리가 적용됩니다.

- dlib 및 플랫폼별 바이너리
- `shape_predictor_68_face_landmarks.dat`
- DeepFace/OpenCV/PyQt 등 외부 라이브러리
- 메뉴·브랜드·광고·결제 관련 이미지 자산

자세한 내용은 [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md)를 참고하세요.
