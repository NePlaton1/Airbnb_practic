import pandas as pd
from pathlib import Path
import streamlit as st
from datetime import datetime

@st.cache_data
def load_data():
    """Загружает очищенный датасет и добавляет служебные признаки."""
    candidates = [
        Path("data/listings_clean.csv"),
        Path("CleanData/listings_clean.csv"),
        Path("CleanData/listings_clean_v2.csv"),
    ]
    for path in candidates:
        if path.exists():
            df = pd.read_csv(path)
            break
    else:
        st.error("Очищенный датасет не найден")
        st.stop()


    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")

    for col in ["review_scores_rating", "review_scores_accuracy", "review_scores_cleanliness",
                "review_scores_checkin", "review_scores_communication", "review_scores_location",
                "review_scores_value"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df[col] = df[col].fillna(df[col].median())
    
    if "last_scraped" in df.columns:
        df["last_scraped"] = pd.to_datetime(df["last_scraped"], errors="coerce")

    # Приведение типов
    if "minimum_nights" in df.columns:
        df["minimum_nights"] = pd.to_numeric(df["minimum_nights"], errors="coerce")

    if "availability_365" in df.columns:
        df["availability_365"] = pd.to_numeric(df["availability_365"], errors="coerce")


    df = df.dropna(subset=["price"])



    df["occupancy_365"] = 365 - df["availability_365"]
    df["price_quartile"] = pd.qcut(df["price"], q=4, labels=["Бюджетный", "Ниже среднего", "Выше среднего", "Премиум"])
    bins_stay = [0, 2, 7, 30, 90, 400]
    labels_stay = ["1-2", "3-7", "8-30", "31-90", "90+"]

    df["min_stay_bin"] = pd.cut(df["minimum_nights"], bins=bins_stay, labels=labels_stay, include_lowest=True)
    bins_avail = [0, 30, 90, 180, 365]

    labels_avail = ["0-30", "31-90", "91-180", "181-365"]
    df["availability_bin"] = pd.cut(df["availability_365"], bins=bins_avail, labels=labels_avail, include_lowest=True)
    bins_occ = [0, 90, 180, 270, 365]
    
    labels_occ = ["0-90", "91-180", "181-270", "271-365"]
    df["occupancy_bin"] = pd.cut(df["occupancy_365"], bins=bins_occ, labels=labels_occ, include_lowest=True)
    

    if "last_review" in df.columns:
        df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
        df.attrs["data_date"] = df["last_review"].max()
    else:
        df.attrs["data_date"] = datetime.now()
    
    return df


def get_last_update_date():
    """Возвращает дату последнего обновления из файла или None."""
    path = Path("CleanData/last_update.txt")
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return None