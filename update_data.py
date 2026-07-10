import requests
from bs4 import BeautifulSoup
import pandas as pd
import gzip
import shutil
import os
import re
from pathlib import Path
from datetime import datetime, timedelta

CITY_INDEX = "https://data.insideairbnb.com/canada/bc/vancouver/"
DATA_DIR = Path("CleanData")
RAW_FILE = DATA_DIR / "listings_raw.csv"
CLEAN_FILE = DATA_DIR / "listings_clean.csv"

def get_latest_listings_url():
    """Перебирает даты от сегодняшней, пока не найдёт существующий файл."""
    base_url = "https://data.insideairbnb.com/canada/bc/vancouver"
    today = datetime.today()
    # Пробуем 120 дней назад — этого достаточно, чтобы попасть в последний опубликованный срез
    for days_back in range(120):
        date_candidate = today - timedelta(days=days_back)
        date_str = date_candidate.strftime("%Y-%m-%d")
        url = f"{base_url}/{date_str}/data/listings.csv.gz"
        # HEAD-запрос без загрузки тела, чтобы проверить существование
        resp = requests.head(url)
        if resp.status_code == 200:
            return url
    raise Exception("Не удалось найти актуальный датасет за последние 120 дней")


def download_and_extract(url, dest_csv):
    print(f"Скачиваю {url}...")
    response = requests.get(url, stream=True)
    if url.endswith(".gz"):
        gz_path = str(dest_csv) + ".gz"
        with open(gz_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)
        with gzip.open(gz_path, "rb") as f_in:
            with open(dest_csv, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(gz_path)
    else:
        with open(dest_csv, "wb") as f:
            shutil.copyfileobj(response.raw, f)
    print("Файл загружен и распакован.")

def clean_data(df):
    cols = [
        'id', 'name', 'host_id', 'host_name',
        'neighbourhood_cleansed', 'latitude', 'longitude',
        'room_type', 'price', 'minimum_nights',
        'number_of_reviews', 'last_review', 'last_scraped',
        'review_scores_rating', 'review_scores_accuracy',
        'review_scores_cleanliness', 'review_scores_checkin',
        'review_scores_communication', 'review_scores_location',
        'review_scores_value', 'availability_365',
        'property_type', 'accommodates', 'bathrooms_text',
        'bedrooms', 'beds'
    ]
    existing = [c for c in cols if c in df.columns]
    df = df[existing].copy()
    df['price'] = df['price'].replace('[\$,]', '', regex=True).astype(float)
    df = df.dropna(subset=['price'])
    for col in ['review_scores_rating', 'review_scores_accuracy',
                'review_scores_cleanliness', 'review_scores_checkin',
                'review_scores_communication', 'review_scores_location',
                'review_scores_value']:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    for col in ['bedrooms', 'beds', 'accommodates']:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    df['minimum_nights'] = df['minimum_nights'].fillna(df['minimum_nights'].median())
    if 'bathrooms_text' in df.columns:
        df['bathrooms_text'] = df['bathrooms_text'].fillna(df['bathrooms_text'].mode()[0])
    df = df.dropna(subset=['latitude', 'longitude'])
    if 'last_review' in df.columns:
        df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')
    if 'last_scraped' in df.columns:
        df['last_scraped'] = pd.to_datetime(df['last_scraped'], errors='coerce')
    df = df.drop_duplicates(subset='id')
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('[^a-z0-9_]', '', regex=True)
    return df

if __name__ == "__main__":
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    url = get_latest_listings_url()
    # Извлекаем дату среза из URL (формат .../YYYY-MM-DD/data/...)
    # Пример: https://.../2026-05-24/data/listings.csv.gz
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', url)
    scraped_date = date_match.group(1) if date_match else datetime.today().strftime("%Y-%m-%d")
    
    download_and_extract(url, RAW_FILE)
    raw = pd.read_csv(RAW_FILE)
    cleaned = clean_data(raw)
    cleaned.to_csv(CLEAN_FILE, index=False)
    print(f"Готово: {len(cleaned)} объявлений сохранено в {CLEAN_FILE}")


    with open(DATA_DIR / "last_update.txt", "w", encoding="utf-8") as f:
        f.write(scraped_date)
    print(f"Дата среза записана: {scraped_date}")
