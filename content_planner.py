import streamlit as st
from datetime import date

def content_planner():
    st.title("コンテンツプランナー")
    st.write("効果的なLINEコンテンツを計画・管理できます。")
    
    content_type = st.selectbox("コンテンツタイプ", ["テキストメッセージ", "画像メッセージ", "動画メッセージ", "リッチメッセージ"])
    content_theme = st.text_input("テーマ")
    target_audience = st.multiselect("ターゲット層", ["10代", "20代", "30代", "40代", "50代以上"])
    scheduled_date = st.date_input("配信予定日", min_value=date.today())
    
    if st.button("コンテンツ案を保存"):
        st.success("コンテンツ案が保存されました。")
        st.write(f"タイプ: {content_type}")
        st.write(f"テーマ: {content_theme}")
        st.write(f"ターゲット層: {', '.join(target_audience)}")
        st.write(f"配信予定日: {scheduled_date}")