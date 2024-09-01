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
            st.markdown(f" {prefix}番号")
            for result in results:
                client_number = result["properties"]["クライアント番号"]["formula"]["string"]
                st.markdown(f"{client_number}")
        else:
            st.write("該当するデータが見つかりませんでした。")
    else:
        st.warning("検索ワードを入力してください。")

def search_db_main():
    st.title("クライアント・見込み客DB")

    tab1, tab2 = st.tabs(["データ検索", "新規追加"])

    with tab1:
        st.subheader("データベース検索")
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

        if st.session_state.get('keyword') and not st.session_state.get('search_performed', False):
            st.session_state.search_performed = True
            perform_search()

    with tab2:
        st.subheader("新規データ追加")
        database = st.selectbox("追加先を選択", ["クライアント", "見込み客"], key="add_db_select")

        with st.form("notion_add_form"):
            name = st.text_input("名前")
            kana = st.text_input("カナ")
            notes = st.text_input("備考")

            submitted = st.form_submit_button("追加")

        if submitted:
            if name and kana:  # 名前とカナは必須
                success, next_number, client_number, error_message = add_to_notion(database, name, kana, notes)
                if success:
                    st.success(f"{name} がデータベースに正常に追加されました。")
                    st.markdown(f"**割り当てられた番号**: {next_number}")
                    st.markdown(f"**クライアント番号**: {client_number}")
                else:
                    st.error(f"データの追加中にエラーが発生しました。\n{error_message}")
            else:
                st.warning("名前とカナは必須項目です。")

# この行を追加して、search_db_main 関数を明示的にエクスポートします
main = search_db_main

if __name__ == "__main__":
    search_db_main()