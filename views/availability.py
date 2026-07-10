import streamlit as st
import plotly.express as px

def render_availability_page(df):
    st.title("🗓️ Цена и доступность жилья")
    st.markdown("Анализ зависимости между доступностью жилья, уровнем занятости и ценой за ночь.")

    avail_stats = df.groupby("availability_bin").agg(
        median_price=("price", "median"),
        count=("id", "count")
    ).reset_index()
    fig1 = px.bar(avail_stats, x="availability_bin", y="median_price", color="availability_bin",
                  title="Медианная цена по сегментам доступности",
                  labels={"median_price": "Медианная цена (CAD)", "availability_bin": "Доступность (дней)"})
    st.plotly_chart(fig1, use_container_width=True)

    fig_box = px.box(df, x="availability_bin", y="price", color="availability_bin",
                     title="Распределение цены по сегментам доступности")
    fig_box.update_traces(boxpoints=False)
    st.plotly_chart(fig_box, use_container_width=True)

    occ_stats = df.groupby("occupancy_bin")["price"].median().reset_index()
    fig_occ = px.bar(occ_stats, x="occupancy_bin", y="price",
                     title="Медианная цена по уровню занятости (дней в году)",
                     labels={"occupancy_bin": "Занятость (дней)", "price": "Медианная цена (CAD)"})
    st.plotly_chart(fig_occ, use_container_width=True)

    st.markdown(
        "На диаграммах показана связь между занятостью объекта (количеством дней в году, когда жилье занято) "
        "и установленной ценой за ночь. Данные позволяют увидеть соотношение между этими показателями в различных сегментах."
    )