import streamlit as st

def proposal_generator():
    st.title("提案書ジェネレーター")
    st.write("クライアント向けの提案書を簡単に作成できます。")
    
    client_name = st.text_input("クライアント名")
    industry = st.selectbox("業界", ["小売", "飲食", "美容", "不動産", "その他"])
    goal = st.multiselect("マーケティング目標", ["認知度向上", "顧客獲得", "売上増加", "顧客維持"])
    
    if st.button("提案書生成"):
        st.write(f"### {client_name}様 LINEマーケティング提案書")
        st.write(f"業界: {industry}")
        st.write("マーケティング目標:")
        for g in goal:
            st.write(f"- {g}")
        st.write("提案内容:")
        st.write("1. LINEオフィシャルアカウントの最適化")
        st.write("2. ターゲット層に合わせたコンテンツ戦略")
        st.write("3. LINE広告を活用したリーチ拡大")
        st.write("4. データ分析に基づくPDCAサイクルの実施")
        st.write("5. LINEポイントを活用したキャンペーン展開")
        st.write("6. リッチメニューのカスタマイズによるUX向上")
        st.write("7. LINE公式アカウントとECサイトの連携強化")
        st.write("8. AIチャットボットの導入による顧客対応の自動化")