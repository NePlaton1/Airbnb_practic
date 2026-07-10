import streamlit as st
import plotly.express as px

def render_room_type_page(df):
    st.title("🏘️ Тип жилья и условия бронирования")
    st.markdown("Анализ влияния типа жилья и минимального срока проживания на стоимость аренды.")

    room_stats = df.groupby("room_type").agg(
        median_price=("price", "median"),
        count=("id", "count")
    ).reset_index()
    fig1 = px.bar(room_stats, x="room_type", y="median_price", color="room_type",
                  title="Медианная цена по типам жилья",
                  labels={"median_price": "Медианная цена (CAD)", "room_type": "Тип жилья"})
    st.plotly_chart(fig1, use_container_width=True)

    stay_stats = df.groupby("min_stay_bin").agg(
        median_price=("price", "median"),
        count=("id", "count")
    ).reset_index()
    fig2 = px.bar(stay_stats, x="min_stay_bin", y="median_price", color="min_stay_bin",
                  title="Цена в зависимости от минимального срока проживания",
                  labels={"median_price": "Медианная цена (CAD)", "min_stay_bin": "Минимальный срок"})
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.box(df, x="room_type", y="price", color="room_type",
                  title="Распределение цены по типам жилья",
                  labels={"price": "Цена (CAD)", "room_type": "Тип жилья"})
    fig3.update_traces(boxpoints=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("Диаграммы показывают распределение цен по различным типам жилья и минимальным срокам бронирования, позволяя сравнить эти ценовые характеристики.")