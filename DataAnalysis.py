import streamlit as st
import pandas as pd
import altair as alt

def data_analysis_page():
    st.title("DataFrame Demo")
    st.write("This demo shows how to use `st.write` to visualize Pandas DataFrames.")

    # サンプルデータの作成
    data = pd.DataFrame({
        'year': list(range(1961, 1968)) * 2,
        'country': ['China'] * 7 + ['United States of America'] * 7,
        'production': [58.3, 60.7, 61.9, 64.5, 66.8, 69.4, 72.1,
                       93.8, 95.1, 96.2, 98.1, 100.4, 102.5, 104.6]
    })

    # グラフの描画（積み上げなしで重ねて表示）
    chart = alt.Chart(data).mark_area(opacity=0.7).encode(
        x='year:O',
        y=alt.Y('production:Q', stack=None),  # stack=None で積み上げを無効化
        color=alt.Color('country:N', scale=alt.Scale(range=['#1f77b4', '#aec7e8'])),
        tooltip=['year', 'country', 'production']
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
