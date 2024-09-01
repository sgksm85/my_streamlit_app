import streamlit as st
import pandas as pd

def link_collection():
    st.title("リンク集")
    
    # 公開されたGoogle SheetsのURL（CSV形式でエクスポート）
    # https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/export?format=csv&gid=[SHEET_ID]
    sheet_url = "https://docs.google.com/spreadsheets/d/1VVLdVGzerxM9Q4LRa5VeDwDIPfZ5ZGIgUMteQu3n62Y/export?format=csv&gid=254512747"
    
    try:
        # DataFrameとして読み込む
        df = pd.read_csv(sheet_url)
        
        # リンク集を表示
        for _, row in df.iterrows():
            st.markdown(f"[{row['プロジェクト名']}]({row['提案書ファイル']})")
        
        # 新しいリンクを追加
        st.subheader("新しいリンクを追加")
        st.write("注意: この機能は読み取り専用のスプレッドシートでは動作しません。")
        new_title = st.text_input("プロジェクト名")
        new_url = st.text_input("提案書ファイル")
        if st.button("追加"):
            st.warning("この機能は現在利用できません。スプレッドシートを直接編集してください。")
    
    except Exception as e:
        st.error(f"スプレッドシートの読み込みに失敗しました: {e}")
        st.write("スプレッドシートが公開されていること、URLが正しいことを確認してください。")