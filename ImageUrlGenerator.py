import streamlit as st
from modules.image_url_generator import generate_image_urls_and_archive  # modulesからインポート

def image_url_generator_page():
    st.title("画像URL生成とアーカイブ")

    img_dir = st.text_input("画像フォルダのパスを入力してください:", value="/Users/shigikasumi/Dropbox/Projects/Projects/00_Shared_Resources/Uploads/img")
    archive_dir = st.text_input("アーカイブフォルダのパス:", value="/Users/shigikasumi/Dropbox/Projects/Projects/99_Automation_Scripts/011:Img_generate_url/Archived")
    base_url = st.text_input("ベースURL:", value="https://rexli.jp/docs/img/")
    output_file = st.text_input("出力ファイル名:", value="/Users/shigikasumi/Dropbox/Projects/Projects/99_Automation_Scripts/011:Img_generate_url/uploaded_url.md")
    only_latest = st.checkbox("最新の画像のみ処理する")

    if st.button("URLを生成してアーカイブ"):
        if img_dir:
            try:
                image_urls = generate_image_urls_and_archive(img_dir, archive_dir, base_url, output_file, only_latest)
                if image_urls:
                    st.write("## 生成されたURL:")
                    for url in image_urls:
                        st.write(url)
                    st.success(f"URLリストを {output_file} に保存しました。")
                else:
                    st.warning("処理する画像ファイルがありませんでした。")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("画像フォルダのパスを入力してください。")
