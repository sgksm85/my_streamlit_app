import streamlit as st
import pandas as pd
from modules.notion_config import NOTION_PROJECT_DATABASE_ID
from modules.notion_integration import add_to_notion_custom, search_todo_or_project_database

# 外部CSSを読み込む
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def project_section():
    
    projects = search_todo_or_project_database(NOTION_PROJECT_DATABASE_ID)
    
    projects_filtered = [
        project for project in projects 
        if project['properties']['進捗状況']['status']['name'] not in ["終了", "成約", "完了"]
    ]
    
    projects_sorted = sorted(
        projects_filtered,
        key=lambda x: x['properties'].get('タグ 2', {}).get('select', {}).get('name', "")
    )

    data = []
    for project in projects_sorted:
        tags = ", ".join([tag["name"] for tag in project['properties'].get('タグ', {}).get('multi_select', [])]) if project['properties'].get('タグ', {}).get('multi_select') else "なし"
        name = project['properties']['名前']['title'][0]['text']['content']
        status = project['properties']['進捗状況']['status']['name']
        tag2 = project['properties'].get('タグ 2', {}).get('select', {}).get('name', "なし")
        url = project['properties'].get('URL', {}).get('url', "なし")
        url_link = f'<a href="{url}" target="_blank">URLを開く</a>' if url != "なし" else "なし"
        notion_link = f'<a href="{project["url"]}" target="_blank">Notion Link</a>'
        data.append([name, status, tags, tag2, url_link, notion_link])

    df_project = pd.DataFrame(data, columns=["名前", "進捗状況", "タグ", "タグ 2", "URL", "Notionリンク"])

    # テーブルのデザインを改善
    st.write(df_project.to_html(escape=False, index=False, classes='table table-striped'), unsafe_allow_html=True)

    # 編集リンクを追加
    st.markdown('<a href="https://www.notion.so/shigi-k/097f9506e00b4b17b0d350bbdfe532d3?v=6da221d02a424edd8aa6a719c34ae24e&pvs=4" target="_blank">編集はこちら</a>', unsafe_allow_html=True)

    # プロジェクトの追加フォーム
    with st.form(key="add_project_form"):
        name = st.text_input("名前")
        status = st.selectbox("進捗状況", ["保留", "未着手", "進行中", "成約", "終了"], index=2)  # デフォルトを「進行中」に設定
        tags = st.multiselect("タグ", ["REXLIコンテンツ", "提案書", "WSコンテンツ"])
        tag2 = st.selectbox("タグ 2", ["★★★", "★★☆", "★☆☆"])
        notes = st.text_area("備考")
        url = st.text_input("URL")
        submit_project = st.form_submit_button(label="追加")

    if submit_project:
        success, error_message = add_to_notion_custom(
            NOTION_PROJECT_DATABASE_ID,
            name=name,
            status=status,
            tags=tags,
            tag2=tag2,
            notes=notes,
            url=url
        )
        if success:
            st.success("プロジェクトが追加されました")
        else:
            st.error(f"エラーが発生しました: {error_message}")

def main():
    st.title("プロジェクト管理")
    local_css("/Users/shigikasumi/Dropbox/Projects/Projects/99_Automation_Scripts/my_streamlit_app/css/project_manager.css")
    project_section()

if __name__ == "__main__":
    main()