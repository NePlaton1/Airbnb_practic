import streamlit as st
import plotly.express as px
import pandas as pd

def render_neighbourhood_page(df):
    st.title("📈 Районы и соотношение цены и рейтинга")
    st.markdown(
        "Проверяем, есть ли у районов ценовая премия и как качество жилья связано с ценой."
    )

    # Общая статистика по районам
    hood_stats = df.groupby("neighbourhood_cleansed").agg(
        median_price=("price", "median"),
        avg_rating=("review_scores_rating", "mean"),
        count=("id", "count"),
    ).reset_index()
    hood_stats = hood_stats[hood_stats["count"] > 30]

    fig = px.scatter(
        hood_stats,
        x="avg_rating",
        y="median_price",
        size="count",
        color="count",
        hover_name="neighbourhood_cleansed",
        labels={"avg_rating": "Средний рейтинг", "median_price": "Медианная цена (CAD)"},
        title="Цена vs рейтинг по районам",
    )
    city_median_price = df["price"].median()
    fig.add_hline(
        y=city_median_price,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Медианная цена по городу: {city_median_price:.0f} CAD",
    )
    fig.add_vline(
        x=4.7,
        line_dash="dash",
        line_color="green",
        annotation_text="Рейтинг 4.7",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "Цель: найти районы, где цена и рейтинг сочетаются наиболее выгодно для гостей и хозяев."
    )
    top5 = hood_stats.sort_values("avg_rating", ascending=False).head(5)
    st.dataframe(top5[["neighbourhood_cleansed", "median_price", "avg_rating", "count"]])

    # --- Детальный осмотр района ---
    st.subheader("🔍 Детальный осмотр района")
    neighbourhoods_list = sorted(df["neighbourhood_cleansed"].unique())
    if not neighbourhoods_list:
        st.info("Нет данных для отображения районов.")
        return

    #Все районы
    options = ["Все районы"] + neighbourhoods_list
    selected = st.selectbox("Выберите район для детального анализа", options)

    if selected == "Все районы":
        hood_df = df.copy()
    else:
        hood_df = df[df["neighbourhood_cleansed"] == selected].copy()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Объявлений", len(hood_df))
    col2.metric("Медианная цена", f"${hood_df['price'].median():.0f}")
    col3.metric(
        "Средний рейтинг",
        f"{hood_df['review_scores_rating'].mean():.2f}" if "review_scores_rating" in hood_df else "—",
    )
    col4.metric(
        "Средняя занятость (дни)",
        f"{hood_df['occupancy_365'].mean():.0f}" if "occupancy_365" in hood_df else "—",
    )


    if selected != "Все районы":
        show_cols = [
            "name", "price", "room_type", "review_scores_rating",
            "accommodates", "minimum_nights", "availability_365",
        ]
        avail_cols = [c for c in show_cols if c in hood_df.columns]
        st.dataframe(
            hood_df[avail_cols].sort_values("price", ascending=True).head(100),
            use_container_width=True,
        )

    # Карта
    if "latitude" in hood_df.columns and "longitude" in hood_df.columns:
        # Определяем центр карты
        if selected == "Все районы":
            center_lat, center_lon, zoom = 49.2827, -123.1207, 10
        else:
            center_lat = hood_df["latitude"].mean()
            center_lon = hood_df["longitude"].mean()
            zoom = 12

        hover_df = hood_df.copy()
        hover_df["hover_name"] = hover_df["name"].fillna("Без названия") + " — $" + hover_df["price"].astype(str)

        fig_map = px.scatter_mapbox(
            hover_df,
            lat="latitude",
            lon="longitude",
            hover_name="hover_name",
            color_discrete_sequence=["#2E86C1"],  
            mapbox_style="open-street-map",
            zoom=zoom,
            center={"lat": center_lat, "lon": center_lon},
            opacity=0.8,
            size_max=6,  
            
            size=[4] * len(hover_df),  
        )
        fig_map.update_traces(marker=dict(size=6))  
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Нет координат для отображения карты.")
