# Third-Party Notices

이 저장소에는 AIN108이 작성·수정한 실험 코드 외에도 외부 라이브러리, 학습된 모델, 브랜드/메뉴/결제 관련 이미지 자산이 포함되어 있습니다. 이 파일은 저장소 전체에 단일 오픈소스 라이선스를 적용하는 것으로 오해하지 않도록 주요 외부 구성요소와 이용 조건을 구분해 기록합니다.

## dlib

- Project: dlib
- Upstream: https://github.com/davisking/dlib
- License: Boost Software License 1.0

저장소에 포함된 `dlib-19.22.99-cp38-cp38-win_amd64.whl`은 dlib 실행 바이너리 패키지입니다. dlib 자체의 이용 조건은 원 프로젝트의 Boost Software License를 따릅니다. 재배포 시에는 원본 프로젝트와 해당 배포물의 출처/빌드 경로를 별도로 확인하는 것이 권장됩니다.

## shape_predictor_68_face_landmarks.dat

- Upstream models repository: https://github.com/davisking/dlib-models
- File: `shape_predictor_68_face_landmarks.dat`
- Training data noted by dlib: iBUG 300-W dataset

dlib 공식 모델 저장소는 이 68-point 모델이 iBUG 300-W 데이터셋으로 학습되었으며, 해당 데이터셋의 라이선스가 상업적 사용을 배제한다고 명시하고 있습니다. 따라서 이 모델 파일을 상업 제품에 사용하는 것은 적절하지 않습니다. 정확한 이용 조건이 필요한 경우 dlib 모델 저장소와 iBUG 300-W 데이터셋의 최신 라이선스를 직접 확인하십시오.

이 파일이 저장소에 포함되어 있다는 사실이 AIN108이 해당 모델 자체의 저작권이나 상업적 재배포 권한을 보유한다는 뜻은 아닙니다.

## DeepFace 및 Python 의존성

DeepFace, OpenCV, PyQt, SpeechRecognition, pyttsx3, Pillow, pandas 등 외부 패키지는 각각의 프로젝트 라이선스를 따릅니다. 이 저장소의 코드 이용 조건과 별개입니다.

## 이미지·브랜드·메뉴 자산

`ksitscma-sef/img/`, `ksitscma-sef/menu/`, `ksitscma-sef/background/` 등에는 카페 메뉴 이미지, 브랜드 로고, 결제 서비스 로고, 광고/인물 이미지 등 제3자 권리가 적용될 수 있는 자산이 포함되어 있습니다.

이러한 이미지·로고·상표는 이 저장소의 소스 코드 라이선스 대상으로 간주하지 않으며, 별도의 사용 허가가 확인되지 않은 자산은 재사용·재배포·상업적 이용 전에 권리 관계를 확인해야 합니다.

## 저장소 이용 시 주의

현재 저장소는 연구·프로토타이핑 당시의 실행 환경을 보존한 성격이 강합니다. 제3자 자산을 제거하거나 출처별 다운로드 절차로 전환하기 전까지는 저장소 전체를 MIT, Apache-2.0 등 하나의 라이선스로 일괄 재배포 가능한 패키지로 취급하지 마십시오.
