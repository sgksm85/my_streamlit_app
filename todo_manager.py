import streamlit as st
import pandas as pd
from datetime import datetime
from modules.notion_config import NOTION_TODO_DATABASE_ID
from modules.notion_integration import add_to_notion_custom, search_todo_or_project_database, update_notion_custom

# 外部CSSを読み込む
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def todo_section():
    status_options = ["保留", "未着手", "進行中", "完了"]

    todos = search_todo_or_project_database(NOTION_TODO_DATABASE_ID)
    
    data = []
    for todo in todos:
        status = todo['properties']['進捗状況']['status']['name']
        if status == "完了":
            continue  # 完了タスクをスキップ
        name = todo['properties']['名前']['title'][0]['text']['content']
        start_date = todo['properties'].get('Start Date', {}).get('date', {}).get('start', "なし")
        due_date = todo['properties'].get('Due Date', {}).get('date', {}).get('start', "なし")
        url = todo['properties'].get('URL', {}).get('url', "なし")
        url_link = f'<a href="{url}" target="_blank">URLを開く</a>' if url != "なし" else "なし"
        notion_link = f'<a href="{todo["url"]}" target="_blank">Notion Link</a>'
        data.append([name, status, start_date, due_date, url_link, notion_link])

    df_todo = pd.DataFrame(data, columns=["名前", "進捗状況", "開始日", "期限日", "URL", "Notionリンク"])

    st.write(df_todo.to_html(escape=False, index=False, classes='table table-striped'), unsafe_allow_html=True)

    st.subheader("TODOの追加")

    with st.form(key="todo_form"):
        name = st.text_input("名前")
        status = st.selectbox("進捗状況", status_options, index=status_options.index("進行中"))
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("開始日")
        with col2:
            due_date = st.date_input("期限日")
        
        url = st.text_input("URL")
        submit_todo = st.form_submit_button(label="追加")
    
    if submit_todo:
        success, error_message = add_to_notion_custom(
            NOTION_TODO_DATABASE_ID,
            name=name,
            status=status,
            start_date=start_date,
            due_date=due_date,
            url=url if url else None
        )
        if success:
            st.success("TODOが追加されました")
        else:
            st.error(f"エラーが発生しました: {error_message}")

    st.subheader("TODOの編集")
    selected_todo = st.selectbox("編集するTODOを選択", options=[todo['properties']['名前']['title'][0]['text']['content'] for todo in todos])
    selected_todo_data = next(todo for todo in todos if todo['properties']['名前']['title'][0]['text']['content'] == selected_todo)

    with st.form(key="edit_todo_form"):
        new_name = st.text_input("名前", value=selected_todo_data['properties']['名前']['title'][0]['text']['content'])
        new_status = st.selectbox("進捗状況", status_options, index=status_options.index(selected_todo_data['properties']['進捗状況']['status']['name']))
        
        col1, col2 = st.columns(2)
        with col1:
            new_start_date = st.date_input("開始日", value=datetime.strptime(selected_todo_data['properties'].get('Start Date', {}).get('date', {}).get('start', '1970-01-01'), '%Y-%m-%d') if selected_todo_data['properties'].get('Start Date', {}).get('date', {}).get('start') else None)
        with col2:
            new_due_date = st.date_input("期限日", value=datetime.strptime(selected_todo_data['properties'].get('Due Date', {}).get('date', {}).get('start', '1970-01-01'), '%Y-%m-%d') if selected_todo_data['properties'].get('Due Date', {}).get('date', {}).get('start') else None)
        
        new_url = st.text_input("URL", value=selected_todo_data['properties'].get('URL', {}).get('url', ""))
        submit_edit_todo = st.form_submit_button(label="更新")
    
    if submit_edit_todo:
        success, error_message = update_notion_custom(
            NOTION_TODO_DATABASE_ID,
            selected_todo_data['id'],
            name=new_name,
            status=new_status,
            start_date=new_start_date,
            due_date=new_due_date,
            url=new_url if new_url else None
        )
        if success:
            st.success("TODOが更新されました")
        else:
            st.error(f"エラーが発生しました: {error_message}")

def main():
    st.title("TODO管理")
    local_css("/Users/shigikasumi/Dropbox/Projects/Projects/99_Automation_Scripts/my_streamlit_app/css/todo_manager.css")
    todo_section()

if __name__ == "__main__":
    main()