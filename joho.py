import streamlit as st
import cv2
import mediapipe as mp
from PIL import Image
import numpy as np

# 顔検出と笑顔評価を行う関数
def analyze_image(image):
    # 画像をOpenCV形式に変換
    img_array = np.array(image)
    img_rgb = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

    # 画像の明るさを計算
    brightness = np.mean(img_rgb)

    # Mediapipeを使用して顔を検出
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.2)

    results = face_detection.process(img_rgb)

    # 顔が検出されたかどうかを確認
    face_detected = False
    smile_score = 0  # 笑顔スコア（初期値）

    if results.detections:
        face_detected = True
        
        # 顔の表情を解析して笑顔スコアを算出
        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.2)

        face_landmarks = face_mesh.process(img_rgb)
        if face_landmarks.multi_face_landmarks:
            for landmarks in face_landmarks.multi_face_landmarks:
                # 顔の口周りのランドマークを取得して笑顔のスコアを計算
                mouth_open = landmarks.landmark[13].y - landmarks.landmark[14].y  # 上唇と下唇の間隔
                smile_score = mouth_open  # 口の開き具合で笑顔の度合いを計算

    return face_detected, brightness, smile_score

# Streamlitインターフェース
st.title("ベストショット選定アプリ（笑顔スコア付き）")

st.write("複数の画像をアップロードし、ベストショットを自動で選んでくれます。笑顔のスコアも表示されます。")

# 複数画像をアップロード
uploaded_images = st.file_uploader("画像を選択（複数可）", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_images:
    # アップロードされた全ての画像を処理
    best_image = None
    best_score = -1  # ベストショットのスコア（初期値は-1）

    for img_file in uploaded_images:
        image = Image.open(img_file)
        st.image(image, caption=f"アップロードした画像: {img_file.name}", use_column_width=True)

        # 画像解析
        face_detected, brightness, smile_score = analyze_image(image)

        # スコアの計算
        score = 0
        if face_detected:
            score += 50  # 顔が検出された場合は50点
        if brightness > 100:  # 明るさが十分であれば追加点
            score += 30
        score += smile_score * 50  # 笑顔スコアに基づいて加点（最大50点）

        st.write(f"画像「{img_file.name}」のスコア: {score} (顔検出: {'あり' if face_detected else 'なし'}, 明るさ: {brightness}, 笑顔スコア: {smile_score:.2f})")

        # 最もスコアが高い画像をベストショットとして選択
        if score > best_score:
            best_score = score
            best_image = image

    # ベストショットを表示
    if best_image:
        st.write("🎉 ベストショットはこの画像です！")
        st.image(best_image, caption="ベストショット", use_column_width=True)
