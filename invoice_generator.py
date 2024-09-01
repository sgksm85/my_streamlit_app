import os
import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import pytz
from modules.notion_integration import fetch_work_hours, update_notion_status

def load_external_css(file_path):
    with open(file_path, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 外部CSSファイルを読み込む
load_external_css("./css/invoice_generator.css") 

HOURLY_RATE = 2700  # 時給2700円

def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    return f"{hours}時間{minutes}分"

def calculate_daily_totals(df, include_amount=False):
    agg_dict = {'労働時間': 'sum'}
    if include_amount:
        agg_dict['金額'] = 'sum'
    
    daily_totals = df.groupby('日付').agg(agg_dict).reset_index()
    daily_totals['労働時間'] = daily_totals['労働時間'].apply(format_timedelta)
    return daily_totals

def save_to_markdown(df, start_date, end_date, total_hours, total_amount, output_dir):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        file_name = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}timerecord.md"
        file_path = os.path.join(output_dir, file_name)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# 労働時間集計 ({start_date} から {end_date} まで)\n\n")
            f.write("| 日付 | 労働時間 | 金額 |\n")
            f.write("|------|----------|------|\n")
            for _, row in df.iterrows():
                f.write(f"| {row['日付']} | {row['労働時間']} | ¥{row['金額']:,} |\n")
            f.write(f"\n**総労働時間: {total_hours}**\n")
            f.write(f"**合計金額: ¥{total_amount:,}**\n")
        
        return file_path
    except Exception as e:
        st.error(f"Markdownファイルの生成中にエラーが発生しました: {e}")
        return None

def custom_table(data, column_config=None):
    st.dataframe(data, use_container_width=True)

def invoice_generator_page():
    st.title("請求明細作成")

    today = date.today()
    start_date = date(today.year, today.month, 1)
    end_date = today

    col1, col2 = st.columns(2)
    with col1:
        user_start_date = st.date_input("開始日を選択", value=start_date)
    with col2:
        user_end_date = st.date_input("終了日を選択", value=end_date)

    # ページ初回ロード時の処理
    if 'initial_daily_totals' not in st.session_state:
        with st.spinner("初期の日毎集計をロードしています..."):
            work_hours_data = fetch_work_hours(start_date, end_date)
            if work_hours_data:
                df = pd.DataFrame(work_hours_data)
                df['労働時間'] = pd.to_timedelta(df['労働時間'] + ':00', errors='coerce')
                initial_daily_totals = calculate_daily_totals(df, include_amount=False)
                st.session_state.initial_daily_totals = initial_daily_totals
            else:
                st.session_state.initial_daily_totals = pd.DataFrame(columns=['日付', '労働時間'])

    # 初期日毎集計の表示
    custom_table(st.session_state.initial_daily_totals)

    if st.button("集計を実行"):
        with st.spinner("集計を実行中..."):
            work_hours_data = fetch_work_hours(user_start_date, user_end_date)
            if work_hours_data:
                df = pd.DataFrame(work_hours_data)
                df['労働時間'] = pd.to_timedelta(df['労働時間'] + ':00', errors='coerce')
                df['金額'] = df['労働時間'].dt.total_seconds().fillna(0) / 3600 * HOURLY_RATE
                df['金額'] = df['金額'].astype(int)

                total_hours = format_timedelta(df['労働時間'].sum())
                total_amount = df['金額'].sum()

                daily_totals = calculate_daily_totals(df, include_amount=True)

                st.session_state.df = df
                st.session_state.daily_totals = daily_totals
                st.session_state.total_hours = total_hours
                st.session_state.total_amount = total_amount
                st.session_state.data_processed = True

                st.success("集計が完了しました。")

    if 'daily_totals' in st.session_state and st.session_state.data_processed:
        st.subheader("日別集計")
        custom_table(st.session_state.daily_totals)

        st.subheader("合計")
        st.write(f"総労働時間: {st.session_state.total_hours}")
        st.write(f"合計金額: ¥{st.session_state.total_amount:,}")
        
        with st.expander("全ての行データを表示"):
            df_display = st.session_state.df[['日付', '開始時間', '終了時間', '労働時間', '金額']].copy()
            df_display['労働時間'] = df_display['労働時間'].apply(format_timedelta)
            custom_table(df_display)

        if st.button("Markdownファイルを生成"):
            with st.spinner("Markdownファイルを生成中..."):
                output_dir = os.path.join(os.getcwd(), "invoice_output")
                file_path = save_to_markdown(st.session_state.daily_totals, user_start_date, user_end_date, 
                                         st.session_state.total_hours, st.session_state.total_amount, output_dir)
                if file_path:
                    st.success(f"Markdownファイルが生成されました: {file_path}")
                    for _, entry in st.session_state.df.iterrows():
                        update_notion_status(entry["Page ID"], "請求済")
                    st.success("Notionのステータスが請求済に更新されました。")
                else:
                    st.error("Markdownファイルの生成に失敗しました。")

if __name__ == "__main__":
    invoice_generator_page()