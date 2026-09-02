import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PROJECT_DIR = ROOT / "ksitscma-sef"

ENTRYPOINTS = {
    "ui": "kiosk.py",
    "integrated": "ksnv.py",
    "face-demo": "deeptwocam.py",
    "prototype": "ks.py",
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kiosk DeepFace의 여러 실험 실행 파일 중 하나를 선택해 실행합니다."
    )
    parser.add_argument(
        "mode",
        choices=ENTRYPOINTS,
        nargs="?",
        default="ui",
        help="ui=기본 PyQt UI, integrated=통합 실험판, face-demo=얼굴/시선 실험, prototype=초기 프로토타입",
    )
    args = parser.parse_args()

    script = PROJECT_DIR / ENTRYPOINTS[args.mode]
    if not script.exists():
        raise FileNotFoundError(f"실행 파일을 찾을 수 없습니다: {script}")

    if args.mode in {"integrated", "face-demo"}:
        predictor = PROJECT_DIR / "shape_predictor_68_face_landmarks.dat"
        if not predictor.exists():
            raise FileNotFoundError(
                "68-point landmark 모델이 필요합니다. THIRD_PARTY_NOTICES.md의 이용 조건을 확인하세요."
            )

    result = subprocess.run([sys.executable, script.name], cwd=PROJECT_DIR)
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
