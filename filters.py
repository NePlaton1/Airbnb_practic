import streamlit as st

def apply_filters(df):
    """Боковая панель с фильтрами и выбором страницы."""
    st.sidebar.title("Airbnb Vancouver")

    page = st.sidebar.radio("📊 Раздел", ["Обзор", "Инсайт 1: Районы", "Инсайт 2: Типы жилья", "Инсайт 3: Доступность"])
    st.sidebar.header("Фильтры:")

    room_types = st.sidebar.multiselect(
        "Тип жилья:",
        options=sorted(df["room_type"].dropna().unique()),
        default=sorted(df["room_type"].dropna().unique()),
    )


    neighbourhoods = st.sidebar.multiselect(
        "Район",
        options=sorted(df["neighbourhood_cleansed"].dropna().unique()),
        default=[],
    )


    price_min, price_max = st.sidebar.slider(
        "Цена за ночь (CAD)",
        float(df["price"].min()),
        float(df["price"].max()),
        (50.0, 500.0),
    )

    
    filtered_df = df[df["room_type"].isin(room_types)]
    if neighbourhoods:
        filtered_df = filtered_df[filtered_df["neighbourhood_cleansed"].isin(neighbourhoods)]
    filtered_df = filtered_df[(filtered_df["price"] >= price_min) & (filtered_df["price"] <= price_max)]
    if filtered_df.empty:
        st.warning("Нет данных, удовлетворяющих выбранным фильтрам. Измените параметры.")
        st.stop()
    return filtered_df, page