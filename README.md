# Kiosk DeepFace

카페형 키오스크 UI에 **DeepFace/dlib 기반 얼굴 분석, 시선 움직임 추적, 음성 인식 기능을 결합해 실험한 키오스크 프로젝트**입니다.

저장소에는 하나의 완성 실행파일만 있는 것이 아니라, 키오스크 UI와 얼굴·시선 분석 기능을 결합하는 과정에서 만들어진 여러 버전의 코드와 데이터·UI·이미지 리소스가 함께 들어 있습니다.

## 주요 기능

- 카페 메뉴 선택 및 장바구니
- 메뉴 옵션 선택
- 매장 / 포장 선택
- 결제 화면 및 QR/바코드 형태의 결제 흐름
- 포인트·영수증·관리자 화면
- SQLite 기반 주문 데이터 처리
- OpenCV + dlib 얼굴 검출
- DeepFace 기반 나이·감정 추정
- 68-point facial landmark 기반 눈 위치 추적
- 일정 시간 동안 눈의 이동 경로를 기록하여 F/Z 형태의 이동 패턴을 판정하는 실험 코드
- SpeechRecognition 기반 음성 입력 실험
- pyttsx3 음성 출력 관련 코드

## 저장소 구조

실제 프로그램 파일은 `ksitscma-sef/` 디렉터리에 있습니다.

```text
kiosk_deepface/
└── ksitscma-sef/
    ├── ksnv.py
    ├── contect.py
    ├── deeptwocam.py
    ├── kiosk.py
    ├── ks.py
    ├── shopping_cart.py
    ├── sub_kiosk.py
    ├── sub_kiosk_1.py
    ├── shape_predictor_68_face_landmarks.dat
    ├── dlib-19.22.99-cp38-cp38-win_amd64.whl
    ├── ui/
    ├── data/
    ├── img/
    ├── menu/
    └── background/
```

## 주요 Python 파일

| 파일 | 역할 |
|---|---|
| `ksnv.py` | 키오스크 UI, 주문·결제·관리 기능과 얼굴/시선 분석 기능이 함께 들어 있는 가장 큰 통합 버전 |
| `contect.py` | Tkinter/PyQt 관련 코드와 메뉴·카트·얼굴 분석 기능이 함께 누적된 통합 실험 버전 |
| `deeptwocam.py` | 카메라 2대를 이용한 얼굴 분석 + 눈 위치/이동 패턴 추적 전용 코드 |
| `kiosk.py` | `QT_design.ui`를 불러와 페이지를 전환하는 초기 PyQt 키오스크 UI |
| `ks.py` | 간단한 메뉴 UI + DeepFace 얼굴 분석 + 음성 인식을 결합한 프로토타입 |
| `shopping_cart.py` | 장바구니 수량 변경, 삭제, 가격 계산 및 SQLite 주문 데이터 처리 |
| `sub_kiosk.py`, `sub_kiosk_1.py` | 키오스크 기능의 이전/분리 버전 |

## 데이터와 UI

`data/`에는 메뉴·가격·품절·결제 관련 CSV와 SQLite 데이터베이스가 포함되어 있습니다.

```text
data.db
drinks_menu.csv
drinks_menu_2.csv
drinks_price.csv
drinks_img_path.csv
drinks_sold_out.csv
order_table.csv
payment_choose.csv
```

`ui/`에는 Qt Designer로 작성된 UI 파일이 들어 있습니다.

```text
mega_ui_ver3.ui
mega_choose_option_page.ui
mega_payment_choose.ui
manager_page.ui
msg_box.ui
point_page.ui
receipt_page_2.ui
```

`img/`, `menu/`, `background/`에는 키오스크 화면에 사용하는 광고·메뉴·결제·버튼 이미지가 들어 있습니다.

## 권장 환경

현재 저장소는 코드의 경로 표기와 포함된 dlib wheel을 기준으로 보면 **Windows 환경을 중심으로 작성된 프로젝트**입니다.

저장소에 포함된 dlib wheel:

```text
dlib-19.22.99-cp38-cp38-win_amd64.whl
```

이 파일은 64비트 Windows용 CPython 3.8 wheel입니다. 다른 Python 버전을 사용할 경우 해당 Python 버전에 맞는 dlib 설치가 별도로 필요합니다.

## 다운로드

```bash
git clone https://github.com/AIN108/kiosk_deepface.git
cd kiosk_deepface/ksitscma-sef
```

## Python 패키지

코드 전체에서 사용되는 주요 패키지는 다음과 같습니다.

```bash
pip install opencv-python deepface PyQt5 pandas pyttsx3 SpeechRecognition Pillow
```

Python 3.8 64비트 Windows에서 저장소에 포함된 dlib wheel을 사용할 경우:

```bash
pip install dlib-19.22.99-cp38-cp38-win_amd64.whl
```

음성 입력 기능을 사용할 경우 `SpeechRecognition`이 마이크에 접근할 수 있도록 PyAudio 등 오디오 입력 백엔드가 추가로 필요할 수 있습니다.

## 실행

### 통합 키오스크 코드

```bash
python ksnv.py
```

`ksnv.py`는 메뉴, 장바구니, 주문, 결제, 관리자 기능과 카메라 분석 코드가 함께 들어 있는 통합 버전입니다.

### 두 카메라 얼굴·시선 분석

```bash
python deeptwocam.py
```

현재 활성 실행부에서는 다음과 같이 카메라를 나눠 사용합니다.

```text
Camera 0 → 얼굴 검출 + DeepFace 나이/감정 추정
Camera 1 → dlib 68-point landmark 기반 눈 위치 추적
```

따라서 이 기능을 그대로 실행하려면 일반적으로 카메라 2대가 필요합니다.

### 초기 PyQt 키오스크

```bash
python kiosk.py
```

이 파일은 `QT_design.ui`를 불러와 `stackedWidget` 페이지를 전환하는 초기 UI 버전입니다.

## 얼굴 분석 구조

`deeptwocam.py`와 통합 코드 일부에서는 다음 처리 구조를 사용합니다.

```text
Webcam
  ↓
dlib 얼굴 검출
  ↓
DeepFace.analyze()
  ↓
나이 / dominant emotion 추정
```

별도의 카메라에서는 `shape_predictor_68_face_landmarks.dat`를 이용하여 얼굴 랜드마크 36~47번의 눈 주변 좌표를 추적합니다.

```text
Camera 1
   ↓
dlib facial landmarks
   ↓
왼쪽/오른쪽 눈 중심 좌표
   ↓
일정 시간 이동 경로 기록
   ↓
F / Z 형태 이동 패턴 판정 실험
```

`shape_predictor_68_face_landmarks.dat` 파일은 현재 저장소에 포함되어 있습니다.

## 경로 관련 주의사항

오래된 코드가 여러 시기에 작성되어 일부 파일에는 작성 당시 PC의 절대경로가 남아 있습니다.

예:

```text
C:\ksitscma-sef\ksitscma-sef\QT_design.ui
C:/ksitscma-sef/ksitscma-sef/background/
```

또한 일부 코드에서는 다음처럼 대문자 디렉터리를 참조합니다.

```text
./UI/
./DATA/
```

현재 저장소의 실제 디렉터리는 `ui/`, `data/` 형태입니다. Windows에서는 대소문자 차이가 문제되지 않는 경우가 많지만 Linux 등 대소문자를 구분하는 파일시스템에서는 경로를 수정해야 합니다.

따라서 다른 PC에서 실행할 경우 각 실행 파일의 경로 설정을 먼저 확인하는 것이 좋습니다.

## DeepFace 및 판정 로직 관련 주의

프로젝트 안에는 DeepFace가 추정한 나이·감정 값과 시선 이동 패턴을 이용하여 사용자의 상태를 분류하려는 실험 로직이 포함되어 있습니다.

이 값들은 카메라 영상에서 모델이 추정한 결과이며 실제 나이, 감정, 디지털 기기 사용 능력을 확정하는 측정값이 아닙니다. 특히 코드에 남아 있는 `디지털 문맹자` 판정 로직은 실험 당시 사용한 휴리스틱으로, 사람의 실제 디지털 활용 능력을 신뢰성 있게 판정하는 방법으로 사용해서는 안 됩니다.

실제 서비스에 적용할 경우 해당 판정 로직을 별도의 검증 없이 사용자 분류나 중요한 의사결정에 사용하지 않는 것이 적절합니다.

## 카메라 및 개인정보

이 프로젝트는 얼굴 영상과 음성 입력을 처리할 수 있습니다. 실제 운용 시에는 촬영·녹음 사실을 사용자에게 알리고, 영상이나 분석 결과를 저장·전송하는 기능을 추가하는 경우 개인정보 및 관련 이용 조건을 별도로 검토해야 합니다.

## 현재 코드 상태

이 저장소는 여러 버전의 키오스크 및 분석 코드를 한곳에 보존한 프로젝트입니다. 따라서 모든 Python 파일이 하나의 동일한 실행 흐름을 구성하는 것은 아니며, 파일마다 사용 UI·데이터 경로·카메라 구성과 의존성이 다릅니다.

새 환경에서 다시 운영하려면 `ksnv.py` 또는 필요한 기능별 파일을 기준으로 경로와 의존성을 정리한 뒤 사용하는 것이 좋습니다.

## 라이선스

현재 저장소에는 별도의 `LICENSE` 파일이 없습니다. 재배포 또는 다른 프로젝트에 포함하여 사용할 경우 저장소 소유자에게 이용 조건을 확인하세요.
