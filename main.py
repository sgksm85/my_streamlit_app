import streamlit as st
from dashboard import dashboard_home
from proposal import proposal_generator
from content_planner import content_planner
from link_collection import link_collection
from Home import home_page
from ImageUrlGenerator import image_url_generator_page
from DataAnalysis import data_analysis_page
from search_db import main as search_db_main
from todo_manager import main as todo_manager_main
from project_manager import main as project_manager_main
from invoice_generator import invoice_generator_page

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    try:
        load_css("styles.css")
    except FileNotFoundError:
        st.warning("styles.cssファイルが見つかりません。")

    st.sidebar.markdown("""
        <style>
        .sidebar-link {
            color: #f2f2f2;
            text-decoration: none;
            display: block;
            padding: 5px 0;
        }
        .sidebar-link:hover {
            color: #1f77b4;
        }
        </style>
        """, unsafe_allow_html=True)

    pages = {
        "ホーム": home_page,
        "ダッシュボード": dashboard_home,
        "Todo Manager": todo_manager_main,
        "Project Manager": project_manager_main,
        "Client DB": search_db_main, 
        "Image URL Generator": image_url_generator_page,
        "Data Analysis": data_analysis_page,
        "提案書ジェネレーター": proposal_generator,
        "コンテンツプランナー": content_planner,
        "リンク集": link_collection,
        "請求明細": invoice_generator_page,
    }

    for page_name, page_func in pages.items():
        st.sidebar.markdown(f'<a href="/?page={page_name}" target="_self" class="sidebar-link">{page_name}</a>', unsafe_allow_html=True)

    page = st.query_params.get("page", "ホーム")
    
    if page in pages:
        pages[page]()
    else:
        st.error("ページが見つかりません。")

    st.sidebar.write("Debug Info:")
    st.sidebar.write(f"Current page: {page}")

if __name__ == "__main__":
    main()