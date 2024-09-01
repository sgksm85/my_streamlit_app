import streamlit as st
import pandas as pd
import plotly.express as px

def dashboard_home():
    st.title("ダッシュボード")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="総友達数", value="112,893", delta="1,234")
    with col2:
        st.metric(label="月間アクティブユーザー", value="78,234", delta="-2,345")
    with col3:
        st.metric(label="平均反応率", value="23.8%", delta="1.2%")
    
    st.subheader("最近のアクティビティ")
    activities = [
        "新規キャンペーン「夏のセール」開始",
        "友達数10万人突破",
        "新機能「おすすめ商品」リリース"
    ]
    for activity in activities:
        st.write(f"- {activity}")

    # クライアントの数値分析のサンプル
    st.subheader("クライアント数値分析")
    df = pd.DataFrame({
        'クライアント': ['A社', 'B社', 'C社', 'D社'],
        '友達数増加率': [15, 22, 8, 30],
        'メッセージ開封率': [68, 75, 62, 80],
        'コンバージョン率': [3.2, 4.5, 2.8, 5.1]
    })
    st.dataframe(df)

    # グラフの追加
    fig = px.bar(df, x='クライアント', y=['友達数増加率', 'メッセージ開封率', 'コンバージョン率'], 
                 title='クライアント別パフォーマンス比較')
    st.plotly_chart(fig)