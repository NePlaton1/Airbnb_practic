from datetime import datetime
import os
from zipfile import Path

import streamlit as st
import pandas as pd
import plotly.express as px
from geo_viz import build_neighbourhood_map




def build_outlier_sensitivity(df):
    full_mean = df["price"].mean()
    full_median = df["price"].median()
    rows = []
    for threshold in [100, 1000, 10000, 30000]:
        capped = df[df["price"] <= threshold]
        rows.append({
            "Порог": threshold,
            "Объявлений": len(capped),
            "Средняя цена": round(capped["price"].mean(), 2),
            "Медиана": round(capped["price"].median(), 2),
            "Изменение средней": round(((capped["price"].mean() - full_mean) / full_mean) * 100, 2),
            "Изменение медианы": round(((capped["price"].median() - full_median) / full_median) * 100, 2),
        })
    return pd.DataFrame(rows)




def render_overview(df):
    st.title("Обзор рынка Airbnb в Ванкувере")
    
    
    last_update_file = "CleanData/last_update.txt"
    if os.path.exists(last_update_file):
        with open(last_update_file, "r", encoding="utf-8") as f:
            date_str = f.read().strip()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            formatted = dt.strftime("%B %Y")
        except:
            formatted = date_str
        st.caption(f"📅 Данные актуальны на: {formatted}")
    else:
        st.caption("📅 Дата среза данных отсутствует")



    col1, col2, col3 = st.columns(3)
    col1.metric("Объявлений:", len(df))
    col2.metric("Средняя цена:", f"${df['price'].mean():.0f}")
    col3.metric("Медианная цена:", f"${df['price'].median():.0f}")

    st.subheader("Чувствительность к выбросам")
    st.markdown("В датасете присутствуют объекты с различными ценами. В таблице ниже показано, как меняются ключевые метрики (средняя цена и медиана) при исключении объектов выше определённого ценового порога.")
    sensitivity = build_outlier_sensitivity(df)
    st.dataframe(sensitivity, use_container_width=True)

    fig = px.histogram(df, x="price", nbins=80, log_y=True,
                       title="Распределение цены за ночь", labels={"price": "Цена (CAD)"})
    st.plotly_chart(fig, use_container_width=True)

    room_price = df.groupby("room_type")["price"].median().reset_index()
    fig2 = px.bar(room_price, x="room_type", y="price", color="room_type",
                  title="Медианная цена по типу жилья",
                  labels={"price": "Медианная цена (CAD)", "room_type": "Тип жилья"})
    st.plotly_chart(fig2, use_container_width=True)

    if "latitude" in df.columns and "longitude" in df.columns:
        st.subheader("Карта объявлений")
        map_fig = px.scatter_mapbox(df, lat="latitude", lon="longitude", color="price",
                                    size="price", hover_name="neighbourhood_cleansed",
                                    mapbox_style="open-street-map", zoom=10, height=500,
                                    size_max=10, labels={"price": "Цена"})
        st.plotly_chart(map_fig, use_container_width=True)

    st.subheader("Карта цен по районам")
    try:
        geo_fig = build_neighbourhood_map(df, value_col="price", agg="median")
        st.plotly_chart(geo_fig, use_container_width=True)
    except Exception as e:
        st.info(f"Карта районов временно недоступна: {e}")