import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load the data
df_2 = pd.read_csv('dataset/5min_crafts_channel.csv')

# Convert duration from seconds to minutes
df_2['duration_minutes'] = df_2['duration'] / 60

# Set up the Streamlit layout
st.title('5 Minutes crafts Channel Analytics Dashboard')

# Sidebar for selecting metric
metric = st.sidebar.selectbox(
    'Select Metric to Display',
    ['Views per Video', 'Likes vs. Views', 'Length vs. Views', 'Views by Day of Week', 'Likes by Day of Week']
)

# Define a light color palette
light_palette = ['#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFDFBA']

# Function to format y-axis labels
def format_func(value, tick_number):
    return f'{value/1e6:.1f}M' if value >= 1e6 else f'{value/1e3:.0f}K'

# Define plot functions
def plot_views_per_video(df):
    top_n = st.slider('Select number of top videos to display', min_value=5, max_value=20, value=10, step=5)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='title', y='viewCount', data=df.sort_values('viewCount', ascending=False).head(top_n), ax=ax, palette=light_palette)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.set_title(f'Top {top_n} Videos by Views')
    ax.set_xlabel('Video Title')
    ax.set_ylabel('Views')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))
    plt.tight_layout()
    st.pyplot(fig)

def plot_likes_vs_views(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='viewCount', y='likeCount', data=df, ax=ax, color=light_palette[0])
    ax.set_title('Likes vs. Views')
    ax.set_xlabel('Views')
    ax.set_ylabel('Likes')
    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_func))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))
    st.pyplot(fig)

def plot_length_vs_views(df):
    # Filter for videos less than 100 minutes
    df_filtered = df[df['duration_minutes'] < 100]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='duration_minutes', y='viewCount', data=df_filtered, ax=ax, color=light_palette[1])
    ax.set_title('Video Length vs. Views (Videos under 100 minutes)')
    ax.set_xlabel('Duration (minutes)')
    ax.set_ylabel('Views')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))
    ax.set_xlim(0, 100)  # Set x-axis limit to 100 minutes
    st.pyplot(fig)

def plot_views_by_day_of_week(df):
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)
    
    avg_views = df.groupby('day_of_week')['viewCount'].mean().reindex(day_order)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=day_order, y=avg_views, ax=ax, palette=light_palette)
    ax.set_title('Average Views by Day of Video Publication')
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Average Views')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))
    st.pyplot(fig)

def plot_likes_by_day_of_week(df):
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)
    
    avg_likes = df.groupby('day_of_week')['likeCount'].mean().reindex(day_order)

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=day_order, y=avg_likes, ax=ax, palette=light_palette)
    ax.set_title('Average Likes by Day of Video Publication')
    ax.set_xlabel('Day of Week')
    ax.set_ylabel('Average Likes')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_func))
    st.pyplot(fig)

# Render the selected metric
if metric == 'Views per Video':
    plot_views_per_video(df_2)
elif metric == 'Likes vs. Views':
    plot_likes_vs_views(df_2)
elif metric == 'Length vs. Views':
    plot_length_vs_views(df_2)
elif metric == 'Views by Day of Week':
    plot_views_by_day_of_week(df_2)
elif metric == 'Likes by Day of Week':
    plot_likes_by_day_of_week(df_2)