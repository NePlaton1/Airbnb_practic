import json
import re
from pathlib import Path
from typing import Literal

import pandas as pd
import plotly.express as px
import streamlit as st


@st.cache_data(show_spinner=False)
def load_neighbourhood_geojson(geojson_path: str | Path = "Data/neighbourhoods.geojson") -> dict:
    path = Path(geojson_path)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _normalize_name(value: object) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def build_neighbourhood_map(
    df: pd.DataFrame,
    geojson_path: str | Path = "Data/neighbourhoods.geojson",
    value_col: str = "price",
    agg: Literal["median", "mean", "count"] = "median",
):
    if "neighbourhood_cleansed" not in df.columns:
        raise ValueError("В датафрейме нет колонки neighbourhood_cleansed")
    if value_col not in df.columns:
        raise ValueError(f"В датафрейме нет колонки {value_col}")

    geojson = load_neighbourhood_geojson(geojson_path)
    features = geojson.get("features", [])
    if not features:
        raise ValueError("GeoJSON не содержит features")

    geo_lookup = {}
    for feature in features:
        props = feature.get("properties", {})
        name = props.get("neighbourhood")
        if name:
            geo_lookup[_normalize_name(name)] = name

    base = df[["neighbourhood_cleansed", value_col]].copy()
    base = base.dropna(subset=["neighbourhood_cleansed", value_col])
    base["neighbourhood_cleansed"] = base["neighbourhood_cleansed"].astype(str)

    if agg == "median":
        stats = base.groupby("neighbourhood_cleansed", dropna=False)[value_col].median().reset_index(name="metric")
    elif agg == "mean":
        stats = base.groupby("neighbourhood_cleansed", dropna=False)[value_col].mean().reset_index(name="metric")
    elif agg == "count":
        stats = base.groupby("neighbourhood_cleansed", dropna=False)[value_col].count().reset_index(name="metric")
    else:
        raise ValueError("agg must be one of: median, mean, count")

    stats["location"] = stats["neighbourhood_cleansed"].map(lambda x: geo_lookup.get(_normalize_name(x)))
    stats = stats.dropna(subset=["location"])

    if stats.empty:
        raise ValueError("Не удалось сопоставить районы из датасета с геоjson")

    title = {
        "median": "Медианная цена по районам",
        "mean": "Средняя цена по районам",
        "count": "Количество объявлений по районам",
    }[agg]
    
    metric_label = {
        "median": "Медианная цена (CAD)",
        "mean": "Средняя цена (CAD)",
        "count": "Количество объявлений",
    }[agg]

    fig = px.choropleth_mapbox(
        stats,
        geojson=geojson,
        locations="location",
        featureidkey="properties.neighbourhood",
        color="metric",
        color_continuous_scale="Viridis",
        hover_name="neighbourhood_cleansed",
        hover_data={"location": False, "metric": ":.0f"},
        mapbox_style="open-street-map",
        zoom=9.8,
        center={"lat": 49.2827, "lon": -123.1207},
        opacity=0.7,
        labels={"metric": metric_label, "neighbourhood_cleansed": "Район"},
    )
    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        title=title,
        title_x=0.5,
    )
    return fig
