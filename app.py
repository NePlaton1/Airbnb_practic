import streamlit as st
from data_utils import load_data
from filters import apply_filters
from views.overview import render_overview
from views.neighbourhood import render_neighbourhood_page
from views.room_type import render_room_type_page
from views.availability import render_availability_page

def main():
    df = load_data()
    filtered_df, page = apply_filters(df)

    if page == "Обзор":
        render_overview(filtered_df)
    elif page == "Инсайт 1: Районы":
        render_neighbourhood_page(filtered_df)
    elif page == "Инсайт 2: Типы жилья":
        render_room_type_page(filtered_df)
    elif page == "Инсайт 3: Доступность":
        render_availability_page(filtered_df)

if __name__ == "__main__":
    main()