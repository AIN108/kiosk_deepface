'''
import cv2
import dlib
from deepface import DeepFace

# dlib 얼굴 검출기 초기화
detector = dlib.get_frontal_face_detector()

camera_ids = [0, 1]  # 사용할 카메라 ID
cameras = [cv2.VideoCapture(id) for id in camera_ids]

try:
    while True:
        for index, cam in enumerate(cameras):
            ret, frame = cam.read()
            if not ret:
                print(f"카메라 {index} 캡처 실패")
                continue

            # dlib을 사용하여 얼굴 검출
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                x, y, w, h = face.left(), face.top(), face.width(), face.height()

                # 얼굴 부분 잘라내기
                face_image = frame[y:y + h, x:x + w]

                try:
                    # DeepFace를 사용하여 나이와 감정 분석
                    # enforce_detection=False 설정
                    result = DeepFace.analyze(face_image, actions=['age', 'emotion'], enforce_detection=False)

                    if type(result) == list and len(result) > 0:
                        result = result[0]  # 첫 번째 결과 사용

                    age = result.get('age', 'N/A')
                    emotion = result.get('dominant_emotion', 'N/A')

                    # 바운딩 박스와 분석 결과 표시
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    text = f"나이: {age}, 감정: {emotion}"
                    cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # 콘솔에 결과 출력
                    print(f"카메라 {index} - 나이: {age}, 감정: {emotion}")

                except Exception as e:
                    print(f"처리 중 오류 발생: {e}")

            # 결과 프레임 표시
            cv2.imshow(f"카메라 {index}", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

finally:
    for cam in cameras:
        cam.release()
    cv2.destroyAllWindows()

'''
'''
import cv2
import dlib
from deepface import DeepFace

# dlib 얼굴 검출기 초기화
detector = dlib.get_frontal_face_detector()

def capture_and_analyze_face(camera_id):
    cap = cv2.VideoCapture(camera_id)
    ret, frame = cap.read()
    if not ret:
        print(f"카메라 {camera_id} 캡처 실패")
        cap.release()
        return None, None, frame

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)
    if len(faces) == 0:
        print("얼굴 검출 실패")
        cap.release()
        return None, None, frame

    face = faces[0]  # 첫 번째 얼굴 사용
    x, y, w, h = face.left(), face.top(), face.width(), face.height()
    face_image = frame[y:y+h, x:x+w]

    try:
        # DeepFace를 사용하여 나이와 감정 분석
        result = DeepFace.analyze(face_image, actions=['age', 'emotion'], enforce_detection=False)

        # 결과가 리스트로 반환된 경우 첫 번째 요소 사용
        if isinstance(result, list) and len(result) > 0:
            result = result[0]

        age = result.get('age', 'N/A')
        emotion = result.get('dominant_emotion', 'N/A')

        # 분석 결과를 원본 이미지에 표시
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        text = f"Age: {age}, Emotion: {emotion}"
        cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    except Exception as e:
        print(f"분석 중 오류 발생: {e}")

    cap.release()
    return age, emotion, frame

# 카메라 0과 1에서 사진 캡처 후 분석
age0, emotion0, image0 = capture_and_analyze_face(0)
age1, emotion1, image1 = capture_and_analyze_face(1)

# 캡처 및 분석된 이미지 저장
if image0 is not None:
    cv2.imwrite("camera_0_result.jpg", image0)
if image1 is not None:
    cv2.imwrite("camera_1_result.jpg", image1)

if age0 is not None and age1 is not None:
    print(f"카메라 0 - 나이: {age0}, 감정: {emotion0}")
    print(f"카메라 1 - 나이: {age1}, 감정: {emotion1}")
    # 나이와 감정 비교
    age_difference = abs(age0 - age1)
    print(f"나이 차이: {age_difference}")
    if emotion0 == emotion1:
        print(f"두 사람의 감정이 같습니다: {emotion0}")
    else:
        print(f"두 사람의 감정이 다릅니다. 카메라 0: {emotion0}, 카메라 1: {emotion1}")
else:
    print("한 명 이상의 얼굴 분석에 실패했습니다.")


def analyze_face_and_save(camera_id=0):
    cap = cv2.VideoCapture(camera_id)
    ret, frame = cap.read()
    if ret:
        # 얼굴 검출
        faces = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        if len(faces) == 0:
            print("No faces detected.")
            cap.release()
            return

        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            # 얼굴에 바운딩 박스 그리기
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        try:
            # DeepFace 분석
            results = DeepFace.analyze(frame, actions=['age', 'emotion'], enforce_detection=False)

            # 결과가 리스트 형태로 반환되는 경우, 첫 번째 결과 사용
            if isinstance(results, list) and len(results) > 0:
                results = results[0]

            age = results.get('age', 'N/A')
            emotion = results.get('dominant_emotion', 'N/A')
            # 분석 결과를 이미지에 표시
            cv2.putText(frame, f"Age: {age}, Emotion: {emotion}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)
            # 이미지 저장
            cv2.imwrite(f"face_analysis_result_{camera_id}.jpg", frame)
            print(f"Camera {camera_id} - Age: {age}, Emotion: {emotion}")
        except Exception as e:
            print(f"Face analysis failed: {e}")
    else:
        print(f"Camera {camera_id} capture failed.")
    cap.release()
    
    def continuous_face_analysis(camera_id=0):
    cap = cv2.VideoCapture(camera_id)
    print("Real-time face analysis started. Press 'q' to stop.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        faces = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        for face in faces:
            x, y, w, h = face.left(), face.top(), face.width(), face.height()
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # 얼굴 부분만 DeepFace 분석을 위해 추출
            face_img = frame[y:y+h, x:x+w]

            try:
                # 각 프레임마다 DeepFace 분석 실행
                results = DeepFace.analyze(face_img, actions=['age', 'emotion'], enforce_detection=False)
                age = results['age']
                emotion = results['dominant_emotion']
                cv2.putText(frame, f"Age: {age}, Emotion: {emotion}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            except Exception as e:
                print(f"Face analysis failed: {e}")

        cv2.imshow(f"Real-time Face Analysis - Camera {camera_id}", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Camera {camera_id} real-time face analysis ended.")

continuous_face_analysis(0)
def track_eyes_and_save_if_moving(camera_id=1, duration=5):
    cap = cv2.VideoCapture(camera_id)
    start_time = time.time()
    first_frame_saved = False

    while time.time() - start_time < duration:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)

        for face in faces:
            landmarks = predictor(gray, face)
            for n in range(36, 48):
                x = landmarks.part(n).x
                y = landmarks.part(n).y
                cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)

        cv2.imshow(f"Eye Tracking - Camera {camera_id}", frame)

        if not first_frame_saved:
            cv2.imwrite(f"eye_tracking_start_{camera_id}.jpg", frame)
            print(f"Camera {camera_id} eye tracking start frame saved.")
            first_frame_saved = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.imwrite(f"eye_tracking_end_{camera_id}.jpg", frame)
    print(f"Camera {camera_id} eye tracking end frame saved.")

    cap.release()
    cv2.destroyAllWindows()

# 무한 루프 시작
while True:
    # 나이와 감정 분석 후 결과 사진 저장
    analyze_face_and_save(0)

    # 지속적인 눈 추적
    continuous_eye_tracking(1)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting...")
        break

cv2.destroyAllWindows()
'''



#여기부터

import cv2
import dlib
import time
import threading
import numpy as np
from deepface import DeepFace
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# dlib 라이브러리 초기화
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")


# def save_screenshot(frame, detection_result, camera_id):
#     filename = f"screenshot_{detection_result}_camera_{camera_id}_{int(time.time())}.png"
#     cv2.imwrite(filename, frame)
#     print(f"Screenshot saved: {filename}")


def continuous_face_analysis(camera_id=0):
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"Camera {camera_id} could not be opened.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    print("Real-time face analysis started. Press 'q' to stop.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"Camera {camera_id}: Frame not read properly.")
                break

            faces = detector(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            for face in faces:
                x, y, w, h = face.left(), face.top(), face.width(), face.height()
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # 얼굴 부분만 DeepFace 분석을 위해 추출
                face_img = frame[y:y + h, x:x + w]

                try:
                    # DeepFace 분석
                    results = DeepFace.analyze(frame, actions=['age', 'emotion'], enforce_detection=False)

                    # 결과가 리스트 형태로 반환되는 경우, 첫 번째 결과 사용
                    if isinstance(results, list) and len(results) > 0:
                        results = results[0]

                    age = results.get('age', 'N/A')
                    emotion = results.get('dominant_emotion', 'N/A')
                    # 분석 결과를 이미지에 표시
                    cv2.putText(frame, f"Age: {age}, Emotion: {emotion}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 2)

                    if emotion in ['surprise', 'angry'] or age >= 50:
                        print(f"Camera {camera_id}: 디지털 문맹자입니다 Detected Emotion: {emotion}, Age: {age}")
                    else:
                        print(f"디지털 문맹자가 아닙니다: {emotion}, Age: {age}")

                except Exception as e:
                    print(f"Error analyzing face: {str(e)}")
                    continue

            cv2.imshow(f"Real-time Face Analysis - Camera {camera_id}", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Exception in camera {camera_id}: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print(f"Camera {camera_id} real-time face analysis ended.")


# 관대한 버전
def detect_eye_pattern(movements):
    if len(movements) < 5:
        return "None"

    # Convert movements to numpy array for easier manipulation
    movements = np.array(movements)

    # Calculate deltas (differences between consecutive points)
    deltas = np.diff(movements, axis=0)

    # Check for F pattern: at least one vertical and two horizontal movements
    vertical_moves = np.sum(np.abs(deltas[:, 1]) > 10)
    horizontal_moves = np.sum(np.abs(deltas[:, 0]) > 10)

    if vertical_moves >= 1 and horizontal_moves >= 2:
        return "F"

    # Check for Z pattern: at least two horizontal and one diagonal movements
    horizontal_segments = np.sum(np.abs(deltas[:, 0]) > 10)
    diagonal_segments = np.sum((np.abs(deltas[:, 0]) > 10) & (np.abs(deltas[:, 1]) > 10))

    if horizontal_segments >= 2 and diagonal_segments >= 1:
        return "Z"

    return "None"


def continuous_eye_tracking(camera_id=1):
    cap = cv2.VideoCapture(camera_id)
    if not cap.isOpened():
        print(f"Camera {camera_id} could not be opened.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    left_eye_trace = []
    right_eye_trace = []

    start_time = time.time()
    detection_result = "None"
    previous_detection_result = "None"

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print(f"Camera {camera_id}: Frame not read properly.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray)

            for face in faces:
                landmarks = predictor(gray, face)
                left_eye_points = [landmarks.part(n) for n in range(36, 42)]
                right_eye_points = [landmarks.part(n) for n in range(42, 48)]

                left_eye_center = (
                    int(sum(point.x for point in left_eye_points) / 6),
                    int(sum(point.y for point in left_eye_points) / 6)
                )
                right_eye_center = (
                    int(sum(point.x for point in right_eye_points) / 6),
                    int(sum(point.y for point in right_eye_points) / 6)
                )

                # 눈동자 이동 경로 저장
                left_eye_trace.append(left_eye_center)
                right_eye_trace.append(right_eye_center)

                # 눈 위치 시각화
                for i in range(1, len(left_eye_trace)):
                    cv2.line(frame, left_eye_trace[i - 1], left_eye_trace[i], (0, 255, 0), 1)
                for i in range(1, len(right_eye_trace)):
                    cv2.line(frame, right_eye_trace[i - 1], right_eye_trace[i], (0, 255, 0), 1)

                cv2.circle(frame, left_eye_center, 2, (0, 0, 255), -1)
                cv2.circle(frame, right_eye_center, 2, (0, 0, 255), -1)

            # 10초마다 눈동자 움직임 패턴 감지
            elapsed_time = time.time() - start_time

            if elapsed_time > 10:
                left_pattern = detect_eye_pattern(left_eye_trace)
                right_pattern = detect_eye_pattern(right_eye_trace)

                if left_pattern == "F" or right_pattern == "F":
                    detection_result = "F pattern detected"
                    print("Z pattern detected ")
                    #save_screenshot(frame, detection_result, camera_id)
                elif left_pattern == "Z" or right_pattern == "Z":
                    detection_result = "Z pattern detected"
                    print("F pattern detected")
                    #save_screenshot(frame, detection_result, camera_id)
                else:
                    detection_result = "None"

                if detection_result != "None" and previous_detection_result != "None" and detection_result != previous_detection_result:
                    detection_result += " | Another pattern detected"

                previous_detection_result = detection_result

                start_time = time.time()  # 타이머 리셋
                left_eye_trace = []  # 새로운 추적을 위해 리스트 초기화
                right_eye_trace = []
                frame = np.zeros_like(frame)  # 프레임 초기화 (선을 지우기 위함)

            # 패턴 감지 결과 표시
            if detection_result != "None":
                cv2.putText(frame, detection_result, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow(f"Continuous Eye Tracking - Camera {camera_id}", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Exception in camera {camera_id}: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()


# 실행
threading.Thread(target=continuous_face_analysis, args=(0,)).start()
threading.Thread(target=continuous_eye_tracking, args=(1,)).start()





