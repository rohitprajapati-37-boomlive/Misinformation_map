# templates/pandas_page.py
import streamlit as st
import pandas as pd
import plotly.express as px


def pandas_page():
    st.title("State Election Results in India")

    # Link to the Google Sheets CSV
    sheet_url = "https://docs.google.com/spreadsheets/d/18Z0HOYlHqjOAHOV55JaUiHiidDvNPqkbMlqDuFBEGWQ/export?format=csv"

    # Read data from Google Sheets
    df = pd.read_csv(sheet_url)

    # Display the data frame
    st.dataframe(df)

    # Bar chart for state results
    fig_bar = px.bar(df, x='State', y='Votes', color='Candidate',
                     barmode='group', title="Votes per State")
    st.plotly_chart(fig_bar)

    # Pie chart for vote share by state
    fig_pie = px.pie(df, names='State', values='Votes',
                     title="Vote Share by State")
    st.plotly_chart(fig_pie)

    # Map visualization by Indian states using the correct GeoJSON
    if 'State' in df.columns:
        geojson_url = "https://raw.githubusercontent.com/datameet/maps/master/State-Maps/india_states.geojson"
        fig_map = px.choropleth(
            df,
            geojson=geojson_url,
            locations='State',
            featureidkey="properties.ST_NM",  # Ensure this matches the property in the GeoJSON
            color='Votes',
            title="State-wise Election Results in India"
        )
        fig_map.update_geos(fitbounds="locations",
                            visible=False, projection=dict(type="mercator"))
        st.plotly_chart(fig_map)
