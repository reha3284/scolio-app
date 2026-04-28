import streamlit as st
import pandas as pd
from datetime import datetime

# アプリのタイトルと設定
st.set_page_config(page_title="Scoli-Hump Private", layout="wide")
st.title("側弯症ハンプ計測アプリ (Private)")

# セッション状態の初期化
if 'px_scale' not in st.session_state:
    st.session_state['px_scale'] = None

# サイドバー：患者情報
with st.sidebar:
    st.header("📋 患者データ入力")
    patient_id = st.text_input("患者ID", "P001")
    height = st.number_input("身長(cm)", 100.0, 200.0, 160.0)
    date = st.date_input("測定日", datetime.now())

# メイン画面：動画アップロード
st.header("1. 動画のアップロード")
video_file = st.file_uploader("iPhoneで撮影した動画を選択", type=["mp4", "mov"])

if video_file:
    st.video(video_file)
    st.info("動画を確認したら、次のステップで計測を行います。")
    
    # 将来的にここにStep1~3のロジックを統合します
    st.button("計測を開始する")

# 履歴表示（仮）
st.header("2. 履歴（スプレッドシート連携予定）")
st.write("ここに過去のデータが表示されるようになります。")
