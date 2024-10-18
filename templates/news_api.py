import streamlit as st

# Ensure this is the very first Streamlit command
st.set_page_config(page_title="Home Page", layout="wide")

import pandas as pd
import requests
from streamlit_folium import st_folium
import folium

# Google Sheets API URL
api_url = 'https://script.google.com/macros/s/AKfycbwBC4nQXIlrDUoSYI1lbZ6qWPdRyGDkjy0FAPsNl9wGn_msOwVV1M2z4abJr__0F7ee1w/exec'

# Cache the API response for news data to avoid re-fetching each time
@st.cache_data
def fetch_news_data():
    response = requests.get(api_url)
    if response.status_code == 200:
        news_data = response.json()
        return pd.DataFrame(news_data)
    else:
        st.error("Failed to load data from API.")
        return pd.DataFrame()

news_df = fetch_news_data()

# Automatically get city locations from news_df
def get_city_locations(df):
    if 'City' in df.columns and 'Latitude' in df.columns and 'Longitude' in df.columns:
        df = df[df['Latitude'].apply(lambda x: str(x).replace('.', '', 1).isdigit())]
        df = df[df['Longitude'].apply(lambda x: str(x).replace('.', '', 1).isdigit())]
        return df[['City', 'Latitude', 'Longitude']].drop_duplicates().set_index('City').T.to_dict('list')
    else:
        st.error("City location data not available in the dataset.")
        return {}

city_locations = get_city_locations(news_df)

@st.cache_data
def load_geojson_data():
    geojson_url = 'https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson'
    response = requests.get(geojson_url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to load GeoJSON data.")
        return {}

def filter_news_by_city(news, city_name):
    filtered_news = news[news['City'].str.lower() == city_name.lower()]
    if filtered_news.empty:
        st.write(f"{city_name} ke liye koi news nahi mili.")
    else:
        for index, row in filtered_news.iterrows():
            category = row['Category'] if 'Category' in row else 'N/A'
            tags_display = row['Tags'] if 'Tags' in row else ''
            st.markdown(
                f"""
                <div class="art-card-box" style="border: 1px solid #ddd; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                    <div style="width: 100%; margin-bottom: 10px;">
                        <a href="{row['URL']}" target="_blank" class="heading-link">
                            <h3 class="main-heading-txt" style="margin: 0; color: #007BFF;">{row['Heading']}</h3>
                        </a>
                    </div>
                    <div style="display: flex;">
                        <div class="future-img" style="flex: 1; margin-right: 15px;">
                            <a href="{row['URL']}" target="_blank" class="image-link">
                                <img src="{row['Image']}" alt="News Image" style="width: 100%; height: auto; border-radius: 8px;">
                            </a>
                        </div>
                        <div style="flex: 2;">
                            <p class="category-trt">{category}</p>
                            <p class="author_ad_date">By <strong>{row['Author']}</strong> | {row['Date Of Publish']}</p>
                            <a class="more-btn" href="{row['URL']}" target="_blank" >Read More</a>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

def create_map_with_hover(city_locations):
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
    for city, coords in city_locations.items():
        if all(isinstance(coord, (int, float)) for coord in coords):
            folium.Marker(
                location=coords,
                popup=city,
                tooltip=f"Click for news from {city}",
                icon=folium.Icon(color='blue')
            ).add_to(m)

    geojson_data = load_geojson_data()
    if geojson_data:
        folium.GeoJson(
            geojson_data,
            name='geojson',
            style_function=lambda x: {'fillColor': 'gray', 'color': 'black', 'weight': 1, 'fillOpacity': 0.1},
            highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.5, 'color': 'blue'},
            tooltip=folium.GeoJsonTooltip(fields=['NAME_1'], aliases=['State: '])
        ).add_to(m)

    return m

def news_api_page():
    st.title("Misinformation Map")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Fake news data on a map and list it by city:")
        m = create_map_with_hover(city_locations)
        map_output = st_folium(m, width=700, height=500)
        city_name = ""
        if map_output and 'last_object_clicked_popup' in map_output:
            city_name = map_output['last_object_clicked_popup']
    with col2:
        st.subheader("Selected City News:")
        if city_name:
            st.write(f"**Selected City: {city_name}**")
            filter_news_by_city(news_df, city_name)
        else:
            st.write("Please click on a city on the map or use the search to find the news.")

if __name__ == '__main__':
    news_api_page()
