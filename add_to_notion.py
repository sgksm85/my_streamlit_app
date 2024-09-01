import streamlit as st
from modules.notion_integration import search_clients, search_prospects, add_to_notion

def reset_search():
    if 'keyword' in st.session_state:
        st.session_state.keyword = ""
    if 'search_performed' in st.session_state:
        st.session_state.search_performed = False

def perform_search():
    if st.session_state.keyword:
        if st.session_state.selected_db == "クライアント":
            results = search_clients(st.session_state.keyword)
            prefix = "クライアント"
        else:
            results = search_prospects(st.session_state.keyword)
            prefix = "見込み客"

        if results:
            for result in results:
                client_number = result["properties"]["クライアント番号"]["formula"]["string"]
                st.markdown(f"#{prefix}  \n\n{client_number}")
        else:
            st.write("該当するデータが見つかりませんでした。")
    else:
        st.warning("検索ワードを入力してください。")

def main():
    st.title("クライアント・見込み客情報検索・追加")

    tab1, tab2 = st.tabs(["検索", "追加"])

    with tab1:
        st.subheader("データベース検索")
        # 既存の検索機能をここに配置
        st.session_state.selected_db = st.selectbox(
            "検索対象を選んでください",
            ["クライアント", "見込み客"],
            key="db_select"
        )

        keyword = st.text_input("名前の一部を入力してください:", value=st.session_state.get('keyword', ''), key="search_input")
        if keyword != st.session_state.get('keyword', ''):
            st.session_state.keyword = keyword
            st.session_state.search_performed = False

        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("検索"):
                st.session_state.search_performed = True
                perform_search()

        with col2:
            if st.button("リセット"):
                reset_search()
                st.rerun()

        # Enterキーでの検索
        if st.session_state.get('keyword') and not st.session_state.get('search_performed', False):
            st.session_state.search_performed = True
            perform_search()

    with tab2:
        st.subheader("新規データ追加")
        add_db = st.selectbox("追加先を選んでください", ["クライアント", "見込み客"], key="add_db_select")
        name = st.text_input("名前")
        kana = st.text_input("カナ")
        category = st.multiselect("カテゴリ", ["個人", "法人", "その他"])
        tags = st.multiselect("タグ", ["重要", "フォローアップ必要", "長期契約"])
        notes = st.text_area("備考")

        if st.button("Notionに追加"):
            if name and kana:
                success = add_to_notion(add_db, name, kana, category, tags, notes)
                if success:
                    st.success("データが正常に追加されました。")
                else:
                    st.error("データの追加中にエラーが発生しました。")
            else:
                st.warning("名前とカナは必須項目です。")

if __name__ == "__main__":
    main()