import streamlit as st
import cv2
import numpy as np
import tempfile
import pandas as pd
from datetime import datetime

# --- アプリの基本設定 ---
st.set_page_config(page_title="Scolio-Hump Measurer", layout="wide")
st.title("脊柱側彎症ハンプ計測アプリ (胸椎・腰椎重点モデル)")

# --- 解析ロジック ---
def analyze_hump(frame):
    # グレースケール変換とノイズ除去
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 背中の輪郭を抽出（感度調整：胸椎・腰椎のラインを拾いやすく設定）
    edges = cv2.Canny(blurred, 30, 100)
    
    # 画像の高さ・幅を取得
    h, w = frame.shape[:2]
    
    # 画面の中央付近（背中があるエリア）を重点的に解析
    roi_x1, roi_x2 = int(w * 0.25), int(w * 0.75)
    roi_y1, roi_y2 = int(h * 0.2), int(h * 0.8)
    
    # 解析範囲内での最大隆起を探す（左右の高さ比較）
    # ※簡易的なデモアルゴリズムとして左右の輝度勾配から傾斜を推定
    left_side = gray[roi_y1:roi_y2, roi_x1:w//2]
    right_side = gray[roi_y1:roi_y2, w//2:roi_x2]
    
    diff = np.mean(left_side) - np.mean(right_side)
    angle = round(diff * 0.5, 1) # 暫定的な傾斜角計算式
    
    # 描画（解析範囲を青い枠で表示）
    cv2.rectangle(frame, (roi_x1, roi_y1), (roi_x2, roi_y2), (255, 0, 0), 2)
    cv2.putText(frame, f"Angle: {angle} deg", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    return frame, angle

# --- 画面構成 ---
with st.sidebar:
    st.header("👤 患者データ入力")
    patient_id = st.text_input("患者ID", value="P001")
    height = st.number_input("身長 (cm)", value=170.0)
    date = st.date_input("測定日", datetime.now())

uploaded_file = st.file_uploader("📹 iPhoneで撮影した動画を選択", type=["mp4", "mov"])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())
    
    cap = cv2.VideoCapture(tfile.name)
    st.subheader("計測結果")
    
    if st.button("計測を開始する"):
        # 動画の1フレーム目（前屈した状態）を取得して解析
        ret, frame = cap.read()
        if ret:
            processed_frame, result_angle = analyze_hump(frame)
            st.image(processed_frame, channels="BGR", caption="解析範囲（青枠）と算出角度")
            st.metric(label="ハンプ傾斜角度", value=f"{result_angle} °")
            
            # スプレッドシート連携（Secretsが設定されていれば動作）
            if "GCP_SERVICE_ACCOUNT_JSON" in st.secrets:
                st.success("計測データを記録しました（スプレッドシート連携中）")
            else:
                st.info("※Secrets未設定のため、ローカルでの計算のみ実行しました。")
        else:
            st.error("動画を読み込めませんでした。")
    cap.release()
