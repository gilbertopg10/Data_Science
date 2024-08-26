import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Page configuration
st.set_page_config(page_title="Job Data Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('final_job_data.csv')

df = load_data()

# Function to get coordinates (cached for performance)
@st.cache_data
def get_coordinates(location):
    geolocator = Nominatim(user_agent="job_locator")
    try:
        return geolocator.geocode(location)
    except Exception as e:
        st.error(f"Error getting coordinates for {location}: {e}")
        return None

# Get coordinates for each job location
df['Coordinates'] = df['City'].apply(lambda city: get_coordinates(city) if pd.notna(city) else None)
df['Latitude'] = df['Coordinates'].apply(lambda x: x.latitude if x else None)
df['Longitude'] = df['Coordinates'].apply(lambda x: x.longitude if x else None)

# Drop rows with invalid coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

# Main title
st.title("Job Data Dashboard")

# Sidebar for view selection
st.sidebar.title("Visualization Options")
selected_view = st.sidebar.radio(
    "Select a view:",
    ["Location Map", "Salary Distribution", "Salary Distribution by Profile", "Job Search"]
)

# Display selected view
if selected_view == "Location Map":
    st.subheader("Job Locations Map")
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=4)
    marker_cluster = MarkerCluster().add_to(m)

    for i, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>{row['Company']}</b><br>{row['Job Title']}<br>${row['Salary']:,.2f}",
            tooltip=row['Company']
        ).add_to(marker_cluster)

    folium_static(m, width=800, height=600)

elif selected_view == "Salary Distribution":
    st.subheader("Salary Distribution")
    fig = px.histogram(df, x="Salary", nbins=10, marginal="box")
    st.plotly_chart(fig, use_container_width=True)

    # Salary statistics
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Salary", f"${df['Salary'].mean():,.2f}")
    col2.metric("Highest Salary", f"${df['Salary'].max():,.2f}")
    col3.metric("Lowest Salary", f"${df['Salary'].min():,.2f}")

elif selected_view == "Salary Distribution by Profile":
    st.subheader("Salary Distribution by Profile")
    fig = px.box(df, x="Job Profile", y="Salary", color="Job Profile")
    st.plotly_chart(fig, use_container_width=True)

    # Statistics by profile
    for profile in df['Job Profile'].unique():
        st.subheader(f"Statistics for {profile}")
        df_profile = df[df['Job Profile'] == profile]
        col1, col2, col3 = st.columns(3)
        col1.metric("Average Salary", f"${df_profile['Salary'].mean():,.2f}")
        col2.metric("Highest Salary", f"${df_profile['Salary'].max():,.2f}")
        col3.metric("Lowest Salary", f"${df_profile['Salary'].min():,.2f}")

else:  # Job Search
    st.subheader("Job Search")
    search_query = st.text_input("Search by job title or company:")
    
    if search_query:
        df_filtered = df[df["Job Title"].str.contains(search_query, case=False) | df["Company"].str.contains(search_query, case=False)]
        if not df_filtered.empty:
            st.dataframe(df_filtered[["Job Title", "Company", "City", "State", "Salary", "Job Profile"]])
        else:
            st.write("No results found for the search.")
    else:
        st.write("Enter a search term to see results.")

# General statistics
st.sidebar.subheader("Labor Market Statistics")
st.sidebar.metric("Average Salary", f"${df['Salary'].mean():,.2f}")
st.sidebar.metric("Highest Salary", f"${df['Salary'].max():,.2f}")
st.sidebar.metric("Number of Jobs", len(df))


